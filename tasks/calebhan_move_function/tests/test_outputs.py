"""Pytest checks for the move-function task inside the task sandbox."""

import ast
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

APP = Path("/app")
ORIGINAL_ORDERS = Path(__file__).with_name("original_orders.py")
FUNCTION = "calculate_tax"
ITEMS = [("pen", Decimal("1.50"), 4), ("pad", Decimal("3.25"), 2)]


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def app_modules() -> dict[Path, ast.Module]:
    return {
        path: parse(path) for path in sorted(APP.rglob("*.py")) if "__pycache__" not in path.parts
    }


def top_level_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def count_definitions(tree: ast.Module, name: str) -> int:
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
        for node in ast.walk(tree)
    )


def imported_modules(tree: ast.Module) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_function_is_defined_in_pricing_unchanged():
    moved = top_level_function(parse(APP / "pricing.py"), FUNCTION)
    assert moved is not None, "pricing.py has no top-level calculate_tax"
    original = top_level_function(parse(ORIGINAL_ORDERS), FUNCTION)
    assert ast.dump(moved) == ast.dump(original)


def test_function_is_defined_only_in_pricing():
    defined_in = [
        path.name
        for path, tree in app_modules().items()
        for _ in range(count_definitions(tree, FUNCTION))
    ]
    assert defined_in == ["pricing.py"]


def orders_aliases(tree: ast.Module) -> set[str]:
    return {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == "orders"
    }


def test_no_module_gets_function_through_orders():
    stale = []
    for path, tree in app_modules().items():
        aliases = orders_aliases(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "orders":
                if any(alias.name == FUNCTION for alias in node.names):
                    stale.append(f"{path.name}:{node.lineno} from orders import {FUNCTION}")
            elif (
                isinstance(node, ast.Attribute)
                and node.attr == FUNCTION
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                stale.append(f"{path.name}:{node.lineno} {node.value.id}.{FUNCTION}")
    assert stale == []


def test_pricing_does_not_import_app_modules():
    assert imported_modules(parse(APP / "pricing.py")).isdisjoint({"orders", "invoices", "cli"})


@pytest.mark.parametrize("module", ["pricing", "orders", "invoices", "cli"])
def test_module_imports_cleanly(module):
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=APP,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("amount", "exempt", "expected"),
    [
        (Decimal("12.50"), False, Decimal("0.91")),
        (Decimal("19.99"), False, Decimal("1.45")),
        (Decimal("0"), False, Decimal("0.00")),
        (Decimal("19.99"), True, Decimal("0.00")),
    ],
)
def test_calculate_tax_behavior(amount, exempt, expected):
    import pricing

    assert pricing.calculate_tax(amount, exempt=exempt) == expected


@pytest.mark.parametrize(
    ("discount", "exempt", "expected"),
    [
        (0, False, Decimal("13.41")),
        (10, False, Decimal("12.07")),
        (0, True, Decimal("12.50")),
        (100, False, Decimal("0.00")),
    ],
)
def test_order_total_behavior(discount, exempt, expected):
    import orders

    assert orders.order_total(ITEMS, discount, exempt=exempt) == expected


@pytest.mark.parametrize(
    ("exempt", "expected"),
    [
        (False, ["Subtotal: 12.50", "Tax: 0.91", "Total: 13.41"]),
        (True, ["Subtotal: 12.50", "Tax: 0.00", "Total: 12.50"]),
    ],
)
def test_invoice_lines_behavior(exempt, expected):
    import invoices

    assert invoices.invoice_lines(ITEMS, exempt=exempt) == expected


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["19.99"], "Tax on 19.99: 1.45"),
        (["19.99", "--exempt"], "Tax on 19.99: 0.00"),
    ],
)
def test_cli_behavior(args, expected):
    result = subprocess.run(
        [sys.executable, str(APP / "cli.py"), *args],
        cwd=APP,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected
