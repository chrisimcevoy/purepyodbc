from typing import List, Dict, Any

from ._connection import Connection
from ._environment import Environment as _Environment
from . import _odbc


apilevel: str = "2.0"
lowercase: bool = False
native_uuid: bool = False
paramstyle: str = "qmark"
pooling: bool = True
threadsafety: int = 1  # TODO: Check threadsafety
version = "0.0.1.dev0"

__environment: _Environment

SQL_CHAR = 1
SQL_WCHAR = -8


def connect(
    connection_string: str,
    autocommit: bool = False,
    ansi: bool = False,
    timeout: int = 0,
    readonly: bool = False,
    attrs_before: Dict[str, Any] = None,
    encoding: str = None,
) -> Connection:

    __ensure_environment_created()

    connection = __environment.connection(
        connection_string, autocommit, ansi, timeout, readonly, attrs_before, encoding
    )

    return connection


def drivers(ansi: bool = False, include_attributes: bool = False) -> List[str]:
    __ensure_environment_created()
    return _odbc.sql_drivers(
        __environment, ansi=ansi, include_attributes=include_attributes
    )


def __ensure_environment_created():
    global __environment
    __environment = _Environment(pooling=pooling)
