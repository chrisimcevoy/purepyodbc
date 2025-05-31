from __future__ import annotations

from collections.abc import Sequence

from ._connection import Connection
from ._driver_manager import DriverManager, detect_driver_manager
from ._enums import HandleType, OdbcVersion
from ._handler import Handler


class Environment(Handler):
    def __init__(self, driver_manager: DriverManager | None = None, pooling: bool = False) -> None:
        if driver_manager is None:
            driver_manager = detect_driver_manager()
        super().__init__(driver_manager)
        self._driver_manager.allocate_environment(self)
        self._driver_manager.set_environment_odbc_version(self, OdbcVersion.SQL_OV_ODBC3_80)

    def connection(
        self,
        connection_string: str,
        autocommit: bool = False,
        ansi: bool = False,
        timeout: int = 0,
        readonly: bool = False,
        attrs_before: dict[int, int | bytes | bytearray | str | Sequence[str]] | None = None,
        encoding: str | None = None,
    ) -> Connection:
        connection = Connection(driver_manager=self._driver_manager)
        self._driver_manager.allocate_connection(self, connection)

        # Initialize autocommit mode.
        # The DB API says we have to default to manual-commit, but ODBC defaults to auto-commit.  We also provide a
        # keyword parameter that allows the user to override the DB API and force us to start in auto-commit (in which
        # case we don't have to do anything).
        if not autocommit:
            connection.autocommit = autocommit

        self._driver_manager.sql_driver_connect(connection, connection_string, ansi=ansi)
        return connection

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_ENV
