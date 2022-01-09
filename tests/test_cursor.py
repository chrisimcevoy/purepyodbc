from purepyodbc import Error

import pytest

SQL = "select * from information_schema.tables;"


def test_execute(cursor):
    cursor.execute(SQL)


def test_fetchone(cursor):
    cursor.execute(SQL)
    row = cursor.fetchone()
    assert row


def test_fetchall(cursor):
    cursor.execute(SQL)
    rows = cursor.fetchall()
    assert len(rows) > 1


def test_fetchmany(cursor):
    cursor.execute(SQL)
    rows = cursor.fetchmany()
    assert len(rows) == cursor.arraysize == 1


@pytest.mark.parametrize("arraysize", [1, 2, 3, 4, 5])
def test_fetchmany_arraysize(cursor, arraysize):
    cursor.arraysize = arraysize
    cursor.execute(SQL)
    rows = cursor.fetchmany()
    assert len(rows) == arraysize
    assert all(rows)


@pytest.mark.parametrize("size", [1, 2, 3, 4, 5])
def test_fetchmany_size(cursor, size):
    cursor.execute(SQL)
    rows = cursor.fetchmany(size)
    assert len(rows) == size
    assert all(rows)


def test_illegal_fetchall_raises(cursor):
    with pytest.raises(Error):
        cursor.fetchall()


def test_illegal_fetchmany_raises(cursor):
    with pytest.raises(Error):
        cursor.fetchmany()


def test_illegal_fetchone_raises(cursor):
    with pytest.raises(Error):
        cursor.fetchone()


def test_nextset(cursor):
    sql = "select 1; select 2;"
    cursor.execute(sql)

    first_set = cursor.fetchall()
    cursor.nextset()
    second_set = cursor.fetchall()

    assert len(first_set) == len(second_set) == 1
    assert first_set[0][0] == 1
    assert second_set[0][0] == 2
