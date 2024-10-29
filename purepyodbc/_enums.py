from __future__ import annotations

from enum import Enum


class OdbcVersion(Enum):
    SQL_OV_ODBC2 = 2
    SQL_OV_ODBC3 = 3
    SQL_OV_ODBC3_80 = 380


class SqlDataType(Enum):
    """https://docs.microsoft.com/en-us/sql/odbc/reference/appendixes/sql-data-types"""

    SQL_TINYINT = -6
    SQL_BIT = -7
    # SQL_WCHAR = -8
    SQL_WVARCHAR = -9
    SQL_WLONGVARCHAR = -10
    SQL_CHAR = 1
    SQL_INTEGER = 4
    SQL_SMALLINT = 5
    SQL_VARCHAR = 12
    SQL_TYPE_TIMESTAMP = 93


class CompletionType(Enum):
    """Enumeration of completion types passed to SQLEndTran."""

    SQL_COMMIT = 0
    SQL_ROLLBACK = 1


class ConnectionAttributeType(Enum):
    """Enumeration of ODBC connection attribute types.

    These are used to indicate to the driver manager which attributes the caller wishes to get or set when calling
    SQLGetConnectAttr and SQLSetConnectAttr.
    """

    SQL_ATTR_ACCESS_MODE = 101
    SQL_ATTR_ASYNC_DBC_EVENT = 119
    SQL_ATTR_ASYNC_DBC_FUNCTIONS_ENABLE = 117
    SQL_ATTR_ASYNC_ENABLE = 4
    SQL_ATTR_AUTO_IPD = 10001
    SQL_ATTR_AUTOCOMMIT = 102
    SQL_ATTR_CONNECTION_DEAD = 1209
    SQL_ATTR_CONNECTION_TIMEOUT = 113
    SQL_ATTR_CURRENT_CATALOG = 109
    SQL_ATTR_DBC_INFO_TOKEN = 118
    SQL_ATTR_ENLIST_IN_DTC = 1207
    SQL_ATTR_LOGIN_TIMEOUT = 103
    SQL_ATTR_METADATA_ID = 10014
    SQL_ATTR_ODBC_CURSORS = 110
    SQL_ATTR_PACKET_SIZE = 112
    SQL_ATTR_QUIET_MODE = 111
    SQL_ATTR_TRACE = 104
    SQL_ATTR_TRACEFILE = 105
    SQL_ATTR_TRANSLATE_LIB = 106
    SQL_ATTR_TRANSLATE_OPTION = 107
    SQL_ATTR_TXN_ISOLATION = 108


class ConnectionAutocommitMode(Enum):
    SQL_AUTOCOMMIT_OFF = 0
    SQL_AUTOCOMMIT_ON = 1


class EnvironmentAttributeType(Enum):
    """https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlsetenvattr-function"""

    SQL_ATTR_ODBC_VERSION = 200
    SQL_ATTR_CONNECTION_POOLING = 201
    SQL_ATTR_CP_MATCH = 202
    SQL_ATTR_OUTPUT_NTS = 10001


class DriverCompletion(Enum):
    SQL_DRIVER_NOPROMPT = 0
    SQL_DRIVER_COMPLETE = 1
    SQL_DRIVER_PROMPT = 2
    SQL_DRIVER_COMPLETE_REQUIRED = 3


class ReturnCode(Enum):
    SQL_INVALID_HANDLE = -2
    SQL_ERROR = -1
    SQL_SUCCESS = 0
    SQL_SUCCESS_WITH_INFO = 1
    SQL_NO_DATA = 100
    SQL_STILL_EXECUTING = 2


class HandleType(Enum):
    SQL_NULL_HANDLE = 0
    SQL_HANDLE_ENV = 1
    SQL_HANDLE_DBC = 2
    SQL_HANDLE_STMT = 3
    SQL_HANDLE_DESC = 4
    # SQL_HANDLE_DBC_INFO_TOKEN = ?


class InfoType(Enum):
    """Information types supported by SQLGetInfo.

    https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlgetinfo-function?view=sql-server-ver16#information-types
    """

    SQL_SEARCH_PATTERN_ESCAPE = 14


class SqlColumnAttrType(Enum):
    SQL_COLUMN_NAME = 1
    SQL_COLUMN_TYPE = 2
    SQL_COLUMN_LENGTH = 3
    SQL_COLUMN_PRECISION = 4
    SQL_COLUMN_SCALE = 5
    SQL_COLUMN_DISPLAY_SIZE = 6
    SQL_COLUMN_NULLABLE = 7
    SQL_COLUMN_UNSIGNED = 8
    SQL_COLUMN_MONEY = 9
    SQL_COLUMN_UPDATABLE = 10
    SQL_COLUMN_AUTO_INCREMENT = 11
    SQL_COLUMN_CASE_SENSITIVE = 12
    SQL_COLUMN_SEARCHABLE = 13
    SQL_COLUMN_TYPE_NAME = 14
    SQL_COLUMN_TABLE_NAME = 15
    SQL_COLUMN_OWNER_NAME = 16
    SQL_COLUMN_QUALIFIER_NAME = 17
    SQL_COLUMN_LABEL = 18


class SqlFetchType(Enum):
    SQL_FETCH_NEXT = 1
    SQL_FETCH_FIRST = 2
    SQL_FETCH_LAST = 3
    SQL_FETCH_PRIOR = 4
    SQL_FETCH_ABSOLUTE = 5
    SQL_FETCH_RELATIVE = 6


class LengthOrIndicatorType(Enum):
    SQL_NULL_DATA = -1
