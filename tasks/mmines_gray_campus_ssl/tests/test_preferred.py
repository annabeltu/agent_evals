"""Full credit: off campus, certificates are still verified."""

from conftest import BODY, run_fetch


def test_off_campus_still_rejects_untrusted_certificates(proxy_url: str) -> None:
    # Only the outcome is checked, so a solution that wraps the SSL error in its
    # own exception message still gets credit.
    result = run_fetch(proxy_url, on_campus=False)

    assert result.returncode != 0
    assert BODY not in result.stdout
