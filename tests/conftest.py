import os
import platform
import typing

import pytest

import purepyodbc


PLATFORM = platform.system()

# These are set in docker-compose.yml.
# Default to localhost otherwise (e.g. in github actions).
SQL_SERVER_HOST = os.environ.get("SQL_SERVER_HOST", "localhost")
POSTGRESQL_HOST = os.environ.get("POSTGRESQL_HOST", "localhost")


@pytest.fixture(
    params=[
        pytest.param(
            ("ODBC Driver 17 for SQL Server", SQL_SERVER_HOST, 1433),
            id="msodbcsql17",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_MSODBCSQL17", False),
                    reason="Skipped via environment variable",
                )
            ],
        ),
        pytest.param(
            ("SQL Server", SQL_SERVER_HOST, 1433),
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
            ("FreeTDS", SQL_SERVER_HOST, 1433),
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
            ("PostgreSQL Unicode", POSTGRESQL_HOST, 5432),
            id="PgSQL Unicode",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_PGSQL_U", False),
                    reason="Skipped via environment variable",
                ),
            ],
        ),
    ]
)
def connection_string(request) -> str:
    driver, server, port = request.param
    return f"DRIVER={{{driver}}};PORT={port};SERVER={server};UID=sa;PWD=Password123;"


@pytest.fixture
def connection(
    connection_string,
) -> typing.Generator[purepyodbc.Connection, None, None]:
    with purepyodbc.connect(connection_string) as c:
        yield c


@pytest.fixture
def cursor(connection) -> typing.Generator[purepyodbc.Cursor, None, None]:
    with connection.cursor() as c:
        yield c


@pytest.fixture()
def pyodbc():
    pyodbc = pytest.importorskip("pyodbc", reason="pyodbc is not installed")
    yield pyodbc


@pytest.fixture
def pyodbc_connection(pyodbc, connection_string):
    with pyodbc.connect(connection_string) as c:
        yield c


@pytest.fixture
def pyodbc_cursor(pyodbc_connection):
    with pyodbc_connection.cursor() as c:
        yield c
