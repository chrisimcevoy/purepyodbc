from __future__ import annotations

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
)
from dataclasses import dataclass
from pathlib import Path
from subprocess import getstatusoutput  # nosec
from typing import Union, TYPE_CHECKING, Tuple


from ._cursor import Cursor

if TYPE_CHECKING:
    from ._environment import Environment
    from ._connection import Connection
from ._errors import ProgrammingError
from ._handler import Handler
from ._enums import (
    ReturnCode,
    HandleType,
    OdbcVersion,
    EnvironmentAttributeType,
    DriverCompletion,
    SqlFetchType,
    DataType,
)
from ._typedef import SQLSMALLINT, SQLLEN, SQLULEN


def find_library() -> Path:
    paths = (
        Path("/usr/lib64"),
        Path("/usr/lib"),
        Path("/usr/lib/i386-linux-gnu"),
        Path("/usr/lib/x86_64-linux-gnu"),
        Path("/usr/lib/libiodbc.dylib"),
    )
    for path in paths:
        libs = sorted(path.glob("libodbc.so*"))
        if libs:
            return libs[-1]
    raise FileNotFoundError


__lib: CDLL = cdll.LoadLibrary(str(find_library()))


def get_sqlwchar_size() -> int:
    """unixODBC defaults to 2-bytes SQLWCHAR, unless "-DSQL_WCHART_CONVERT" was
    added to CFLAGS, in which case it will be the size of wchar_t.
    Note that using 4-bytes SQLWCHAR will break most ODBC drivers, as driver
    development mostly targets the Windows platform.
    """
    status, output = getstatusoutput("odbc_config --cflags")
    if status == 0 and "SQL_WCHART_CONVERT" in output:
        return sizeof(c_wchar)
    return sizeof(c_ushort)


def get_unicode_size() -> int:
    """Determine the size of Py_UNICODE
    sys.maxunicode > 65536 and 'UCS4' or 'UCS2'
    """
    return sys.maxunicode > 65536 and 4 or 2


SQLWCHAR_SIZE = get_sqlwchar_size()
UNICODE_SIZE = get_unicode_size()


wchar_pointer = c_wchar_p
create_buffer = create_string_buffer
odbc_encoding = "utf_16_le"
odbc_decoding = "utf_16"
ucs_length = 2


def UTF16_BE_dec(buffer):
    i = 0
    uchars = []
    while True:
        # TODO: verify that this condition correctly identifies
        # a surrogate pair in UTF-16 BE
        if ord(buffer.raw[i + 1]) & 0xD0 == 0xD0:
            n = 2
        else:
            n = 1
        uchar = buffer.raw[i : i + n * ucs_length].decode(odbc_decoding)
        if uchar == str("\x00"):
            break
        uchars.append(uchar)
        i += n * ucs_length
    return "".join(uchars)


def UCS_dec(buffer):
    i = 0
    uchars = []
    while True:
        uchar = buffer.raw[i : i + ucs_length].decode(odbc_decoding)
        if uchar == str("\x00"):
            break
        uchars.append(uchar)
        i += ucs_length
    return "".join(uchars)


# This is the common case on Linux, which uses wide Python build together with
# the default unixODBC without the "-DSQL_WCHART_CONVERT" CFLAGS.
if sys.platform not in ("win32", "cli", "cygwin"):
    if UNICODE_SIZE >= SQLWCHAR_SIZE:
        # We can only use unicode buffer if the size of wchar_t (UNICODE_SIZE) is
        # the same as the size expected by the driver manager (SQLWCHAR_SIZE).
        create_buffer_u = create_buffer
        wchar_pointer = c_char_p

        def UCS_buf(s):
            return s.encode(odbc_encoding)

        if odbc_encoding == "utf_16":
            from_buffer_u = UTF16_BE_dec
        else:
            from_buffer_u = UCS_dec

    # Esoteric case, don't really care.
    # elif UNICODE_SIZE < SQLWCHAR_SIZE:
    #     raise OdbcLibraryError(
    #         "Using narrow Python build with ODBC library expecting wide unicode is not supported."
    #     )


def _handle_error(handler) -> None:
    ansi = True
    if ansi:
        state = create_buffer(22)
        message = create_buffer(1024 * 4)
        f = __lib.SQLGetDiagRec
        # raw_s = lambda s: bytes(s, "ascii")
    else:
        state = create_buffer_u(24)
        message = create_buffer_u(1024 * 4)
        f = __lib.SQLGetDiagRecW
        # raw_s = str
    native_error = c_int()
    buffer_len = c_short()
    err_list = []

    while True:
        err_number = len(err_list) + 1
        return_code = ReturnCode(
            f(
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
            if ansi:
                err_list.append((state.value, message.value, native_error.value))
            else:
                err_list.append(
                    (from_buffer_u(state), from_buffer_u(message), native_error.value)
                )
        elif return_code is ReturnCode.SQL_INVALID_HANDLE:
            raise ProgrammingError("", return_code.name)
        elif return_code == ReturnCode.SQL_NO_DATA:
            raise Exception(f"{state.value.decode()}{message.value.decode()}")
        else:
            raise Exception(f"Unhandled return code: {return_code}")


def check_success(return_code: Union[int, ReturnCode], handler: Handler) -> None:
    if isinstance(return_code, int):
        return_code = ReturnCode(return_code)

    success_codes = (
        ReturnCode.SQL_SUCCESS,
        ReturnCode.SQL_SUCCESS_WITH_INFO,
        ReturnCode.SQL_NO_DATA,
    )

    if return_code not in success_codes:
        _handle_error(handler)


ReturnCodeAndHandler = Tuple[int, Handler]


def allocate_environment(environment: Environment) -> None:
    return_code = __lib.SQLAllocHandle(
        HandleType.SQL_HANDLE_ENV.value,
        HandleType.SQL_NULL_HANDLE.value,
        byref(environment.handle),
    )
    check_success(return_code, environment)


def set_environment_odbc_version(
    environment: Environment, odbc_version: OdbcVersion
) -> None:
    attribute = EnvironmentAttributeType.SQL_ATTR_ODBC_VERSION
    return_code = __lib.SQLSetEnvAttr(
        environment.handle, attribute.value, odbc_version.value
    )
    check_success(return_code, environment)


def allocate_connection(environment: Environment, connection: Connection) -> None:
    return_code = __lib.SQLAllocHandle(
        HandleType.SQL_HANDLE_DBC.value, environment.handle, byref(connection.handle)
    )
    check_success(return_code, connection)


def allocate_statement(cursor: Cursor) -> None:
    return_code = __lib.SQLAllocHandle(
        HandleType.SQL_HANDLE_STMT.value, cursor.connection.handle, byref(cursor.handle)
    )
    check_success(return_code, cursor)


def sql_free_handle(handler: Handler) -> None:
    return_code = __lib.SQLFreeHandle(handler.handle_type.value, handler.handle)
    check_success(return_code, handler)


def sql_driver_connect(connection: Connection, connection_string: str) -> None:
    ansi = False
    if not ansi:
        c_connectString = wchar_pointer(UCS_buf(connection_string))
        f = __lib.SQLDriverConnectW
    else:
        c_connectString = c_char_p(connection_string)
        f = __lib.SQLDriverConnect

    return_code = f(
        connection.handle,
        0,
        c_connectString,
        len(connection_string),
        None,
        0,
        None,
        DriverCompletion.SQL_DRIVER_NOPROMPT.value,
    )
    check_success(return_code, connection)


def sql_disconnect(connection: Connection) -> None:
    check_success(__lib.SQLDisconnect(connection.handle), connection)


def sql_exec_direct(cursor: Cursor, query_string: str) -> None:
    c_query_string = wchar_pointer(UCS_buf(query_string))
    return_code = __lib.SQLExecDirectW(cursor.handle, c_query_string, len(query_string))
    check_success(return_code, cursor)


def sql_row_count(cursor: Cursor) -> int:
    rowcount: SQLLEN = SQLLEN(-1)
    return_code = __lib.SQLRowCount(cursor.handle, byref(rowcount))
    check_success(return_code, cursor)
    return rowcount.value


def sql_num_result_cols(cursor: Cursor) -> int:
    num_cols = SQLSMALLINT(-1)
    check_success(__lib.SQLNumResultCols(cursor.handle, byref(num_cols)), cursor)
    return num_cols.value


@dataclass(frozen=True)
class ColumnDescription:
    name: str
    data_type: DataType  # TODO: data type enum
    size: int
    decimal_digits: int
    is_nullable: bool


def sql_describe_col(cursor: Cursor, column_number: int) -> ColumnDescription:
    buffer_length = 1024
    column_name = create_string_buffer(buffer_length)
    name_length = SQLSMALLINT()
    data_type = SQLSMALLINT()
    column_size = SQLULEN()
    decimal_digits = SQLSMALLINT()
    nullable = SQLSMALLINT()

    return_code = __lib.SQLDescribeCol(
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

    check_success(return_code, cursor)

    column_description = ColumnDescription(
        column_name.value.decode(),
        DataType(data_type.value),
        column_size.value,
        decimal_digits.value,
        bool(nullable.value),
    )

    return column_description


def sql_fetch(cursor: Cursor) -> bool:
    return_code = ReturnCode(__lib.SQLFetch(cursor.handle))
    check_success(return_code, cursor)
    return return_code is not ReturnCode.SQL_NO_DATA


def sql_get_data(
    cursor: Cursor, column_number: int, column_description: ColumnDescription
):
    buffer_size = 4096
    buffer = create_string_buffer(buffer_size)
    foo = SQLLEN()
    return_code = __lib.SQLGetData(
        cursor.handle, column_number, 1, byref(buffer), buffer_size, byref(foo)
    )
    check_success(return_code, cursor)
    # TODO: check return code for SQL_SUCCESS_WITH_INFO (partial data in buffer)
    return buffer.value.decode()


def sql_drivers(
    environment: Environment, ansi: bool = False, include_attributes: bool = False
) -> list[str]:
    buffer_size = 1000
    direction = SqlFetchType.SQL_FETCH_FIRST
    driver_description = create_buffer(buffer_size)
    buffer_length1 = c_short(buffer_size)
    description_length = c_short()
    driver_attributes = create_buffer(buffer_size)
    buffer_length2 = c_short(buffer_size)
    attributes_length = c_short()
    drivers = []
    func = __lib.SQLDrivers if ansi else __lib.SQLDriversW
    while True:
        return_code = func(
            environment.handle,
            direction.value,
            driver_description,
            buffer_length1,
            byref(description_length),
            driver_attributes,
            buffer_length2,
            byref(attributes_length),
        )
        check_success(return_code, environment)
        if ReturnCode(return_code) is ReturnCode.SQL_NO_DATA:
            break

        def decode(buffer) -> str:
            if ansi:
                return buffer.value.decode()
            return UCS_dec(buffer)

        driver = decode(driver_description)
        if include_attributes:
            driver += f" ({decode(driver_attributes)})"
        drivers.append(driver)
        direction = SqlFetchType.SQL_FETCH_NEXT
    return drivers
