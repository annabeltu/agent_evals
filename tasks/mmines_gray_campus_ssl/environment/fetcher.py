"""Download text from web APIs over HTTPS."""

import ssl
import urllib.request


def ssl_context() -> ssl.SSLContext:
    """Return the TLS settings used for every request."""
    return ssl.create_default_context()


def fetch(url: str, timeout: float = 10.0) -> str:
    """Return the body of `url` as text."""
    with urllib.request.urlopen(url, context=ssl_context(), timeout=timeout) as response:
        return response.read().decode()
