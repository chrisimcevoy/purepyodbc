import platform
import typing

import pytest

import purepyodbc


PLATFORM = platform.system()


@pytest.fixture(
    params=[
        "DRIVER={ODBC Driver 17 for SQL Server};PORT=1433;",
        "DRIVER={SQL Server};PORT=1433;",
        "DRIVER={FreeTDS};PORT=1433;",
        "DRIVER={PostgreSQL Unicode};PORT=5432;",
    ]
)
def connection_string(request) -> str:
    conn_str_fragment = request.param
    if PLATFORM == "Linux":
        if "{SQL Server}" in conn_str_fragment:
            pytest.skip("MDAC SQL Server Driver not supported on Linux.")
    elif PLATFORM == "Windows":
        if "{FreeTDS}" in conn_str_fragment:
            pytest.skip("FreeTDS not supported on Windows")

    return conn_str_fragment + "SERVER=localhost;UID=sa;PWD=Password123;"


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
