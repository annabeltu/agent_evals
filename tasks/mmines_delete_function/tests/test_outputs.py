"""Pytest checks that hypotenuse and only its own helper were deleted."""

import calculator


def test_hypotenuse_and_its_helper_deleted():
    assert not hasattr(calculator, "hypotenuse")
    assert not hasattr(calculator, "_square")


def test_shared_helper_kept():
    assert hasattr(calculator, "_round")
    assert calculator.average([1, 1, 2]) == 1.33
