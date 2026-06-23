#!/usr/bin/env python3
"""Secret redaction for steelman evidence excerpts (security bundle).

Before any evidence excerpt gathered during investigation is surfaced to the
transcript, it is run through `redact` so leaked credentials are masked to
NAMES + COUNTS ONLY — the secret value never reaches the conversation.

The high-entropy token patterns are battle-tested against scraped content and are
inlined here (rather than imported) so this global skill stays self-contained and
portable. A generic key/token/password ASSIGNMENT pattern is added on top to
catch `API_KEY=...` / `password: ...` style leaks while preserving the label.

Pure function + thin CLI: reads stdin, writes redacted text to stdout, and a
`# redacted: {...}` summary line to stderr.
"""
from __future__ import annotations

import re
import sys

# (name, pattern) — whole match is replaced with the placeholder.
_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("private_key", re.compile(r"-----BEGIN[^-]*PRIVATE KEY-----.*?-----END[^-]*PRIVATE KEY-----", re.DOTALL)),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),          # OpenAI-style
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),  # GitHub tokens
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),                 # AWS access key id
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")), # Slack
]

# Generic assignment: redact the VALUE, keep the label (group 1) + separator (group 2).
_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|bearer)\b(\s*[:=]\s*['\"]?)([A-Za-z0-9._\-/+]{8,})"
)

_PLACEHOLDER = "[REDACTED-SECRET]"


def redact(text: str) -> tuple[str, dict[str, int]]:
    """Return (cleaned_text, summary) where summary maps pattern-name -> count.

    The summary carries names and counts only — never the redacted value — so it
    is safe to surface alongside the cleaned text.
    """
    summary: dict[str, int] = {}

    for name, pat in _SECRET_PATTERNS:
        text, n = pat.subn(_PLACEHOLDER, text)
        if n:
            summary[name] = summary.get(name, 0) + n

    def _repl(m: re.Match) -> str:
        return m.group(1) + m.group(2) + _PLACEHOLDER

    text, n = _ASSIGNMENT_RE.subn(_repl, text)
    if n:
        summary["assignment"] = summary.get("assignment", 0) + n

    return text, summary


def main() -> int:
    data = sys.stdin.read()
    cleaned, summary = redact(data)
    sys.stdout.write(cleaned)
    if summary:
        sys.stderr.write(f"# redacted: {summary}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
