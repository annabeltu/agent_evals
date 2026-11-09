#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier
if python -m pytest -q -p no:cacheprovider /tests/test_outputs.py; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
