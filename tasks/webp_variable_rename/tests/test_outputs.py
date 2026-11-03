"""Pytest checks for the tax_rate rename inside the task sandbox."""

import difflib
from pathlib import Path

import pricing
import pytest
import report

APP = Path("/app")
EXPECTED = Path(__file__).parent / "expected"


@pytest.fixture
def restore_tax_rate(monkeypatch):
    monkeypatch.setattr(pricing, "tax_rate", pricing.tax_rate)


@pytest.mark.parametrize("name", ["pricing.py", "report.py"])
def test_files_match_expected(name):
    expected = (EXPECTED / name).read_text().splitlines(keepends=True)
    actual = (APP / name).read_text().splitlines(keepends=True)
    diff = "".join(difflib.unified_diff(expected, actual, "expected", "actual"))
    assert actual == expected, diff


def test_no_files_added_or_removed():
    assert {p.name for p in APP.glob("*.py")} == {"pricing.py", "report.py"}


def test_names():
    assert pricing.tax_rate == 0.2
    assert not hasattr(pricing, "rate")
    assert pricing.rate_cap == 100


@pytest.mark.parametrize(("amount", "expected"), [(50, 10.0), (100, 20.0), (1000, 100)])
def test_apply(amount, expected):
    assert pricing.apply(amount) == pytest.approx(expected)


def test_describe():
    assert pricing.describe() == "rate: standard"


def test_summary():
    assert report.summary(100) == "0.2 -> 20.0"


def test_bump(restore_tax_rate):
    report.bump()
    assert pricing.apply(100) == pytest.approx(30)
