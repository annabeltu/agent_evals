"""Check indentation-only repairs and all branches of the summary."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

MODULE_PATH = Path("/app/report.py")


@pytest.fixture(scope="module")
def report() -> ModuleType:
    spec = importlib.util.spec_from_file_location("task_report", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_only_leading_whitespace_changed() -> None:
    original = Path(__file__).with_name("original_report.py.txt").read_text()
    repaired = MODULE_PATH.read_text()
    assert [line.lstrip(" \t") for line in repaired.splitlines()] == [
        line.lstrip(" \t") for line in original.splitlines()
    ]


@pytest.mark.parametrize(
    ("numbers", "expected"),
    [
        ([], {"positive": 0, "negative": 0, "zero": 0, "total": 0}),
        ([0], {"positive": 0, "negative": 0, "zero": 1, "total": 0}),
        ([4], {"positive": 1, "negative": 0, "zero": 0, "total": 4}),
        ([-3], {"positive": 0, "negative": 1, "zero": 0, "total": -3}),
        ([3, -2, 0, 3], {"positive": 2, "negative": 1, "zero": 1, "total": 4}),
        ([0, 0, -5, -1, 2], {"positive": 1, "negative": 2, "zero": 2, "total": -4}),
        ([1, 2, 3], {"positive": 3, "negative": 0, "zero": 0, "total": 6}),
    ],
)
def test_summary(report: ModuleType, numbers: list[int], expected: dict[str, int]) -> None:
    before = numbers.copy()
    assert report.summarize_numbers(numbers) == expected
    assert numbers == before


@pytest.mark.parametrize(
    ("numbers", "expected"),
    [
        ([], "No numbers"),
        ([0], "positive=0, negative=0, zero=1, total=0"),
        ([3, -2, 0, 3], "positive=2, negative=1, zero=1, total=4"),
        ([-5, -1], "positive=0, negative=2, zero=0, total=-6"),
    ],
)
def test_description(report: ModuleType, numbers: list[int], expected: str) -> None:
    assert report.describe_numbers(numbers) == expected
