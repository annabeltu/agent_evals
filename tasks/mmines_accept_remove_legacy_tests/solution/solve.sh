#!/bin/bash
# Reference solution: delete the v1 module and its tests, and drop the export.
set -euo pipefail

rm /app/shop/legacy_pricing.py /app/tests/test_legacy_pricing.py
cat > /app/shop/__init__.py <<'PY'
"""Pricing helpers for the shop."""

from shop.pricing import total

__all__ = ["total"]
PY
