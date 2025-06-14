from __future__ import annotations

import pytest

from purepyodbc import Connection


@pytest.mark.xfail
def test_set_encoding(connection: Connection) -> None:
    connection.setencoding("utf-16")


@pytest.mark.xfail
def test_set_decoding(connection: Connection) -> None:
    connection.setdecoding(
        sqltype=1,
        encoding="utf-16",
        ctype=1,
    )


def test_autocommit(connection: Connection) -> None:
    assert connection.autocommit is False
    connection.autocommit = True
    assert connection.autocommit is True
    connection.autocommit = False
    assert connection.autocommit is False


def test_schema_term(connection: Connection) -> None:
    expected = {
        "Microsoft SQL Server": "owner",
        "PostgreSQL": "schema",
        "MySQL": "",
    }[connection.dbms_name]

    schema_term = connection.schema_term

    assert schema_term == expected
