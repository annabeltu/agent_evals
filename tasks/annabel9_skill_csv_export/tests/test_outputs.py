"""Hidden checks for the Example Bank transaction exporter."""

import ast
import csv
import inspect
import io
from datetime import date
from decimal import Decimal

import exporter


def rows(csv_text):
    return list(csv.reader(io.StringIO(csv_text, newline="")))


def test_exports_header_and_sorted_formatted_rows():
    transactions = [
        {"transaction_id": "tx-20", "amount": Decimal("4"), "date": "2024-01-09"},
        {"transaction_id": "tx-02", "amount": "12.5", "date": date(2023, 12, 3)},
    ]

    assert rows(exporter.export_transactions(transactions)) == [
        ["transaction_id", "amount", "date"],
        ["tx-02", "12.50", "20231203"],
        ["tx-20", "4.00", "20240109"],
    ]


def test_missing_amount_is_na_and_special_characters_are_csv_escaped():
    transactions = [
        {"transaction_id": "z,9", "date": "2024-10-01", "amount": None},
        {"transaction_id": 'a"1', "date": "2024-02-29"},
    ]

    assert rows(exporter.export_transactions(transactions)) == [
        ["transaction_id", "amount", "date"],
        ['a"1', "NA", "20240229"],
        ["z,9", "NA", "20241001"],
    ]


def test_public_signature_is_preserved():
    assert str(inspect.signature(exporter.export_transactions)) == "(transactions)"


def test_uses_csv_module():
    tree = ast.parse(inspect.getsource(exporter))
    assert any(
        isinstance(node, ast.Import) and any(alias.name == "csv" for alias in node.names)
        for node in tree.body
    ) or any(isinstance(node, ast.ImportFrom) and node.module == "csv" for node in tree.body)
