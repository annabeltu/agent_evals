#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier
if PYTHONPATH=/app python -m pytest -q /tests/test_outputs.py; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
