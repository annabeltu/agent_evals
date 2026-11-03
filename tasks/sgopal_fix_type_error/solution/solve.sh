#!/bin/bash
set -euo pipefail

cat > /app/age.py <<'PY'
def describe_age(age):
    return "Age: " + str(age)
PY
