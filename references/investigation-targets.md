# Investigation Targets — Discovery Guide

This is a general-purpose checklist for discovering evidence in any project.
Do NOT hardcode paths — discover them dynamically.

## Configuration Discovery

**Goal:** Find what the user has already configured, customized, or worked around.

Search patterns (check both project and user-level):
- `settings*.json`, `config.*`, `.env*`, `*.config.js`, `*.config.ts`
- `.claude/settings.json`, `.claude/settings.local.json`
- `CLAUDE.md`, `.claude/rules/`, `.claude/commands/`
- Package manifests: `package.json`, `pyproject.toml`, `Cargo.toml`
- CI/CD: `.github/workflows/`, `Dockerfile`, `docker-compose*`

**What to look for:**
- Number and nature of custom rules or overrides (high count = high investment)
- Permission configurations (allow lists, deny lists, tool restrictions)
- Hook implementations (what events are handled, what scripts run)
- Environment variables set in project vs user scope

## Usage Pattern Discovery

**Goal:** Determine what the user actually uses vs what exists but is unused.

Signals of active use:
- File modification dates (recently changed = actively used)
- File counts in directories (populated = used, empty = abandoned/not adopted)
- Git blame frequency (files with many recent commits = active development)

Signals of non-use:
- Empty directories (feature created but never populated)
- Skeleton files with only boilerplate content
- Config entries that reference non-existent paths or tools

**Key command:**
```bash
# Find empty directories (signals unused features)
find . -type d -empty -not -path './.git/*' 2>/dev/null

# Find recently modified files (signals active work)
git log --oneline -20 --name-only | grep -v '^[a-f0-9]' | sort | uniq -c | sort -rn | head -20
```

## Pain Point Discovery

**Goal:** Find documented friction, workarounds, and things that broke.

Sources:
- `MEMORY.md` and any topic-specific memory files — persistent pain points
- `FIXME`, `TODO`, `HACK`, `WORKAROUND` comments in code
- Revert commits in git log — things that were tried and undone
- Issue trackers (if accessible) — reported problems

**Key commands:**
```bash
# Search for pain markers in code
grep -rn "FIXME\|TODO\|HACK\|WORKAROUND\|XXX" --include='*.md' --include='*.py' --include='*.ts' --include='*.js' . 2>/dev/null | head -30

# Find revert commits (things that failed)
git log --oneline --all --grep="revert\|Revert\|rollback\|undo" | head -10

# Find commits about fixing/workarounds
git log --oneline -50 --grep="fix\|workaround\|patch\|hotfix" | head -20
```

## Git History Analysis

**Goal:** Understand project trajectory, decision patterns, and development velocity.

**Key commands:**
```bash
# Recent activity (what's being worked on NOW)
git log --oneline -20

# File churn (what changes most = where friction lives)
git log --pretty=format: --name-only -50 | sort | uniq -c | sort -rn | head -15

# Commit frequency (development velocity)
git log --format='%ad' --date=short -50 | uniq -c

# Planning/decision history
ls -la .planning/ 2>/dev/null
ls -la .planning/phases/ 2>/dev/null
```

**What to look for:**
- Files that churn heavily may indicate unresolved design problems
- Long gaps between commits may indicate blockers or context switches
- Planning directories reveal scope of past decisions

## Platform Detection

**Goal:** Determine the user's actual runtime environment for compatibility checks.

**Key commands:**
```bash
# OS and shell
uname -a 2>/dev/null || echo "Windows (no uname)"
echo "SHELL=$SHELL"
echo "TERM=$TERM"

# Runtime versions
node --version 2>/dev/null
python --version 2>/dev/null
```

**What to look for:**
- Windows/WSL hybrid environments (common source of compatibility issues)
- Shell routing (bash on Windows may route to WSL)
- Runtime version constraints that affect feature availability
