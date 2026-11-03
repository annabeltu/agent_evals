#!/bin/bash
set -euo pipefail

git -C /app/repo for-each-ref --format='%(refname:short)' refs/heads/ \
    > /app/local-branches.txt
