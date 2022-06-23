import platform

from purepyodbc import Error, ProgrammingError

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


def test_emoticons_as_literal(cursor, connection_string):
    def check_freetds_version():
        from subprocess import getstatusoutput

        status, output = getstatusoutput("tsql -C")
        if status != 0:
            return
        for line in output.split("\n"):
            line = line.lower().strip()
            version_line_start = "version: freetds v"
            if line.startswith(version_line_start):
                from packaging import version

                freetds_version = version.parse(line.lstrip(version_line_start))
                fixed_version = version.parse("1.1.23")
                if freetds_version < fixed_version:
                    pytest.xfail("Doesn't work in old versions of FreeTDS")

    if "freetds" in connection_string.lower():
        # https://github.com/FreeTDS/freetds/issues/317
        check_freetds_version()

    if "windows" in platform.platform().lower():
        if "postgres" in connection_string.lower():
            # https://stackoverflow.com/a/38487921/5567657
            temp = cursor.connection.cursor()
            temp.execute("SET client_encoding TO 'UTF8';")
            temp.execute("SHOW server_encoding;")
            server_enc = temp.fetchone().server_encoding
            if server_enc.lower() != "utf8":
                # https://stackoverflow.com/a/19391061/5567657
                # https://github.com/ikalnytskyi/action-setup-postgres/issues/3
                pytest.skip("PostgreSQL is not in UTF8 character set!")

    v = "x \U0001F31C z"

    cursor.execute("drop table if exists t1")

    # TODO: something less hacky than a try/except
    try:
        # sql server
        cursor.execute("create table t1(s nvarchar(100))")
    except ProgrammingError:
        # postgresql
        cursor.execute("create table t1(s varchar(100))")

    # TODO: use a parameterised query instead of f-string
    cursor.execute(f"insert into t1 (s) values (N'{v}')")

    result = cursor.execute("select s from t1").fetchone()[0]

    assert result == v


def test_nextset(cursor):
    sql = "select 1; select 2;"
    cursor.execute(sql)

    first_set = cursor.fetchall()
    cursor.nextset()
    second_set = cursor.fetchall()

    assert len(first_set) == len(second_set) == 1
    assert first_set[0][0] == 1
    assert second_set[0][0] == 2


def test_tables(cursor):
    cursor.tables(schema="%")
    r = cursor.fetchone()
    assert hasattr(r, "table_cat")
    assert hasattr(r, "table_schem")
    assert hasattr(r, "table_name")
    assert hasattr(r, "table_type")
    assert hasattr(r, "remarks")
