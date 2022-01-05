from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Generic

from ._custom_types import TSqlHandle
from ._typedef import SQLHANDLE
from ._enums import HandleType
from . import _odbc


@dataclass  # type: ignore
class Handler(Generic[TSqlHandle]):
    """Python object which references a SQLHANDLE."""

    handle: TSqlHandle = field(init=False, default_factory=SQLHANDLE)
    _closed: bool = field(init=False, default=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    @abstractmethod
    def handle_type(self) -> HandleType:
        ...

    def close(self) -> None:
        if self._closed:
            return
        _odbc.sql_free_handle(self)
        self._closed = True
