from __future__ import annotations

from dataclasses import dataclass

from . import _odbc
from ._enums import HandleType, OdbcVersion
from ._handler import Handler
from ._connection import Connection
from ._typedef import SQLHENV


@dataclass
class Environment(Handler[SQLHENV]):
    pooling: bool

    def __post_init__(self):
        _odbc.allocate_environment(self)
        _odbc.set_environment_odbc_version(self, OdbcVersion.SQL_OV_ODBC3_80)

    def connection(
        self,
        connection_string: str,
        autocommit: bool = False,
        ansi: bool = False,
        timeout: int = 0,
        readonly: bool = False,
        attrs_before: dict = None,
        encoding: str = None,
    ) -> Connection:
        connection = Connection()
        _odbc.allocate_connection(self, connection)
        _odbc.sql_driver_connect(connection, connection_string)
        return connection

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_ENV
