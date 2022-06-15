from __future__ import annotations

import typing

from ._driver_manager import DriverManager
from ._dto import ColumnDescription, SqlColumnDescription
from ._row import Row
from ._enums import HandleType
from ._handler import Handler

if typing.TYPE_CHECKING:
    from ._connection import Connection


class Cursor(Handler):
    def __init__(self, driver_manager: DriverManager, connection: Connection) -> None:
        super().__init__(driver_manager)
        self.connection = connection
        self.arraysize = 1
        self.__rowcount = -1
        self.__column_descriptions: typing.Tuple[ColumnDescription, ...] = tuple()
        self.__sql_column_descriptions: typing.Tuple[
            SqlColumnDescription, ...
        ] = tuple()
        self._driver_manager.allocate_statement(self)

    @property
    def rowcount(self) -> int:
        return self.__rowcount

    @property
    def description(self) -> typing.Sequence[ColumnDescription]:
        return self.__column_descriptions

    @property
    def columncount(self) -> int:
        return self._driver_manager.sql_num_result_cols(self)

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_STMT

    def __post_execute(self, lowercase: bool = False) -> None:
        """Update rowcount and column descriptions."""
        self.__rowcount = self._driver_manager.sql_row_count(self)
        self.__sql_column_descriptions = tuple(
            self._driver_manager.sql_describe_col(self, i + 1, lowercase)
            for i in range(self.columncount)
        )
        self.__column_descriptions = tuple(
            x.to_column_description() for x in self.__sql_column_descriptions
        )

    def execute(self, query_string: str) -> Cursor:
        self._driver_manager.sql_exec_direct(self, query_string)
        self.__post_execute()
        return self

    def fetchmany(self, size: typing.Optional[int] = None) -> typing.List[Row]:
        """Fetch the next set of rows of a query result.
        https://www.python.org/dev/peps/pep-0249/#fetchmany
        """

        size = self.arraysize if size is None else size
        rows: list[Row] = []

        if size:
            while len(rows) < size:
                row = self.fetchone()
                if not row:
                    break
                rows.append(row)

        return rows

    def fetchall(self) -> typing.List[Row]:
        """Fetch all (remaining) rows in the result set."""
        rows = []

        while True:
            row = self.fetchone()
            if not row:
                break
            rows.append(row)

        return rows

    def fetchone(self) -> typing.Optional[Row]:
        if not self._driver_manager.sql_fetch(self):
            return None
        row = Row()
        for sql_column_description in self.__sql_column_descriptions:
            value = self._driver_manager.sql_get_data(self, sql_column_description)
            setattr(row, sql_column_description.name, value)
        return row

    def nextset(self) -> typing.Optional[bool]:
        if self._driver_manager.sql_more_results(self):
            self.__post_execute()
            return True
        return None

    def tables(
        self,
        table: typing.Optional[str] = None,
        catalog: typing.Optional[str] = None,
        schema: typing.Optional[str] = None,
        table_type: typing.Optional[str] = None,
    ) -> Cursor:
        self._driver_manager.sql_tables(self, catalog, schema, table, table_type)
        self.__post_execute(lowercase=True)
        return self

    def procedures(
        self,
        procedure: typing.Optional[str] = None,
        catalog: typing.Optional[str] = None,
        schema: typing.Optional[str] = None,
    ) -> Cursor:
        self._driver_manager.sql_procedures(self, procedure, catalog, schema)
        self.__post_execute(lowercase=True)
        return self

    def foreignKeys(
        self,
        table: typing.Optional[str] = None,
        catalog: typing.Optional[str] = None,
        schema: typing.Optional[str] = None,
        foreignTable: typing.Optional[str] = None,
        foreignCatalog: typing.Optional[str] = None,
        foreignSchema: typing.Optional[str] = None,
    ) -> Cursor:
        self._driver_manager.sql_foreign_keys(
            self, table, catalog, schema, foreignTable, foreignCatalog, foreignSchema
        )
        self.__post_execute(lowercase=True)
        return self
