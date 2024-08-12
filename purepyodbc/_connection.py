from __future__ import annotations

from ._errors import ProgrammingError
from ._cursor import Cursor
from ._handler import Handler
from ._enums import HandleType, InfoType


class Connection(Handler):
    """Connection objects manage connections to the database.

    Each manages a single ODBC HDBC.
    """

    def cursor(self) -> Cursor:
        cur = Cursor(self._driver_manager, self)
        return cur

    @property
    def searchescape(self) -> str:
        """The escape character to be used with catalog functions."""
        return self._driver_manager.sql_get_info(
            self, InfoType.SQL_SEARCH_PATTERN_ESCAPE
        )

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_DBC

    def commit(self) -> None:
        # TODO: Implement Connection.commit()
        raise NotImplementedError

    def rollback(self) -> None:
        # TODO: Implement Connection.rollback()
        raise NotImplementedError

    def close(self) -> None:
        self._driver_manager.sql_disconnect(self)
        super().close()

    def setencoding(self, *args, **kwargs):
        raise NotImplementedError

    def setdecoding(
        self, sqltype: int, encoding: str | None = None, ctype: int | None = None
    ) -> None:
        raise NotImplementedError


def connection_check(cnxn: Connection) -> bool:
    return isinstance(cnxn, Connection)


def connection_validate(cnxn: Connection) -> Connection:
    if not cnxn or not connection_check(cnxn):
        raise TypeError("Connection object required")

    if not cnxn.handle.value:
        raise ProgrammingError("Attempt to use a closed connection.")

    return cnxn
