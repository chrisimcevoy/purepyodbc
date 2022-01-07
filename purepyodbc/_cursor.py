from __future__ import annotations

import typing
from dataclasses import dataclass, field

from ._dto import ColumnDescription, SqlColumnDescription
from ._row import Row
from . import _odbc
from ._enums import HandleType
from ._handler import Handler
from ._typedef import SQLHSTMT

if typing.TYPE_CHECKING:
    from ._connection import Connection


@dataclass
class Cursor(Handler[SQLHSTMT]):
    connection: Connection
    arraysize: int = 1
    __rowcount: int = -1
    __column_descriptions: typing.Tuple[ColumnDescription] = field(
        default_factory=tuple
    )
    __sql_column_descriptions: typing.Tuple[SqlColumnDescription] = field(
        default_factory=list
    )

    def __post_init__(self):
        _odbc.allocate_statement(self)

    @property
    def rowcount(self) -> int:
        return self.__rowcount

    @property
    def description(self) -> typing.Sequence[ColumnDescription]:
        return self.__column_descriptions

    @property
    def columncount(self) -> int:
        return _odbc.sql_num_result_cols(self)

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_STMT

    def execute(self, query_string: str) -> Cursor:
        _odbc.sql_exec_direct(self, query_string)
        self.__update_rowcount()
        self.__update_sql_column_descriptions()
        self.__update_column_descriptions()
        return self

    def __update_rowcount(self) -> None:
        self.__rowcount = _odbc.sql_row_count(self)

    def __update_sql_column_descriptions(self) -> None:
        self.__sql_column_descriptions = tuple(
            _odbc.sql_describe_col(self, i + 1) for i in range(self.columncount)
        )

    def __update_column_descriptions(self) -> None:
        self.__column_descriptions = tuple(
            x.to_column_description() for x in self.__sql_column_descriptions
        )

    def fetchmany(self, size: typing.Optional[int] = None) -> typing.List[Row]:
        """Fetch the next set of rows of a query result.
        https://www.python.org/dev/peps/pep-0249/#fetchmany
        """

        size = self.arraysize if size is None else size
        rows = []

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
        if not _odbc.sql_fetch(self):
            return None
        row = Row()
        for sql_column_description in self.__sql_column_descriptions:
            value = _odbc.sql_get_data(self, sql_column_description)
            setattr(row, sql_column_description.name, value)
        return row

    def nextset(self) -> typing.Optional[bool]:
        if _odbc.sql_more_results(self):
            self.__update_rowcount()
            self.__update_sql_column_descriptions()
            self.__update_column_descriptions()
            return True
