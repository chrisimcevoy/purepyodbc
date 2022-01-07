import pytest


@pytest.mark.xfail
def test_set_encoding(connection):
    connection.setencoding("utf-16")


@pytest.mark.xfail
def test_set_decoding(connection):
    connection.setdecoding()
