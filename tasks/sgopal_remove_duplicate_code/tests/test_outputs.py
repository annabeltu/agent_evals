"""Pytest checks for the duplicate removal inside the task sandbox."""

import functions


def test_one_duplicate_function_removed():
    remaining = [
        getattr(functions, name)
        for name in ("function_a", "function_b")
        if hasattr(functions, name)
    ]
    assert len(remaining) == 1
    assert remaining[0]() == "hello"
