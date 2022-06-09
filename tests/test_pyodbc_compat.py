import purepyodbc

from typing import List

import pytest


sql = "select * from information_schema.tables"


def get_attrs(foo) -> List[str]:
    return sorted([attr for attr in dir(foo) if not attr.startswith("_")])


@pytest.mark.xfail
def test_module_attributes(pyodbc):
    assert get_attrs(purepyodbc) == get_attrs(pyodbc)


@pytest.mark.xfail
def test_connection_attributes(connection, pyodbc_connection):
    assert get_attrs(connection) == get_attrs(pyodbc_connection)


def test_connection_searchescape(connection, pyodbc_connection):
    assert connection.searchescape == pyodbc_connection.searchescape


@pytest.mark.xfail
def test_cursor_attributes(cursor, pyodbc_cursor):
    assert get_attrs(cursor) == get_attrs(pyodbc_cursor)


def test_cursor_description(cursor, pyodbc_cursor):
    cursor.execute(sql)
    pyodbc_cursor.execute(sql)
    assert cursor.description == pyodbc_cursor.description


def test_cursor_tables(cursor, pyodbc_cursor):
    cursor.tables(schema="%")
    r = cursor.fetchone()
    pyodbc_cursor.tables(schema="%")
    pr = pyodbc_cursor.fetchone()
    # TODO: Fix rowcount for Cursor.tables()
    # assert cursor.rowcount == pyodbc_cursor.rowcount
    attrs = ["table_cat", "table_schem", "table_name", "table_type", "remarks"]
    for attr in attrs:
        r_value = getattr(r, attr)
        pr_value = getattr(pr, attr)
        assert (
            r_value == pr_value
        ), f"{attr} not equal (expected: {pr_value}, got {r_value})"


def test_cursor_procedures(cursor, pyodbc_cursor):
    cursor.procedures()
    r = cursor.fetchone()

    pyodbc_cursor.procedures()
    pr = pyodbc_cursor.fetchone()

    attrs = [
        "procedure_cat",
        "procedure_schem",
        "procedure_name",
        "num_input_params",
        "num_output_params",
        "num_result_sets",
        "remarks",
        "procedure_type",
    ]

    for attr in attrs:
        r_value = getattr(r, attr)
        pr_value = getattr(pr, attr)
        assert r_value == pr_value


def test_cursor_fetchone(cursor, pyodbc_cursor):

    a = cursor.execute(sql).fetchone()
    b = pyodbc_cursor.execute(sql).fetchone()

    for i, col in enumerate(pyodbc_cursor.description):
        col_name = col[0]
        assert getattr(a, col_name) == getattr(b, col_name)
        assert a[i] == b[i]
