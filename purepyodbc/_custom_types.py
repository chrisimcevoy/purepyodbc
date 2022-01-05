from typing import TypeVar

from ._typedef import SQLHANDLE

TSqlHandle = TypeVar("TSqlHandle", bound=SQLHANDLE)
