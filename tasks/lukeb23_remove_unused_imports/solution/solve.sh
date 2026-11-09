#!/bin/bash
set -euo pipefail

cat > /app/report.py <<'PY'
"""Produce a deterministic summary of integer readings."""

import json
import math
from collections import Counter
from statistics import mean as average


def summarize_readings(readings: list[int]) -> dict[str, object]:
    counts = Counter(readings)
    mean_value = average(readings) if readings else 0
    return {
        "count": len(readings),
        "total": sum(readings),
        "mean": mean_value,
        "ceiling": math.ceil(mean_value),
        "counts_json": json.dumps(dict(counts), sort_keys=True),
    }
PY
