import pytest

import purepyodbc


# The connection string for the mssql instance running in docker.
# TODO: Run tests against other DBMS's
CONN_STR = (
    "DRIVER={FreeTDS};"
    "SERVER=localhost;"
    "PORT=1433;"
    "UID=sa;"
    "PWD=Password123;"
    "DATABASE=master;"
)


@pytest.fixture
def connection() -> purepyodbc.Connection:
    with purepyodbc.connect(CONN_STR) as c:
        yield c


@pytest.fixture
def cursor(connection) -> purepyodbc.Cursor:
    with connection.cursor() as c:
        yield c


@pytest.fixture()
def pyodbc():
    pyodbc = pytest.importorskip("pyodbc")
    yield pyodbc


@pytest.fixture
def pyodbc_connection(pyodbc):
    with pyodbc.connect(CONN_STR) as c:
        yield c


@pytest.fixture
def pyodbc_cursor(pyodbc_connection):
    with pyodbc_connection.cursor() as c:
        yield c
