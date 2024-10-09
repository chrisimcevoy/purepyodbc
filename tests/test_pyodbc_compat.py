import purepyodbc

from typing import List

import pytest


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


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"table": "parent"},
        {"table": "child"},
    ],
)
def test_cursor_tables(cursor, pyodbc_cursor, kwargs):
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
            assert (
                r_value == pr_value
            ), f"{attr} not equal (expected: {pr_value}, got {r_value})"
    assert tables > 0, "No tables in result set"


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


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            {},
            id="No arguments",
            marks=[pytest.mark.xfail(reason="Requires at least one argument.")],
        ),
        pytest.param({"foreignTable": "child"}, id="foreignTable=child"),
        pytest.param({"table": "parent"}, id="table=parent"),
    ],
)
def test_cursor_foreignkeys(cursor, pyodbc_cursor, kwargs):
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

    fk_count = 0

    # Act
    pyodbc_cursor.foreignKeys(**kwargs)
    cursor.foreignKeys(**kwargs)

    # Assert
    pyodbc_fk = pyodbc_cursor.fetchone()
    while pyodbc_fk:
        fk_count += 1
        fk = cursor.fetchone()
        assert fk is not None

        for attr in attrs:
            pyodbc_fk_value = getattr(pyodbc_fk, attr)
            fk_value = getattr(fk, attr)
            assert fk_value == pyodbc_fk_value
        pyodbc_fk = pyodbc_cursor.fetchone()
    assert fk_count > 0, "No foreign keys were checked"


def test_cursor_fetchone(cursor, pyodbc_cursor):
    a = cursor.execute(sql).fetchone()
    b = pyodbc_cursor.execute(sql).fetchone()

    for i, col in enumerate(pyodbc_cursor.description):
        col_name = col[0]
        assert getattr(a, col_name) == getattr(b, col_name)
        assert a[i] == b[i]
