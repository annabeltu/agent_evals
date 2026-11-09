"""Needed for any credit: fetch works on campus, without a process-wide TLS patch."""

from conftest import BODY, run_fetch


def test_fetch_works_on_campus(proxy_url: str) -> None:
    result = run_fetch(proxy_url, on_campus=True)

    assert result.returncode == 0, result.stderr
    assert BODY in result.stdout


def test_change_stays_inside_fetcher(proxy_url: str) -> None:
    result = run_fetch(proxy_url, on_campus=True)

    assert "GLOBAL_OK" in result.stdout, result.stdout + result.stderr
