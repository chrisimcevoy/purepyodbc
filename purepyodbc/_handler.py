from __future__ import annotations

from abc import abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING

from ._driver_manager import DriverManager
from ._enums import HandleType
from ._typedef import SQLHANDLE

if TYPE_CHECKING:
    from typing_extensions import Self


class Handler:
    """Python object which references a SQLHANDLE."""

    def __init__(self, driver_manager: DriverManager) -> None:
        self._closed = False
        self.handle = SQLHANDLE()
        self._driver_manager: DriverManager = driver_manager

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # TODO: What happens if self.close() raises?
        self.close()

    @property
    @abstractmethod
    def handle_type(self) -> HandleType: ...

    def close(self) -> None:
        if self._closed:
            return
        self._driver_manager.sql_free_handle(self)
        self._closed = True
