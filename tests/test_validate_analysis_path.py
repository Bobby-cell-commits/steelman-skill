"""Unit tests for the Mode-A analysis-path denylist (security bundle).

The steelman skill runs against a live-key repo. When invoked as `/steelman <path>`,
the path is attacker-influenceable (it can come from conversation context). The
validator refuses to read sensitive files (~/.ssh, .env*, settings.local.json),
symlinks (escape vector), and anything resolving outside the project root.
Pattern: pathlib.resolve + denylist checks.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_analysis_path import validate  # noqa: E402


def _root(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    (root / "NOTES.md").write_text("# notes\n")
    (root / "analysis.md").write_text("# analysis\n")
    (root / ".env").write_text("API_KEY=sk-secret\n")
    (root / ".env.local").write_text("X=1\n")
    (root / "settings.local.json").write_text("{}\n")
    sub = root / ".claude"
    sub.mkdir()
    (sub / "settings.local.json").write_text("{}\n")
    return root


def test_allows_in_project_markdown(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate(str(root / "analysis.md"), str(root))
    assert ok, reason


def test_denies_env_file(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate(str(root / ".env"), str(root))
    assert not ok and "env" in reason.lower()


def test_denies_env_dotted_variant(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate(str(root / ".env.local"), str(root))
    assert not ok


def test_denies_settings_local_at_root(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate(str(root / "settings.local.json"), str(root))
    assert not ok


def test_denies_settings_local_nested(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate(str(root / ".claude" / "settings.local.json"), str(root))
    assert not ok


def test_denies_ssh_path(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate("~/.ssh/id_rsa", str(root))
    assert not ok and "ssh" in reason.lower()


def test_denies_escape_project_root(tmp_path):
    root = _root(tmp_path)
    ok, reason = validate(str(root / ".." / ".." / "etc" / "passwd"), str(root))
    assert not ok and ("outside" in reason.lower() or "escape" in reason.lower())


def test_denies_symlink(tmp_path):
    root = _root(tmp_path)
    target = tmp_path / "outside.md"
    target.write_text("x")
    link = root / "link.md"
    link.symlink_to(target)
    ok, reason = validate(str(link), str(root))
    assert not ok and "symlink" in reason.lower()
