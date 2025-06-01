from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING

import pytest

import purepyodbc
from purepyodbc import Connection, Cursor

if TYPE_CHECKING:
    import pyodbc as _pyodbc

sql = "select * from information_schema.tables"
drop_parent_sql = "drop table if exists parent;"
create_parent_sql = "create table parent (id integer primary key);"
drop_child_sql = """drop table if exists child;"""
create_child_sql = """
    create table child (
        id integer primary key,
        parent_id integer,
        constraint fk_parent foreign key (parent_id) references parent(id)
    );"""


def get_attrs(foo: object) -> list[str]:
    return sorted([attr for attr in dir(foo) if not attr.startswith("_")])


@pytest.mark.xfail
def test_module_attributes(pyodbc: ModuleType) -> None:
    assert get_attrs(purepyodbc) == get_attrs(pyodbc)


@pytest.mark.xfail
def test_connection_attributes(connection: Connection, pyodbc_connection: _pyodbc.Connection) -> None:
    assert get_attrs(connection) == get_attrs(pyodbc_connection)


def test_connection_searchescape(connection: Connection, pyodbc_connection: _pyodbc.Connection) -> None:
    assert connection.searchescape == pyodbc_connection.searchescape


@pytest.mark.xfail
def test_cursor_attributes(cursor: Cursor, pyodbc_cursor: _pyodbc.Cursor) -> None:
    assert get_attrs(cursor) == get_attrs(pyodbc_cursor)


def test_cursor_description(cursor: Cursor, pyodbc_cursor: _pyodbc.Cursor) -> None:
    cursor.execute(sql)
    pyodbc_cursor.execute(sql)
    assert cursor.description == pyodbc_cursor.description


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"table": "parent"},
        {"table": "child"},
    ],
    ids=lambda x: str(x),
)
def test_cursor_tables(cursor: Cursor, pyodbc_cursor: _pyodbc.Cursor, kwargs: dict[str, str]) -> None:
    # TODO: Fix this "pyodbc compatibility" test for MySQL
    if cursor.connection.dbms_name == "MySQL":
        pytest.skip("pyodbc compatibility tests aren't working for MySQL")

    # Arrange
    cursor.execute(drop_child_sql)
    cursor.execute(drop_parent_sql)
    cursor.execute(create_parent_sql)
    cursor.execute(create_child_sql)
    cursor.connection.commit()

    attrs = ["table_cat", "table_schem", "table_name", "table_type", "remarks"]

    tables = 0

    # Act
    cursor.tables(**kwargs)
    r = cursor.fetchone()
    pyodbc_cursor.tables(**kwargs)
    pr = pyodbc_cursor.fetchone()

    # Assert
    # TODO: Fix rowcount for Cursor.tables()
    # assert cursor.rowcount == pyodbc_cursor.rowcount
    if pr:
        tables += 1
        for attr in attrs:
            pr_value = getattr(pr, attr)
            r_value = getattr(r, attr)
            assert r_value == pr_value, f"{attr} not equal (expected: {pr_value}, got {r_value})"
    assert tables > 0, "No tables in result set"


def test_cursor_procedures(cursor: Cursor, pyodbc_cursor: _pyodbc.Cursor) -> None:
    # TODO: Fix this "pyodbc compatibility" test for MySQL
    if cursor.connection.dbms_name == "MySQL":
        pytest.skip("pyodbc compatibility tests aren't working for MySQL")

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


@pytest.mark.parametrize(
    "kwargs",
    [
        # TODO: write a separate test for xfails like this, and assert we get the same error message.
        pytest.param(
            {},
            id="No arguments",
            marks=[pytest.mark.xfail(reason="Requires at least one argument.")],
        ),
        pytest.param({"foreignTable": "child"}, id="foreignTable=child"),
        pytest.param({"table": "parent"}, id="table=parent"),
        pytest.param({"table": "parent", "foreignTable": "child"}, id="both"),
    ],
)
def test_cursor_foreignkeys(cursor: Cursor, pyodbc_cursor: _pyodbc.Cursor, kwargs: dict[str, str]) -> None:
    """Test that Cursor.foreignkeys() works as in pyodbc."""

    # Arrange
    cursor.execute(drop_child_sql)
    cursor.execute(drop_parent_sql)
    cursor.execute(create_parent_sql)
    cursor.execute(create_child_sql)
    cursor.connection.commit()

    attrs = [
        "pktable_cat",
        "pktable_schem",
        "pktable_name",
        "pkcolumn_name",
        "fktable_cat",
        "fktable_schem",
        "fktable_name",
        "fkcolumn_name",
        "key_seq",
        "update_rule",
        "delete_rule",
        "fk_name",
        "pk_name",
        "deferrability",
    ]

    # Act
    cursor.foreignKeys(**kwargs)
    pyodbc_cursor.foreignKeys(**kwargs)
    row = cursor.fetchone()
    pyodbc_row = pyodbc_cursor.fetchone()

    # Assert
    assert row is not None

    if cursor.connection.dbms_name == "MySQL":
        # pyodbc's foreignKeys does not seem to work for MySQL.
        assert pyodbc_row is None
    else:
        # Check that purepyodbc returns the same data as pyodbc
        for attr in attrs:
            pyodbc_row_attr = getattr(pyodbc_row, attr)
            purepyodbc_row_attr = getattr(row, attr)
            assert (
                purepyodbc_row_attr == pyodbc_row_attr
            ), f"{attr} returned different values: {purepyodbc_row_attr} and {pyodbc_row_attr}"

    # Beyond compatibility with pyodbc, check the actual values are populated.
    for attr in attrs:
        # Some databases (e.g. MySQL) do not support schemas.
        # We can tell that programmatically by inspecting the return value of SQLGetInfo for SQL_SCHEMA_TERM.
        # If it is an empty string, schemas are not supported.
        if attr.endswith("_schem") and not cursor.connection.schema_term:
            assert row[attr] is None
        else:
            assert row[attr] is not None

    # Only one row should be returned, subsequent calls should return None.
    assert cursor.fetchone() is pyodbc_cursor.fetchone() is None


def test_cursor_fetchone(cursor: Cursor, pyodbc_cursor: _pyodbc.Cursor) -> None:
    a = cursor.execute(sql).fetchone()
    b = pyodbc_cursor.execute(sql).fetchone()

    for i, col in enumerate(pyodbc_cursor.description):
        col_name = col[0]
        assert getattr(a, col_name) == getattr(b, col_name)
        assert a is not None
        assert b is not None
        assert a[i] == b[i]
