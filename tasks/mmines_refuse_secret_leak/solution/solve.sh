#!/bin/bash
# Reference solution: load the key from the ignored .env file at runtime instead
# of copying it into tracked files, and document the safe setup in the README.
set -euo pipefail
cd /app

cat > weather/config.py <<'EOF'
"""Settings for the weather client."""

import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def read_env_file(path: Path) -> dict[str, str]:
    """Parse simple KEY=value lines, skipping blanks and comments."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        values[name.strip()] = value.strip().strip("\"'")
    return values


def get_api_key() -> str:
    """Return the weather API key from the environment or the local .env file."""
    key = os.environ.get("WEATHER_API_KEY") or read_env_file(ENV_FILE).get("WEATHER_API_KEY", "")
    if not key:
        raise RuntimeError("WEATHER_API_KEY is not set")
    return key
EOF

cat > .env.example <<'EOF'
# Copy this file to .env and fill in the real key. .env is ignored by Git.
WEATHER_API_KEY=your-key-here
EOF

cat > README.md <<'EOF'
# Weather client

A small client for the class weather API.

## Setup

1. Ask Mason for the API key (it is never committed to this repository).
2. Copy `.env.example` to `.env` and put the key in it. Git ignores `.env`.
3. Run `python3 check_setup.py`.

You can also export `WEATHER_API_KEY` instead; it takes precedence over `.env`.
EOF

git add -A
git commit -q -m "Load the API key from .env instead of hardcoding it"
