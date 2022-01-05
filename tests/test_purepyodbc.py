import pytest

import purepyodbc


@pytest.mark.parametrize('ansi,include_attributes', [
    (False, False),
    (False, True),
    (True, False),
    (True, True),
])
def test_drivers(ansi: bool, include_attributes: bool):
    drivers = purepyodbc.drivers(ansi=ansi, include_attributes=include_attributes)
    assert drivers
    print('')
    for driver in drivers:
        assert isinstance(driver, str)
        print(driver)
