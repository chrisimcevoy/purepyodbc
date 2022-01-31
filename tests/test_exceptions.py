import pytest

from purepyodbc import ProgrammingError


def test_invalid_syntax(cursor):
    with pytest.raises(ProgrammingError):
        cursor.execute("foo bar baz")
