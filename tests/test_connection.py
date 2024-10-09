import pytest


@pytest.mark.xfail
def test_set_encoding(connection):
    connection.setencoding("utf-16")


@pytest.mark.xfail
def test_set_decoding(connection):
    connection.setdecoding()


def test_autocommit(connection) -> None:
    assert connection.autocommit is False
    connection.autocommit = True
    assert connection.autocommit is True
    connection.autocommit = False
    assert connection.autocommit is False
