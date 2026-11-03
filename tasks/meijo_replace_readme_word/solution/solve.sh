#!/bin/bash
set -euo pipefail

python - <<'PYTHON'
import re
from pathlib import Path

readme = Path("/app/README.md")
readme.write_bytes(re.sub(rb"\bsmall\b", b"simple", readme.read_bytes()))
PYTHON
