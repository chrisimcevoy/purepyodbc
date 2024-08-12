from __future__ import annotations

import ctypes
import datetime
import typing
import sys
from ctypes import (
    cdll,
    CDLL,
    byref,
    c_int,
    c_short,
    c_char_p,
    c_ushort,
    c_wchar_p,
    create_string_buffer,
    sizeof,
    c_wchar,
    create_unicode_buffer,
)
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, TYPE_CHECKING

from . import _constants
import purepyodbc
from ._dto import SqlColumnDescription

if TYPE_CHECKING:
    from ._cursor import Cursor
    from ._environment import Environment
    from ._connection import Connection
    from ._handler import Handler
from ._errors import (
    Error,
    ProgrammingError,
    InterfaceError,
    OperationalError,
    NotSupportedError,
    IntegrityError,
    DataError,
)
from ._enums import (
    ReturnCode,
    HandleType,
    InfoType,
    OdbcVersion,
    EnvironmentAttributeType,
    DriverCompletion,
    SqlFetchType,
    SqlDataType,
    LengthOrIndicatorType,
)
from ._typedef import SQLSMALLINT, SQLLEN, SQLULEN


DEFAULT_ODBC_ENCODING = "utf-16-le" if sys.byteorder == "little" else "utf-16-be"


def detect_driver_manager() -> DriverManager:
    import platform

    if platform.system() == "Windows":
        odbc32 = ctypes.windll.odbc32  # type: ignore[attr-defined]
        return DriverManager(cdll=odbc32)
    else:
        paths = (
            Path("/usr/lib64"),
            Path("/usr/lib"),
            Path("/usr/lib/i386-linux-gnu"),
            Path("/usr/lib/x86_64-linux-gnu"),
            Path("/usr/lib/libiodbc.dylib"),
        )
        for path in paths:
            for unixodbc_so in reversed(sorted(path.glob("libodbc.so*"))):
                return DriverManager(cdll=cdll.LoadLibrary(str(unixodbc_so)))
            for iodbc_so in path.glob("libiodbc.so*"):
                return DriverManager(cdll=cdll.LoadLibrary(str(iodbc_so)))
        raise FileNotFoundError("No supported driver manager detected!")


@dataclass
class DriverManager:
    cdll: CDLL
    _sqlwchar_size: int = field(init=False, default=2)
    _odbc_encoding: str = field(init=False, default=DEFAULT_ODBC_ENCODING)

    def __post_init__(self):
        # Needed for 64-bit Windows, otherwise you get ValueErrors on non-zero ReturnCodes
        for func_name in (
            "SQLAllocHandle",
            "SQLBindParameter",
            "SQLBindCol",
            "SQLBrowseConnect",
            "SQLBrowseConnectW",
            "SQLCloseCursor",
            "SQLColAttribute",
            "SQLColAttributeW",
            "SQLColAttributes",
            "SQLColAttributesW",
            "SQLColumns",
            "SQLColumnsW",
            "SQLConnect",
            "SQLConnectW",
            "SQLDataSources",
            "SQLDataSourcesW",
            "SQLDescribeCol",
            "SQLDescribeColW",
            "SQLDescribeParam",
            "SQLDisconnect",
            "SQLDriverConnect",
            "SQLDriverConnectW",
            "SQLDrivers",
            "SQLDriversW",
            "SQLEndTran",
            "SQLExecDirect",
            "SQLExecDirectW",
            "SQLExecute",
            "SQLFetch",
            "SQLFetchScroll",
            "SQLForeignKeys",
            "SQLForeignKeysW",
            "SQLFreeHandle",
            "SQLFreeStmt",
            "SQLGetConnectAttr",
            "SQLGetConnectAttrW",
            "SQLGetConnectOption",
            "SQLGetConnectOptionW",
            "SQLGetCursorName",
            "SQLGetCursorNameW",
            "SQLGetData",
            "SQLGetDescField",
            "SQLGetDescFieldW",
            "SQLGetDescRec",
            "SQLGetDescRecW",
            "SQLGetDiagField",
            "SQLGetDiagFieldW",
            "SQLGetDiagRec",
            "SQLGetDiagRecW",
            "SQLGetInfo",
            "SQLGetInfoW",
            "SQLGetTypeInfo",
            "SQLGetTypeInfoW",
            "SQLMoreResults",
            "SQLNativeSql",
            "SQLNativeSqlW",
            "SQLNumParams",
            "SQLNumResultCols",
            "SQLPrepare",
            "SQLPrepareW",
            "SQLPrimaryKeys",
            "SQLPrimaryKeysW",
            "SQLProcedureColumns",
            "SQLProcedureColumnsW",
            "SQLProcedures",
            "SQLProceduresW",
            "SQLRowCount",
            "SQLSetConnectAttr",
            "SQLSetConnectAttrW",
            "SQLSetConnectOption",
            "SQLSetConnectOptionW",
            "SQLSetCursorName",
            "SQLSetCursorNameW",
            "SQLSetDescField",
            "SQLSetDescFieldW",
            "SQLSetEnvAttr",
            "SQLSetStmtAttr",
            "SQLSetStmtAttrW",
            "SQLSpecialColumns",
            "SQLSpecialColumnsW",
            "SQLStatistics",
            "SQLStatisticsW",
            "SQLTablePrivileges",
            "SQLTablePrivilegesW",
            "SQLTables",
            "SQLTablesW",
        ):
            func = getattr(self.cdll, func_name)
            func.restype = c_short

        # unixODBC defaults to 2-bytes SQLWCHAR, unless "-DSQL_WCHART_CONVERT" was
        # added to CFLAGS, in which case it will be the size of wchar_t.
        # Note that using 4-bytes SQLWCHAR will break most ODBC drivers, as driver
        # development mostly targets the Windows platform.
        from subprocess import getstatusoutput  # nosec

        status, output = getstatusoutput("odbc_config --cflags")
        if status == 0 and "SQL_WCHART_CONVERT" in output.upper():
            sqlwchar_type = c_wchar
        else:
            # TODO: We don't know for sure - should we generate a warning?
            sqlwchar_type = c_ushort
        self._sqlwchar_size = sizeof(sqlwchar_type)

    @property
    def _odbc_bytes_per_char(self) -> int:
        """Return the (max) number of bytes per char for the Driver Manager's encoding."""
        if self._odbc_encoding.startswith("utf-8") or self._odbc_encoding.startswith(
            "utf-32"
        ):
            return 4
        elif self._odbc_encoding.startswith("utf-16"):
            return 2
        raise NotSupportedError(f'"{self._odbc_encoding}" is not supported.')

    def _count_odbc_encoded_bytes(self, s) -> int:
        """Return the number of bytes required in the DriverManager's encoding."""
        return int(len(self._odbc_encode(s)) / self._odbc_bytes_per_char)

    def _to_char_pointer(self, s):
        if isinstance(s, str):
            s = self._odbc_encode(s)
        return c_char_p(s)

    def _to_wchar_pointer(self, s):
        if self._sqlwchar_size == 2:
            return c_char_p(self._odbc_encode(s))
        return c_wchar_p(s)

    def _odbc_encode(self, s):
        return s.encode(self._odbc_encoding)

    def _to_buffer(self, init, size=None):
        if self._sqlwchar_size == 2:
            return create_string_buffer(init, size)
        return create_unicode_buffer(init, size)

    def _from_buffer(self, buffer) -> str:
        if self._sqlwchar_size == 2:
            return buffer.raw.decode(self._odbc_encoding).rstrip("\x00")
        return buffer.value

    def allocate_environment(self, environment: Environment) -> None:
        return_code = self.cdll.SQLAllocHandle(
            HandleType.SQL_HANDLE_ENV.value,
            HandleType.SQL_NULL_HANDLE.value,
            byref(environment.handle),
        )
        self.check_success(return_code, environment)

    def set_environment_odbc_version(
        self, environment: Environment, odbc_version: OdbcVersion
    ) -> None:
        attribute = EnvironmentAttributeType.SQL_ATTR_ODBC_VERSION
        return_code = self.cdll.SQLSetEnvAttr(
            environment.handle, attribute.value, odbc_version.value
        )
        self.check_success(return_code, environment)

    def allocate_connection(
        self, environment: Environment, connection: Connection
    ) -> None:
        return_code = self.cdll.SQLAllocHandle(
            HandleType.SQL_HANDLE_DBC.value,
            environment.handle,
            byref(connection.handle),
        )
        self.check_success(return_code, connection)

    def allocate_statement(self, cursor: Cursor) -> None:
        return_code = self.cdll.SQLAllocHandle(
            HandleType.SQL_HANDLE_STMT.value,
            cursor.connection.handle,
            byref(cursor.handle),
        )
        self.check_success(return_code, cursor)

    def sql_free_handle(self, handler: Handler) -> None:
        return_code = self.cdll.SQLFreeHandle(handler.handle_type.value, handler.handle)
        self.check_success(return_code, handler)

    def sql_driver_connect(
        self, connection: Connection, connection_string: str, ansi: bool
    ) -> None:
        if ansi:
            c_connect_string = self._to_char_pointer(connection_string)
            f = self.cdll.SQLDriverConnect
        else:
            c_connect_string = self._to_wchar_pointer(connection_string)
            f = self.cdll.SQLDriverConnectW

        return_code = f(
            connection.handle,
            0,
            c_connect_string,
            len(connection_string),
            None,
            0,
            None,
            DriverCompletion.SQL_DRIVER_NOPROMPT.value,
        )
        self.check_success(return_code, connection)

    def sql_disconnect(self, connection: Connection) -> None:
        self.check_success(self.cdll.SQLDisconnect(connection.handle), connection)

    def sql_exec_direct(self, cursor: Cursor, query_string: str) -> None:
        c_query_string = self._to_wchar_pointer(query_string)
        length = self._count_odbc_encoded_bytes(query_string)
        return_code = self.cdll.SQLExecDirectW(cursor.handle, c_query_string, length)
        self.check_success(return_code, cursor)

    def sql_row_count(self, cursor: Cursor) -> int:
        rowcount: SQLLEN = SQLLEN(-1)
        return_code = self.cdll.SQLRowCount(cursor.handle, byref(rowcount))
        self.check_success(return_code, cursor)
        return rowcount.value

    def sql_num_result_cols(self, cursor: Cursor) -> int:
        num_cols = SQLSMALLINT(-1)
        self.check_success(
            self.cdll.SQLNumResultCols(cursor.handle, byref(num_cols)), cursor
        )
        return num_cols.value

    def sql_describe_col(
        self,
        cursor: Cursor,
        column_number: int,
        lowercase: typing.Optional[bool] = None,
    ) -> SqlColumnDescription:
        buffer_length = 1024
        column_name = self._to_buffer(buffer_length)
        name_length = SQLSMALLINT()
        data_type = SQLSMALLINT()
        column_size = SQLULEN()
        decimal_digits = SQLSMALLINT()
        nullable = SQLSMALLINT()

        return_code = self.cdll.SQLDescribeColW(
            cursor.handle,
            column_number,
            byref(column_name),
            buffer_length,
            byref(name_length),
            byref(data_type),
            byref(column_size),
            byref(decimal_digits),
            byref(nullable),
        )

        self.check_success(return_code, cursor)

        sql_type = SqlDataType(data_type.value)
        python_type = SQL_DATA_TYPE_MAP[sql_type].python_type

        name = self._from_buffer(column_name)
        if lowercase is True or purepyodbc.lowercase is True:
            name = name.lower()

        column_description = SqlColumnDescription(
            name,
            sql_type,
            python_type,
            column_size.value,
            decimal_digits.value,
            bool(nullable.value),
            column_number,
        )

        return column_description

    def sql_fetch(self, cursor: Cursor) -> bool:
        return_code = ReturnCode(self.cdll.SQLFetch(cursor.handle))
        self.check_success(return_code, cursor)
        return return_code is not ReturnCode.SQL_NO_DATA

    def sql_get_data(
        self, cursor: Cursor, column_description: SqlColumnDescription
    ) -> typing.Any:
        buffer_size = 4096
        buffer = self._to_buffer(buffer_size)
        length_or_indicator = SQLLEN()

        return_code = self.cdll.SQLGetData(
            cursor.handle,
            column_description.column_number,
            -8,  # TODO: Don't hardcode SQL_C_WCHAR for SQLGetData..? Enum?
            byref(buffer),
            buffer_size,
            byref(length_or_indicator),
        )

        self.check_success(return_code, cursor)

        # TODO: check return code for SQL_SUCCESS_WITH_INFO (partial data in buffer)

        try:
            indicator = LengthOrIndicatorType(length_or_indicator.value)
            if indicator is LengthOrIndicatorType.SQL_NULL_DATA:
                return None
        except ValueError:
            pass

        raw_value = self._from_buffer(buffer)

        try:
            handling = SQL_DATA_TYPE_MAP[column_description.data_type]
        except KeyError:
            raise InterfaceError(
                f"No output converter for SQL data type {column_description.data_type.name}"
            )

        value = handling.output_converter(raw_value)
        return value

    def sql_more_results(self, cursor: Cursor) -> bool:
        return_code = ReturnCode(self.cdll.SQLMoreResults(cursor.handle))
        self.check_success(return_code, cursor)
        return return_code != ReturnCode.SQL_NO_DATA

    def sql_get_info(self, connection: Connection, info_type: InfoType) -> typing.Any:
        buffer_size = 4096
        buffer = self._to_buffer(buffer_size)
        string_len = SQLSMALLINT()

        return_code = ReturnCode(
            self.cdll.SQLGetInfoW(
                connection.handle,
                info_type.value,
                buffer,
                buffer_size,
                byref(string_len),
            )
        )

        self.check_success(return_code, connection)

        return self._from_buffer(buffer)

    def sql_drivers(
        self, environment: Environment, include_attributes: bool = False
    ) -> list[str]:
        buffer_size = 1000
        direction = SqlFetchType.SQL_FETCH_FIRST
        description_length = c_short()
        attributes_length = c_short()
        drivers = []
        func = self.cdll.SQLDriversW
        while True:
            driver_description = self._to_buffer(buffer_size)
            driver_attributes = self._to_buffer(buffer_size)
            return_code = func(
                environment.handle,
                direction.value,
                driver_description,
                buffer_size,
                byref(description_length),
                driver_attributes,
                buffer_size,
                byref(attributes_length),
            )
            self.check_success(return_code, environment)
            if ReturnCode(return_code) is ReturnCode.SQL_NO_DATA:
                break

            driver = self._from_buffer(driver_description)
            if include_attributes:
                raw_attrs = self._from_buffer(driver_attributes)
                # TODO: Each key-value driver attribute pair is separated by a null byte.
                #  Should we do something else eg newline or split?
                # attrs = attrs.replace('\x00', '\n')
                # attrs = attrs.replace('\x00', ',')
                attrs = raw_attrs.split("\x00")
                driver += f" {attrs}"
            drivers.append(driver)
            direction = SqlFetchType.SQL_FETCH_NEXT
        return drivers

    def sql_tables(
        self,
        cursor: Cursor,
        catalog: typing.Optional[str],
        schema: typing.Optional[str],
        table: typing.Optional[str],
        table_type: typing.Optional[str],
    ):
        def get_pointer_and_len(v) -> tuple[Union[c_wchar_p, ctypes.c_void_p], int]:
            if v is None:
                return ctypes.c_void_p(), _constants.SQL_NTS
            # Note that pyodbc just passes SQL_NTS for everything
            # Worth bearing in mind if counting the bytes gives problems
            # or if we think we're just wasting cycles here (performance).
            return self._to_wchar_pointer(v), len(v)

        c_catalog, c_catalog_len = get_pointer_and_len(catalog)
        c_schema, c_schema_len = get_pointer_and_len(schema)
        c_table, c_table_len = get_pointer_and_len(table)
        c_table_type, c_table_type_len = get_pointer_and_len(table_type)

        return_code = self.cdll.SQLTablesW(
            cursor.handle,
            c_catalog,
            c_catalog_len,
            c_schema,
            c_schema_len,
            c_table,
            c_table_len,
            c_table_type,
            c_table_type_len,
        )
        self.check_success(return_code, cursor)

    def check_success(
        self, return_code: Union[int, ReturnCode], handler: Handler
    ) -> None:
        if isinstance(return_code, int):
            return_code = ReturnCode(return_code)

        success_codes = (
            ReturnCode.SQL_SUCCESS,
            ReturnCode.SQL_SUCCESS_WITH_INFO,
            ReturnCode.SQL_NO_DATA,
        )

        if return_code not in success_codes:
            self._handle_error(handler)

    def _handle_error(self, handler) -> None:
        state = self._to_buffer(24)
        message = self._to_buffer(1024 * 4)
        native_error = c_int()
        buffer_len = c_short()
        err_list: typing.List[typing.Tuple[str, str, int]] = []

        while True:
            err_number = len(err_list) + 1
            return_code = ReturnCode(
                self.cdll.SQLGetDiagRecW(
                    handler.handle_type.value,
                    handler.handle,
                    err_number,
                    state,
                    byref(native_error),
                    message,
                    1024,
                    byref(buffer_len),
                )
            )
            if return_code is ReturnCode.SQL_SUCCESS:
                err_list.append(
                    (
                        self._from_buffer(state),
                        self._from_buffer(message),
                        native_error.value,
                    )
                )
            elif return_code is ReturnCode.SQL_INVALID_HANDLE:
                raise ProgrammingError("", return_code.name)
            elif return_code == ReturnCode.SQL_NO_DATA:
                first_state = err_list[0][0]
                first_msg = err_list[0][1]
                sql_state_exc_map = {
                    "01002": OperationalError,
                    "08001": OperationalError,
                    "08003": OperationalError,
                    "08004": OperationalError,
                    "08007": OperationalError,
                    "08S01": OperationalError,
                    "0A000": NotSupportedError,
                    "28000": InterfaceError,
                    "40002": IntegrityError,
                    "22": DataError,
                    "23": IntegrityError,
                    "24": ProgrammingError,
                    "25": ProgrammingError,
                    "42": ProgrammingError,
                    "HY001": OperationalError,
                    "HY014": OperationalError,
                    "HYT00": OperationalError,
                    "HYT01": OperationalError,
                    "IM001": InterfaceError,
                    "IM002": InterfaceError,
                    "IM003": InterfaceError,
                }
                for k, v in sql_state_exc_map.items():
                    if first_state.startswith(k):
                        exc_type = v
                        break
                else:
                    exc_type = Error
                raise exc_type(f"{first_state}{first_msg}")
            else:
                raise Error(f"Unhandled return code: {return_code}")

    def sql_procedures(self, cursor: Cursor, procedure, catalog, schema):
        return_code = ReturnCode(
            self.cdll.SQLProcedures(
                cursor.handle,
                procedure,
                _constants.SQL_NTS,
                catalog,
                _constants.SQL_NTS,
                schema,
                _constants.SQL_NTS,
            )
        )
        self.check_success(return_code, cursor)

    def sql_foreign_keys(
        self,
        cursor: Cursor,
        table,
        catalog,
        schema,
        foreignTable,
        foreignCatalog,
        foreignSchema,
    ):
        """https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlforeignkeys-function"""

        def get_pointer_and_len(v) -> tuple[Union[c_wchar_p, ctypes.c_void_p], int]:
            if v is None:
                return ctypes.c_void_p(), _constants.SQL_NTS
            # Note that pyodbc just passes SQL_NTS for everything
            # Worth bearing in mind if counting the bytes gives problems
            # or if we think we're just wasting cycles here (performance).
            return self._to_wchar_pointer(v), len(v)

        catalog, catalog_len = get_pointer_and_len(catalog)
        schema, schema_len = get_pointer_and_len(schema)
        table, table_len = get_pointer_and_len(table)
        foreignCatalog, foreignCatalog_len = get_pointer_and_len(foreignCatalog)
        foreignSchema, foreignSchema_len = get_pointer_and_len(foreignSchema)
        foreignTable, foreignTable_len = get_pointer_and_len(foreignTable)

        return_code = ReturnCode(
            self.cdll.SQLForeignKeysW(
                cursor.handle,
                catalog,
                catalog_len,
                schema,
                schema_len,
                table,
                table_len,
                foreignCatalog,
                foreignCatalog_len,
                foreignSchema,
                foreignSchema_len,
                foreignTable,
                foreignTable_len,
            )
        )
        self.check_success(return_code, cursor)


def parse_sql_bit(value: str) -> bool:
    return bool(int(value))


T = typing.TypeVar("T")


@dataclass(frozen=True)
class SqlDataTypeHandling(typing.Generic[T]):
    python_type: typing.Type[T]
    output_converter: typing.Callable[[str], T]


SQL_DATA_TYPE_MAP: typing.Dict[SqlDataType, SqlDataTypeHandling] = {
    SqlDataType.SQL_CHAR: SqlDataTypeHandling(python_type=str, output_converter=str),
    SqlDataType.SQL_VARCHAR: SqlDataTypeHandling(python_type=str, output_converter=str),
    SqlDataType.SQL_WVARCHAR: SqlDataTypeHandling(
        python_type=str, output_converter=str
    ),
    SqlDataType.SQL_WLONGVARCHAR: SqlDataTypeHandling(
        python_type=str, output_converter=str
    ),
    SqlDataType.SQL_BIT: SqlDataTypeHandling(
        python_type=bool, output_converter=parse_sql_bit
    ),
    SqlDataType.SQL_INTEGER: SqlDataTypeHandling(python_type=int, output_converter=int),
    SqlDataType.SQL_TINYINT: SqlDataTypeHandling(python_type=int, output_converter=int),
    SqlDataType.SQL_TYPE_TIMESTAMP: SqlDataTypeHandling(
        python_type=datetime.datetime, output_converter=datetime.datetime.fromisoformat
    ),
    SqlDataType.SQL_SMALLINT: SqlDataTypeHandling(
        python_type=int, output_converter=int
    ),
}
