"""Unit tests for evidence secret-redaction (security bundle).

Before any evidence excerpt is surfaced from the investigation, secrets are
redacted to NAMES + COUNTS ONLY (the secret value never reaches the transcript).
Patterns are battle-tested against scraped content + a generic key/token/password
assignment pattern.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from redact_secrets import redact  # noqa: E402


def test_redacts_openai_style_key():
    secret = "sk-" + "a" * 40
    cleaned, summary = redact(f"set OPENAI_API_KEY={secret}")
    assert secret not in cleaned
    assert "[REDACTED-SECRET]" in cleaned
    assert summary  # non-empty


def test_redacts_private_key_block():
    pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIxyz\n-----END RSA PRIVATE KEY-----"
    cleaned, summary = redact(f"my key:\n{pem}")
    assert "PRIVATE KEY" not in cleaned
    assert summary.get("private_key") == 1


def test_redacts_github_token():
    secret = "ghp_" + "b" * 36
    cleaned, summary = redact(f"token {secret}")
    assert secret not in cleaned
    assert summary.get("github_token") == 1


def test_redacts_aws_and_slack():
    cleaned, summary = redact("AKIAABCDEFGHIJKLMNOP and xoxb-12345678901234")
    assert "AKIAABCDEFGHIJKLMNOP" not in cleaned
    assert "xoxb-12345678901234" not in cleaned
    assert summary.get("aws_key") == 1 and summary.get("slack_token") == 1


def test_redacts_generic_assignment_value_keeps_label():
    cleaned, summary = redact('password: "hunter2supersecret"')
    assert "hunter2supersecret" not in cleaned
    assert "password" in cleaned.lower()  # the label survives; only the value is masked
    assert summary.get("assignment") == 1


def test_clean_text_untouched():
    text = "This analysis recommends relocating the scheduled job to a cron trigger."
    cleaned, summary = redact(text)
    assert cleaned == text and summary == {}


def test_summary_is_names_and_counts_only():
    a, b = "a" * 40, "b" * 36
    _, summary = redact(f"sk-{a} and ghp_{b}")
    blob = str(summary)
    assert a not in blob and b not in blob  # never leak the value through findings
    assert all(isinstance(v, int) for v in summary.values())
