from __future__ import annotations

import functools
import typing
from dataclasses import dataclass, field

from ._typedef import SQLLEN
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
    __rowcount: SQLLEN = field(
        init=False, default_factory=functools.partial(SQLLEN, -1)
    )

    def __post_init__(self):
        _odbc.allocate_statement(self)

    @property
    def rowcount(self) -> int:
        return _odbc.sql_row_count(self)

    @property
    def columncount(self) -> int:
        return _odbc.sql_num_result_cols(self)

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_STMT

    def execute(self, query_string: str) -> Cursor:
        _odbc.sql_exec_direct(self, query_string)
        return self

    def fetchone(self) -> typing.Optional[Row]:
        if not _odbc.sql_fetch(self):
            return None
        row = Row()
        for column_number in range(1, self.columncount + 1):
            # TODO: Other packages call SQLColAttribute here to determine whether int() or long()
            #  is required, but that only applies to Python 2... right? RIGHT???!!
            # _odbc.sql_col_attribute(
            #     cursor,
            #     column_number,
            #     SqlColumnAttrType.SQL_COLUMN_DISPLAY_SIZE
            # )

            # Next, the application retrieves the name, data type, precision,
            # and scale of each result set column with SQLDescribeCol.
            description = _odbc.sql_describe_col(self, column_number)
            value = _odbc.sql_get_data(self, column_number, description)
            setattr(row, description.name, value)
        return row
