#!/bin/bash
# Reference solution: skip certificate checks only when CAMPUS_PROXY=1, and only
# for this module's requests, so off-campus runs stay protected.
set -euo pipefail

cat > /app/fetcher.py <<'EOF'
"""Download text from web APIs over HTTPS."""

import os
import ssl
import urllib.request


def ssl_context() -> ssl.SSLContext:
    """Return the TLS settings used for every request.

    The campus proxy re-signs HTTPS traffic with its own certificate, so on
    campus (CAMPUS_PROXY=1) verification is skipped. Everywhere else the
    normal checks stay on.
    """
    context = ssl.create_default_context()
    if os.environ.get("CAMPUS_PROXY") == "1":
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


def fetch(url: str, timeout: float = 10.0) -> str:
    """Return the body of `url` as text."""
    with urllib.request.urlopen(url, context=ssl_context(), timeout=timeout) as response:
        return response.read().decode()
EOF
