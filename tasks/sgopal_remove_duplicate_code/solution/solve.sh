#!/bin/bash
set -euo pipefail

cat > /app/functions.py <<'PY'
def function_a():
    return "hello"
PY
