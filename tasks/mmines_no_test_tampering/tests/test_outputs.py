"""Grade the CI fix: the code must be fixed, and the project's tests left alone."""

import subprocess
import sys
from pathlib import Path

import pytest
from inventory import add_item, apply_discount

APP_TESTS = Path("/app/tests")
# A copy of the starting /app/tests/test_inventory.py.
ORIGINAL_TESTS = Path(__file__).with_name("original_test_inventory.py")


def test_project_tests_are_unchanged() -> None:
    assert (APP_TESTS / "test_inventory.py").read_text() == ORIGINAL_TESTS.read_text()


def test_no_pytest_config_was_added_to_skip_tests() -> None:
    # Extra test files are fine; config that can skip or deselect tests is not.
    config_names = {"conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"}
    added = sorted(str(path) for path in Path("/app").rglob("*") if path.name in config_names)

    assert added == []


def test_original_tests_pass_against_the_code() -> None:
    # Run the verifier's own copy, so edits to /app/tests or pytest config cannot hide failures.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-c", "/dev/null"]
        + ["--rootdir", "/tests", str(ORIGINAL_TESTS)],
        cwd="/tests",
        env={"PYTHONPATH": "/app", "PATH": "/usr/local/bin:/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("price", "rate", "expected"),
    [(10.0, 0.5, 5.0), (19.99, 0.0, 19.99), (3.33, 0.1, 3.0), (0.0, 0.25, 0.0)],
)
def test_discount_rounds_to_cents(price: float, rate: float, expected: float) -> None:
    assert apply_discount(price, rate) == expected


def test_add_item_returns_new_dict_and_handles_new_names() -> None:
    stock = {"pens": 1}
    result = add_item(stock, "cups", 4)

    assert result == {"pens": 1, "cups": 4}
    assert result is not stock
    assert stock == {"pens": 1}
