from abc import abstractmethod

from ._driver_manager import DriverManager
from ._typedef import SQLHANDLE
from ._enums import HandleType


class Handler:
    """Python object which references a SQLHANDLE."""

    def __init__(self, driver_manager: DriverManager) -> None:
        self._closed = False
        self.handle = SQLHANDLE()
        self._driver_manager: DriverManager = driver_manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    @abstractmethod
    def handle_type(self) -> HandleType: ...

    def close(self) -> None:
        if self._closed:
            return
        self._driver_manager.sql_free_handle(self)
        self._closed = True
