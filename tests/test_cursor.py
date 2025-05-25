from __future__ import annotations

import uuid

import pytest

from purepyodbc import Connection, Cursor, Error

SQL = "select * from information_schema.tables;"


def test_execute(cursor: Cursor) -> None:
    cursor.execute(SQL)


def test_fetchone(cursor: Cursor) -> None:
    cursor.execute(SQL)
    row = cursor.fetchone()
    assert row


def test_fetchall(cursor: Cursor) -> None:
    cursor.execute(SQL)
    rows = cursor.fetchall()
    assert len(rows) > 1


def test_fetchmany(cursor: Cursor) -> None:
    cursor.execute(SQL)
    rows = cursor.fetchmany()
    assert len(rows) == cursor.arraysize == 1


@pytest.mark.parametrize("arraysize", [1, 2, 3, 4, 5])
def test_fetchmany_arraysize(cursor: Cursor, arraysize: int) -> None:
    cursor.arraysize = arraysize
    cursor.execute(SQL)
    rows = cursor.fetchmany()
    assert len(rows) == arraysize
    assert all(rows)


@pytest.mark.parametrize("size", [1, 2, 3, 4, 5])
def test_fetchmany_size(cursor: Cursor, size: int) -> None:
    cursor.execute(SQL)
    rows = cursor.fetchmany(size)
    assert len(rows) == size
    assert all(rows)


def test_illegal_fetchall_raises(cursor: Cursor) -> None:
    with pytest.raises(Error):
        cursor.fetchall()


def test_illegal_fetchmany_raises(cursor: Cursor) -> None:
    with pytest.raises(Error):
        cursor.fetchmany()


def test_illegal_fetchone_raises(cursor: Cursor) -> None:
    with pytest.raises(Error):
        cursor.fetchone()


def test_emoticons_as_literal(cursor: Cursor) -> None:
    v = "x \U0001f31c z"

    cursor.execute("drop table if exists t1")

    # TODO: something less hacky
    dbms_name = cursor.connection.dbms_name
    if dbms_name == "Microsoft SQL Server":
        cursor.execute("create table t1(s nvarchar(100))")
    elif dbms_name == "PostgreSQL":
        cursor.execute("create table t1(s varchar(100))")
    elif dbms_name == "MySQL":
        # TODO: Fix this test for mysql
        pytest.skip("Fails with MySQL currently ;-(")
        # MySQL defaults to latin1, I think?
        # utf8mb4 needed for full unicode.
        cursor.execute("CREATE TABLE t1(s varchar(100)) DEFAULT CHARSET=utf8mb4")
    else:
        raise Exception(f"Add a create table statement to this test for {dbms_name}")

    # TODO: use a parameterised query instead of f-string
    if dbms_name == "MySQL":
        cursor.execute(f"insert into t1 (s) values ('{v}')")
    cursor.execute(f"insert into t1 (s) values (N'{v}')")

    row = cursor.execute("select s from t1").fetchone()

    assert row is not None

    result = row[0]

    assert result == v


def test_nextset(cursor: Cursor) -> None:
    sql = "select 1; select 2;"
    cursor.execute(sql)

    first_set = cursor.fetchall()
    cursor.nextset()
    second_set = cursor.fetchall()

    assert len(first_set) == len(second_set) == 1
    assert first_set[0][0] == 1
    assert second_set[0][0] == 2


def test_tables(connection: Connection, cursor: Cursor) -> None:
    tbl = str(uuid.uuid4())
    cursor.execute(f"drop table if exists {connection.identifier_quote_char}{tbl}{connection.identifier_quote_char};")
    cursor.execute(
        f"create table {connection.identifier_quote_char}{tbl}{connection.identifier_quote_char} (a varchar(1));"
    )
    cursor.tables(table=tbl)
    r = cursor.fetchone()
    assert r is not None
    assert hasattr(r, "table_cat")
    assert hasattr(r, "table_schem")
    assert hasattr(r, "table_name")
    assert hasattr(r, "table_type")
    assert hasattr(r, "remarks")
    assert r.table_name == tbl
