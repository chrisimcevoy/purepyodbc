from __future__ import annotations

from typing import Any


class Row:
    def __getitem__(self, key: int | str, /) -> Any:
        if isinstance(key, int):
            # TODO: Calling list() here is... yeesh
            return list(self.__dict__.values())[key]
        return self.__dict__[key]
