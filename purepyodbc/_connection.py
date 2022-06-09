from ._errors import ProgrammingError
from ._cursor import Cursor
from ._handler import Handler
from ._enums import HandleType, InfoType
from ._typedef import SQLHDBC


class Connection(Handler[SQLHDBC]):
    """Connection objects manage connections to the database.
    Each manages a single ODBC HDBC.
    """

    def cursor(self) -> Cursor:
        cur = Cursor(self._driver_manager, self)
        return cur

    @property
    def searchescape(self) -> str:
        """The escape character to be used with catalog functions."""
        return self._driver_manager.sql_get_info(
            self, InfoType.SQL_SEARCH_PATTERN_ESCAPE
        )

    @property
    def handle_type(self) -> HandleType:
        return HandleType.SQL_HANDLE_DBC

    def commit(self) -> None:
        # TODO: Implement Connection.commit()
        raise NotImplementedError

    def rollback(self) -> None:
        # TODO: Implement Connection.rollback()
        raise NotImplementedError

    def close(self) -> None:
        self._driver_manager.sql_disconnect(self)
        super().close()

    def setencoding(self, *args, **kwargs):
        raise NotImplementedError

    def setdecoding(self, sqltype, encoding, ctype) -> None:
        """
        setdecoding(sqltype, encoding=None, ctype=None) --> None

        Configures how text of type `ctype` (SQL_CHAR or SQL_WCHAR) is decoded
        when read from the database.

        When reading, the database will assign one of the sqltypes to text columns.
        pyodbc uses this lookup the decoding information set by this function.
        sqltype: pyodbc.SQL_CHAR or pyodbc.SQL_WCHAR

        encoding: A registered Python encoding such as "utf-8".

        ctype: The C data type should be requested.  Set this to SQL_CHAR for
          single-byte encodings like UTF-8 and to SQL_WCHAR for two-byte encodings
          like UTF-16.
        """
        raise NotImplementedError


def connection_check(cnxn: Connection) -> bool:
    return isinstance(cnxn, Connection)


def connection_validate(cnxn: Connection) -> Connection:
    if not cnxn or not connection_check(cnxn):
        raise TypeError("Connection object required")

    if not cnxn.handle.value:
        raise ProgrammingError("Attempt to use a closed connection.")

    return cnxn
