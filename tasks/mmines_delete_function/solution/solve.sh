#!/bin/bash
set -euo pipefail

# _square was only used by hypotenuse; _round stays because average uses it.
cat > /app/calculator.py <<'PY'
def _round(value):
    return round(value, 2)


def average(numbers):
    return _round(sum(numbers) / len(numbers))
PY
