"""Check that the weather client is configured."""

import sys

from weather.config import get_api_key

try:
    key = get_api_key()
except RuntimeError as error:
    print(f"Setup failed: {error}")
    sys.exit(1)

print(f"Setup OK: API key ending in ...{key[-4:]}")
