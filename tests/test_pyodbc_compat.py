import purepyodbc

from typing import List

import pytest


def get_attrs(foo) -> List[str]:
    return sorted([attr for attr in dir(foo) if not attr.startswith("_")])


@pytest.mark.xfail
def test_module_attributes(pyodbc):
    assert get_attrs(purepyodbc) == get_attrs(pyodbc)


@pytest.mark.xfail
def test_connection_attributes(connection, pyodbc_connection):
    assert get_attrs(connection) == get_attrs(pyodbc_connection)


@pytest.mark.xfail
def test_cursor_attributes(cursor, pyodbc_cursor):
    assert get_attrs(cursor) == get_attrs(pyodbc_cursor)


def test_cursor_description(cursor, pyodbc_cursor):
    sql = "select * from information_schema.tables"
    cursor.execute(sql)
    pyodbc_cursor.execute(sql)
    assert cursor.description == pyodbc_cursor.description


def test_cursor_fetchone(cursor, pyodbc_cursor):
    sql = "select * from information_schema.tables"
    a = cursor.execute(sql).fetchone()
    b = pyodbc_cursor.execute(sql).fetchone()

    for col in b.cursor_description:
        col_name = col[0]
        assert getattr(a, col_name) == getattr(b, col_name)
