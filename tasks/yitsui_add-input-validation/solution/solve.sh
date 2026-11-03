#!/bin/bash
set -euo pipefail

cat > /app/calculator.py <<'PY'
def add(a, b):
    for value in (a, b):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Arguments must be integers or floats, excluding booleans")
    return a + b
PY
