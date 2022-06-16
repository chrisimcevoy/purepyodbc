import os
import platform
import typing

import pytest

import purepyodbc


PLATFORM = platform.system()


@pytest.fixture(
    params=[
        pytest.param(
            ("ODBC Driver 17 for SQL Server", 1433),
            id="msodbcsql17",
            marks=[
                pytest.mark.skipif(
                    os.getenv("PUREPYODBC_SKIP_MSODBCSQL17", False),
                    reason="Skipped via environment variable",
                )
            ],
        ),
        pytest.param(
            ("SQL Server", 1433),
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
            ("FreeTDS", 1433),
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
            ("PostgreSQL Unicode", 5432),
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
    driver, port = request.param
    return f"DRIVER={{{driver}}};PORT={port};SERVER=localhost;UID=sa;PWD=Password123;"


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
    pyodbc = pytest.importorskip("pyodbc")
    yield pyodbc


@pytest.fixture
def pyodbc_connection(pyodbc, connection_string):
    with pyodbc.connect(connection_string) as c:
        yield c


@pytest.fixture
def pyodbc_cursor(pyodbc_connection):
    with pyodbc_connection.cursor() as c:
        yield c
