#!/bin/bash
set -euo pipefail

cat > /app/pricing.py <<'PY'
tax_rate = 0.2
rate_cap = 100


def apply(amount):
    # rate applies before the cap
    return min(amount * tax_rate, rate_cap)


def describe():
    rate = "standard"
    return "rate: " + rate
PY

cat > /app/report.py <<'PY'
import pricing
from pricing import tax_rate


def summary(amount):
    return f"{tax_rate} -> {pricing.apply(amount)}"


def bump():
    pricing.tax_rate = 0.3
PY
