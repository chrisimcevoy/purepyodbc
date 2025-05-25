from __future__ import annotations

import os
import platform
from types import ModuleType
from typing import TYPE_CHECKING, Generator

import pytest

import purepyodbc

if TYPE_CHECKING:
    import pyodbc as _pyodbc


PLATFORM = platform.system()

# These are set in docker-compose.yml.
# Default to localhost otherwise (e.g. in github actions).
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
POSTGRESQL_HOST = os.environ.get("POSTGRESQL_HOST", "localhost")
SQL_SERVER_HOST = os.environ.get("SQL_SERVER_HOST", "localhost")


@pytest.fixture(
    params=[
        pytest.param(
            ("ODBC Driver 17 for SQL Server", SQL_SERVER_HOST, 1433, "sa", "Password123", None),
            id="msodbcsql17",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_MSODBCSQL17", False),
                    reason="Skipped via environment variable",
                )
            ],
        ),
        pytest.param(
            ("SQL Server", SQL_SERVER_HOST, 1433, "sa", "Password123", None),
            id="SQL Server (MDAC)",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_MDAC", False),
                    reason="Skipped via environment variable",
                ),
                pytest.mark.skipif(
                    PLATFORM != "Windows",
                    reason=f"MDAC Driver not supported on {PLATFORM}.",
                ),
            ],
        ),
        pytest.param(
            ("FreeTDS", SQL_SERVER_HOST, 1433, "sa", "Password123", None),
            id="FreeTDS",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_FREETDS", False),
                    reason="Skipped via environment variable",
                ),
                pytest.mark.skipif(
                    PLATFORM == "Windows",
                    reason="FreeTDS driver not supported on Windows.",
                ),
            ],
        ),
        pytest.param(
            ("PostgreSQL Unicode", POSTGRESQL_HOST, 5432, "sa", "Password123", None),
            id="PgSQL Unicode",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_PGSQL_W", False),
                    reason="Skipped via environment variable",
                ),
            ],
        ),
        # TODO:
        #  pytest.param(
        #      ("PostgreSQL ANSI", POSTGRESQL_HOST, 5432, "sa", "Password123", None),
        #      id="PgSQL ANSI",
        #      marks=[
        #          pytest.mark.skipif(
        #              os.getenv("PUREPYODBC_SKIP_PGSQL_A", False),
        #              reason="Skipped via environment variable",
        #          ),
        #      ],
        #  ),
        pytest.param(
            ("MySQL ODBC 9.3 Unicode Driver", MYSQL_HOST, 3306, "root", "super-secret-password", "OPTION=67108864"),
            id="MySQL Unicode",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_MYSQL_W", False),
                    reason="Skipped via environment variable",
                ),
            ],
        ),
        pytest.param(
            # OPTION here enables multi statements.
            # See https://dev.mysql.com/doc/connector-odbc/en/connector-odbc-configuration-connection-parameters.html#codbc-dsn-option-flags
            ("MySQL ODBC 9.3 ANSI Driver", MYSQL_HOST, 3306, "root", "super-secret-password", "OPTION=67108864"),
            id="MySQL ANSI",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_MYSQL_A", False),
                    reason="Skipped via environment variable",
                ),
            ],
        ),
    ]
)
def connection_string(request: pytest.FixtureRequest) -> str:
    driver, server, port, user, password, suffix = request.param
    connection_str = f"DRIVER={{{driver}}};PORT={port};SERVER={server};UID={user};PWD={password};"
    if suffix:
        connection_str += suffix
    return connection_str


@pytest.fixture
def connection(
    connection_string: str,
) -> Generator[purepyodbc.Connection, None, None]:
    with purepyodbc.connect(connection_string) as c:
        yield c


@pytest.fixture
def cursor(
    connection: purepyodbc.Connection,
) -> Generator[purepyodbc.Cursor, None, None]:
    with connection.cursor() as c:
        if connection.dbms_name == "MySQL":
            c.execute("use mysql;")
        yield c


@pytest.fixture()
def pyodbc() -> ModuleType:
    module: ModuleType = pytest.importorskip("pyodbc", reason="pyodbc is not installed")
    return module


@pytest.fixture
def pyodbc_connection(pyodbc: ModuleType, connection_string: str) -> Generator[_pyodbc.Connection]:
    with pyodbc.connect(connection_string) as c:
        yield c


@pytest.fixture
def pyodbc_cursor(pyodbc_connection: _pyodbc.Connection) -> Generator[_pyodbc.Cursor]:
    with pyodbc_connection.cursor() as c:
        yield c
