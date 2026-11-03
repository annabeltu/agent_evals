#!/bin/bash
set -euo pipefail

mkdir -p /app/solution/solving-solutions
mv /app/solution/solve.sh /app/solution/solving-solutions/solve.sh
sed -i 's|/app/solution/solve.sh|/app/solution/solving-solutions/solve.sh|' /app/run.sh
