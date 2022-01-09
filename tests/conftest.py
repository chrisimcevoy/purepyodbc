import pytest

import purepyodbc


@pytest.fixture(
    params=[
        "DRIVER={FreeTDS};PORT=1433;",  # SQL Server
        "DRIVER={PostgreSQL Unicode};PORT=5432;",  # Postgres
    ]
)
def connection_string(request) -> str:
    return request.param + "SERVER=localhost;UID=sa;PWD=Password123;"


@pytest.fixture
def connection(connection_string) -> purepyodbc.Connection:
    with purepyodbc.connect(connection_string) as c:
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
def pyodbc_connection(pyodbc, connection_string):
    with pyodbc.connect(connection_string) as c:
        yield c


@pytest.fixture
def pyodbc_cursor(pyodbc_connection):
    with pyodbc_connection.cursor() as c:
        yield c
