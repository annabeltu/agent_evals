"""Pytest checks for the type error fix inside the task sandbox."""

import pytest
from age import describe_age


@pytest.mark.parametrize(("age", "expected"), [(5, "Age: 5"), (0, "Age: 0")])
def test_describe_age(age, expected):
    assert describe_age(age) == expected
