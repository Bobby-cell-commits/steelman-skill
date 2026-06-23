#!/usr/bin/env python3
"""Mode-A analysis-path denylist for the steelman skill (security bundle).

`/steelman <path>` reads an arbitrary file as the analysis to challenge. Because
steelman runs against a live-key repo and the path can originate from
conversation context, the path is validated BEFORE it is read. Refuses:

  - sensitive files: ~/.ssh/**, .env / .env.* , settings.local.json (any dir)
  - symlinks (a classic allowlist-escape vector)
  - any path that resolves OUTSIDE the project root

Pure functions (`validate`) + a thin CLI. Pattern: pathlib resolve + denylist
checks. Exit 0 = allowed; exit 2 = denied (reason on stdout).
"""
from __future__ import annotations

import pathlib
import sys

# Basenames that are never a valid analysis input, even inside the project root.
_DENY_BASENAMES = {"settings.local.json"}


def _denylist_reason(resolved: pathlib.Path) -> str | None:
    """Return a denial reason if the resolved path hits a sensitive pattern, else None."""
    parts = [p.lower() for p in resolved.parts]
    name = resolved.name.lower()

    if ".ssh" in parts:
        return "path is under an .ssh directory (private keys)"
    if name == ".env" or name.startswith(".env."):
        return "path is a .env file (secrets)"
    if name in _DENY_BASENAMES:
        return f"path is a {resolved.name} file (local settings / secrets)"
    return None


def validate(path_str: str, project_root: str) -> tuple[bool, str]:
    """Validate that `path_str` is a safe analysis file inside `project_root`.

    Returns (allowed, reason). `allowed` is False with a human-readable reason
    when the path is sensitive, a symlink, or escapes the project root.
    """
    raw = pathlib.Path(path_str).expanduser()
    root = pathlib.Path(project_root).expanduser().resolve()

    # Symlink check must run on the un-resolved path (resolve() follows links and
    # would hide an escape). Check the final component AND any existing parent.
    probe = raw
    seen = set()
    while True:
        if probe.is_symlink():
            return False, f"path component is a symlink ({probe}); symlinks are refused"
        if probe == probe.parent or str(probe) in seen:
            break
        seen.add(str(probe))
        probe = probe.parent

    resolved = raw.resolve()

    reason = _denylist_reason(resolved)
    if reason:
        return False, reason

    if not (resolved == root or root in resolved.parents):
        return False, f"path resolves outside the project root ({resolved} not under {root})"

    return True, str(resolved)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_analysis_path.py <path> [project_root]", file=sys.stderr)
        return 2
    path_str = argv[1]
    project_root = argv[2] if len(argv) > 2 else str(pathlib.Path.cwd())
    allowed, reason = validate(path_str, project_root)
    print(("OK: " if allowed else "DENIED: ") + reason)
    return 0 if allowed else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
