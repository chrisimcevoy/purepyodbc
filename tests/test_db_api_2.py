import inspect
from typing import Any

import pytest

import purepyodbc
from purepyodbc import Cursor, Connection


class TestModule:
    def test_constructors(self):
        assert inspect.isfunction(getattr(purepyodbc, "connect"))

    @pytest.mark.parametrize(
        "global_, value",
        [
            ("apilevel", "2.0"),
            ("threadsafety", 1),
            ("paramstyle", "qmark"),
        ],
    )
    def test_globals(self, global_: str, value: Any):
        """https://www.python.org/dev/peps/pep-0249/#globals"""
        assert getattr(purepyodbc, global_) == value


class TestExceptions:
    """https://www.python.org/dev/peps/pep-0249/#exceptions"""

    @pytest.mark.parametrize(
        "exc,parent",
        [
            (purepyodbc.Warning, Exception),
            (purepyodbc.Error, Exception),
            (purepyodbc.InterfaceError, purepyodbc.Error),
            (purepyodbc.DatabaseError, purepyodbc.Error),
            (purepyodbc.DataError, purepyodbc.DatabaseError),
            (purepyodbc.OperationalError, purepyodbc.DatabaseError),
            (purepyodbc.IntegrityError, purepyodbc.DatabaseError),
            (purepyodbc.InternalError, purepyodbc.DatabaseError),
            (purepyodbc.ProgrammingError, purepyodbc.DatabaseError),
            (purepyodbc.NotSupportedError, purepyodbc.DatabaseError),
        ],
    )
    def test_exception_inheritance(self, exc, parent):
        assert issubclass(exc, parent)


class TestConnection:
    """https://www.python.org/dev/peps/pep-0249/#connection-objects"""

    @pytest.mark.parametrize("method", ["close", "commit", "rollback", "cursor"])
    def test_connection_has_method(self, connection: Connection, method: str):
        """https://www.python.org/dev/peps/pep-0249/#connection-methods"""
        assert inspect.ismethod(getattr(connection, method))


class TestCursor:
    @pytest.mark.parametrize(
        "attr",
        [
            "description",
            "rowcount",
            "arraysize",
        ],
    )
    def test_cursor_has_attribute(self, cursor: Cursor, attr: str):
        assert hasattr(cursor, attr)

    @pytest.mark.parametrize(
        "method",
        [
            pytest.param("callproc", marks=pytest.mark.xfail),
            "close",
            "execute",
            pytest.param("executemany", marks=pytest.mark.xfail),
            "fetchone",
            "fetchmany",
            "fetchall",
            "nextset",
            pytest.param("setinputsizes", marks=pytest.mark.xfail),
            pytest.param("setoutputsizes", marks=pytest.mark.xfail),
        ],
    )
    def test_cursor_has_method(self, cursor: Cursor, method: str):
        assert inspect.ismethod(getattr(cursor, method))
