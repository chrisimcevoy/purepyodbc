from __future__ import annotations

import pytest

from purepyodbc import Cursor, ProgrammingError


def test_invalid_syntax(cursor: Cursor) -> None:
    with pytest.raises(ProgrammingError):
        cursor.execute("foo bar baz")
