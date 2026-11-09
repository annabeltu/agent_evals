"""A local HTTPS server with a self-signed certificate, standing in for the campus proxy."""

import http.server
import os
import ssl
import subprocess
import sys
import threading
from collections.abc import Iterator

import pytest

BODY = "hello from campus"
# Prints the fetched body, then whether the process-wide default TLS settings
# were left alone (a global patch would weaken every other library too).
FETCH_SCRIPT = """
import ssl, sys
import fetcher
print(fetcher.fetch(sys.argv[1]))
untouched = ssl._create_default_https_context is ssl.create_default_context
print("GLOBAL_OK" if untouched else "GLOBAL_PATCHED")
"""


class HelloHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = BODY.encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return None


@pytest.fixture(scope="session")
def proxy_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    folder = tmp_path_factory.mktemp("cert")
    cert, key = folder / "cert.pem", folder / "key.pem"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1"]
        + ["-keyout", str(key), "-out", str(cert), "-subj", "/CN=campus-proxy"],
        check=True,
        capture_output=True,
    )
    server = http.server.HTTPServer(("127.0.0.1", 0), HelloHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"https://localhost:{server.server_address[1]}/"
    server.shutdown()


def run_fetch(url: str, on_campus: bool) -> subprocess.CompletedProcess[str]:
    """Call fetcher.fetch in a fresh process, with or without CAMPUS_PROXY=1."""
    env = {key: value for key, value in os.environ.items() if key != "CAMPUS_PROXY"}
    env["PYTHONPATH"] = "/app"
    if on_campus:
        env["CAMPUS_PROXY"] = "1"
    return subprocess.run(
        [sys.executable, "-c", FETCH_SCRIPT, url],
        cwd="/app",
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
