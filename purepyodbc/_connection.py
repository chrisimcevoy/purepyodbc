from __future__ import annotations

from ._errors import ProgrammingError
from ._cursor import Cursor
from ._handler import Handler
from ._enums import (
    HandleType,
    InfoType,
    ConnectionAttributeType,
    ConnectionAutocommitMode,
    CompletionType,
)


class Connection(Handler):
    """The ODBC connection class representing an ODBC connection to a database, for
    managing database transactions and creating cursors.
    https://www.python.org/dev/peps/pep-0249/#connection-objects

    This class should not be instantiated directly, instead call purepyodbc.connect() to
    create a Connection object.
    """

    @property
    def autocommit(self) -> bool:
        """Whether the database automatically executes a commit after every successful transaction.

        Default is False.
        """
        # TODO: According to pep-0249 this is deprecated.
        #  https://peps.python.org/pep-0249/#optional-db-api-extensions
        ret: int = self._driver_manager.sql_get_connect_attr(
            connection=self, attr=ConnectionAttributeType.SQL_ATTR_AUTOCOMMIT
        )
        return (
            ConnectionAutocommitMode(ret) == ConnectionAutocommitMode.SQL_AUTOCOMMIT_ON
        )

    @autocommit.setter
    def autocommit(self, enabled: bool) -> None:
        self._driver_manager.sql_set_connect_attr(
            connection=self,
            attr=ConnectionAttributeType.SQL_ATTR_AUTOCOMMIT,
            value=ConnectionAutocommitMode(int(enabled)).value,
        )

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
        self._driver_manager.sql_end_tran(self, CompletionType.SQL_COMMIT)

    def rollback(self) -> None:
        self._driver_manager.sql_end_tran(self, CompletionType.SQL_ROLLBACK)

    def close(self) -> None:
        if not self.autocommit:
            self.rollback()
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
