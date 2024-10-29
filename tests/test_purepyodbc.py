from __future__ import annotations

import pytest

import purepyodbc


@pytest.mark.parametrize(
    "include_attributes",
    [
        False,
        True,
    ],
)
def test_drivers(include_attributes: bool) -> None:
    drivers = purepyodbc.drivers(include_attributes=include_attributes)
    assert drivers
    print("")
    for driver in drivers:
        assert isinstance(driver, str)
        print(driver)
