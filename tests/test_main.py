import pytest

from smalldataviewer.__main__ import str_to_ints


@pytest.mark.parametrize('s,expected', [
    ['1,2,3', (1, 2, 3)],
    ['  1 , 2 , 3 ', (1, 2, 3)],
])
def test_str_to_ints(s,expected):
    assert str_to_ints(s) == expected
