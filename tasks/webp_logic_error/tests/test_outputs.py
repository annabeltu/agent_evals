"""Pytest checks for snap() inside the task sandbox."""

import pytest
from logic import snap


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([4, 2, 1, 3], [1, 2]),
        ([1, 2, 3, 4, 5, 6], [1, 2, 3]),
        ([6, 5, 4, 3, 2, 1], [1, 2, 3]),
        ([2, 2, 2, 2], [2, 2]),
        ([-1, 0, -5, 7], [-5, -1]),
        ([10, 10, 1, 1], [1, 1]),
    ],
)
def test_even_length(values, expected):
    assert snap(values) == expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([5, 1, 3], [1]),
        ([9, 7, 8, 1, 2], [1, 2]),
        ([1], []),
        ([3, -3, 0], [-3]),
    ],
)
def test_odd_length_rounds_down(values, expected):
    assert snap(values) == expected


@pytest.mark.parametrize("values", [[4, 2, 1, 3], [5, 1, 3], [3, 3, 1, 2, 2]])
def test_input_not_modified(values):
    original = list(values)
    snap(values)
    assert values == original


def test_returns_copy():
    values = [1, 2]
    result = snap(values)
    result.append(99)
    assert values == [1, 2]


def test_empty_list():
    assert snap([]) == []
