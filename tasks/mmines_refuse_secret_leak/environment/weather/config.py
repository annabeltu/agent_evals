"""Settings for the weather client."""

import os


def get_api_key() -> str:
    """Return the weather API key."""
    key = os.environ.get("WEATHER_API_KEY", "")
    if not key:
        raise RuntimeError("WEATHER_API_KEY is not set")
    return key
