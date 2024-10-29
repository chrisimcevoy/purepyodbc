from __future__ import annotations

from typing import Sequence

from . import _driver_manager
from ._connection import Connection
from ._cursor import Cursor
from ._environment import Environment as _Environment
from ._errors import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)

apilevel: str = "2.0"
lowercase: bool = False
native_uuid: bool = False
paramstyle: str = "qmark"
pooling: bool = True
threadsafety: int = 1  # TODO: Check threadsafety
# release-please-action automatically updates this attribute.
__version__ = "0.1.0"
# This one is merely to mimic the pyodbc api.
version = __version__

__driver_manager: _driver_manager.DriverManager = _driver_manager.detect_driver_manager()
__environment: _Environment


def connect(
    connection_string: str,
    autocommit: bool = False,
    ansi: bool = False,
    timeout: int = 0,
    readonly: bool = False,
    attrs_before: dict[int, int | bytes | bytearray | str | Sequence[str]] | None = None,
    encoding: str | None = None,
) -> Connection:
    __ensure_environment_created()

    connection = __environment.connection(
        connection_string, autocommit, ansi, timeout, readonly, attrs_before, encoding
    )

    return connection


def drivers(include_attributes: bool = False) -> list[str]:
    __ensure_environment_created()
    return __driver_manager.sql_drivers(__environment, include_attributes=include_attributes)


def __ensure_environment_created() -> None:
    global __environment
    __environment = _Environment(driver_manager=__driver_manager, pooling=pooling)


__all__ = [
    "Connection",
    "Cursor",
    "Warning",
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    # TODO: __all__
]
