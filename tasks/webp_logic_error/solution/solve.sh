#!/bin/bash
set -euo pipefail

cat > /app/logic.py <<'PY'
def snap(input: list[int]):
    size = len(input) // 2
    result = sorted(input)
    result = result[:size]
    return result
PY
