#!/bin/sh
set -eu

python - <<'PY'
from pathlib import Path

path = Path("/app/geometry.py")
source = path.read_text()
old_return = "return 3.14159 * radius * radius"

if old_return not in source:
    raise SystemExit("Expected starter implementation was not found")

updated = source.replace(old_return, "return PI * radius * radius", 1)
path.write_text("PI = 3.14159\n\n\n" + updated)
PY
