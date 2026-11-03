"""Behavioral checks for the input-validation task inside Harbor's sandbox."""

import pytest
from calculator import add


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (2, 3, 5),
        (-2, 3, 1),
        (-2, -3, -5),
        (0, 0, 0),
        (5, 0, 5),
        (0, -5, -5),
        (1.5, 2.25, 3.75),
        (-1.5, 0.5, -1.0),
        (2, 0.5, 2.5),
        (0.5, 2, 2.5),
        (0.0, 0.0, 0.0),
    ],
)
def test_valid_numbers(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize("invalid", [True, False, "2", "", None, [], {}, (), 1 + 2j])
@pytest.mark.parametrize("position", ["a", "b"])
def test_rejects_invalid_argument(invalid, position):
    arguments = {"a": 2, "b": 3}
    arguments[position] = invalid
    with pytest.raises(TypeError):
        add(**arguments)


@pytest.mark.parametrize(
    ("a", "b"),
    [("2", "3"), ([], []), ((), ()), (True, False), (None, None)],
)
def test_rejects_two_invalid_arguments(a, b):
    with pytest.raises(TypeError):
        add(a, b)


def test_accepts_keyword_arguments():
    assert add(b=2.5, a=-1) == 1.5
