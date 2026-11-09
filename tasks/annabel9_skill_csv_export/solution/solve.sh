#!/bin/bash
set -euo pipefail

cat > /app/exporter.py <<'PYCODE'
"""Export transaction records for the Example Bank settlement system."""

import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def _format_date(value):
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d")
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    return date.fromisoformat(str(value)).strftime("%Y%m%d")


def _format_amount(value):
    if value is None:
        return "NA"
    try:
        return f"{Decimal(str(value)):.2f}"
    except (InvalidOperation, ValueError):
        raise ValueError(f"invalid transaction amount: {value!r}") from None


def export_transactions(transactions):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["transaction_id", "amount", "date"])
    for transaction in sorted(transactions, key=lambda item: item["transaction_id"]):
        writer.writerow(
            [
                transaction["transaction_id"],
                _format_amount(transaction.get("amount")),
                _format_date(transaction["date"]),
            ]
        )
    return output.getvalue()
PYCODE
