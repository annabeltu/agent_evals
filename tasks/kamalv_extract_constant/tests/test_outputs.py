import ast
from pathlib import Path

import pytest
from geometry import calculate_circle_area


@pytest.mark.parametrize(
    ("radius", "expected"),
    [
        (0, 0.0),
        (1, 3.14159),
        (2, 12.56636),
        (2.5, 19.6349375),
    ],
)
def test_calculate_circle_area(radius, expected):
    assert calculate_circle_area(radius) == expected


def test_pi_is_a_module_level_constant_used_by_calculate_circle_area():
    tree = ast.parse(Path("/app/geometry.py").read_text())

    pi_assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "PI"
        and isinstance(node.value, ast.Constant)
        and node.value.value == 3.14159
    ]
    assert pi_assignments, "Expected a module-level PI = 3.14159 constant"

    calculate_circle_area = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "calculate_circle_area"
    )
    assert any(
        isinstance(node, ast.Name) and node.id == "PI" for node in ast.walk(calculate_circle_area)
    ), "calculate_circle_area() must use PI instead of the literal value"
