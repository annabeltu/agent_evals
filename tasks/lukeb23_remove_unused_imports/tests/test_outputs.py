"""Check unused bindings are removed while preserving code and behavior."""

import ast
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

MODULE_PATH = Path("/app/report.py")
IMPORT_TYPES = (ast.Import, ast.ImportFrom)


@pytest.fixture(scope="module")
def tree() -> ast.Module:
    return ast.parse(MODULE_PATH.read_text())


@pytest.fixture(scope="module")
def report() -> ModuleType:
    spec = importlib.util.spec_from_file_location("task_report", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_used_imports(tree: ast.Module) -> None:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((None, item.name, item.asname) for item in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imports.extend((node.module, item.name, item.asname) for item in node.names)
    assert len(imports) == 4
    assert set(imports) == {
        (None, "json", None),
        (None, "math", None),
        ("collections", "Counter", None),
        ("statistics", "mean", "average"),
    }


def test_non_import_code_unchanged(tree: ast.Module) -> None:
    original = ast.parse(Path(__file__).with_name("original_report.py.txt").read_text())
    actual_body = [node for node in tree.body if not isinstance(node, IMPORT_TYPES)]
    expected_body = [node for node in original.body if not isinstance(node, IMPORT_TYPES)]
    assert ast.dump(ast.Module(body=actual_body, type_ignores=[])) == ast.dump(
        ast.Module(body=expected_body, type_ignores=[])
    )


@pytest.mark.parametrize(
    ("readings", "mean", "ceiling", "counts"),
    [
        ([], 0, 0, "{}"),
        ([0], 0, 0, '{"0": 1}'),
        ([1, 2, 2], 5 / 3, 2, '{"1": 1, "2": 2}'),
        ([-3, -2], -2.5, -2, '{"-3": 1, "-2": 1}'),
        ([-2, 0, 2, 2], 0.5, 1, '{"-2": 1, "0": 1, "2": 2}'),
        ([10, 2, 10], 22 / 3, 8, '{"2": 1, "10": 2}'),
    ],
)
def test_behavior(
    report: ModuleType, readings: list[int], mean: float, ceiling: int, counts: str
) -> None:
    before = readings.copy()
    assert report.summarize_readings(readings) == {
        "count": len(readings),
        "total": sum(readings),
        "mean": mean,
        "ceiling": ceiling,
        "counts_json": counts,
    }
    assert readings == before
