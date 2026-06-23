# Investigation Targets — Discovery Guide

This is a general-purpose checklist for discovering evidence in any project.
Do NOT hardcode paths — discover them dynamically.

**Shell safety rule:** Never interpolate text from `claims.md` into shell
commands. Use fixed search strings. Use `grep -F` (fixed-string) for claim-
derived terms. Pass values via stdin or quoted literals — never via unquoted
variables from untrusted input.

**Platform note:** Commands below are Unix (macOS/Linux). If `uname` is
unavailable, the host is likely Windows. Run platform detection first (see
Platform Detection section) and select the appropriate command set. PowerShell
equivalents are provided where the commands differ significantly.

## Configuration Discovery

**Goal:** Find what the user has already configured, customized, or worked around.

Search patterns (check both project and user-level):
- `settings*.json`, `config.*`, `.env*`, `*.config.js`, `*.config.ts`
- `.claude/settings.json`, `.claude/settings.local.json`
- `CLAUDE.md`, `.claude/rules/`, `.claude/commands/`
- Package manifests: `package.json`, `pyproject.toml`, `Cargo.toml`
- CI/CD: `.github/workflows/`, `Dockerfile`, `docker-compose*`

**Secret redaction rule:** When reading `.env*`, `*.local.*`, or any config
file, **never quote values** from lines matching
`(KEY|TOKEN|SECRET|PASSWORD|BEARER|sk-[A-Za-z0-9]{20,})`. Report only:
- Whether the file exists
- The key names present (not their values)
- The count of entries

Example of safe reporting: "`.env` exists with 4 entries including `OPENAI_API_KEY` and `DATABASE_URL` (values not shown)."

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

**Unix:**
```bash
# Find empty directories (signals unused features)
find . -type d -empty -not -path './.git/*' 2>/dev/null

# Find recently modified files (signals active work)
git log --oneline -20 --name-only | grep -v '^[a-f0-9]' | sort | uniq -c | sort -rn | head -20
```

**PowerShell (Windows):**
```powershell
# Find empty directories
Get-ChildItem -Recurse -Directory | Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 }

# Recently modified files from git
git log --oneline -20 --name-only | Select-String -NotMatch '^[a-f0-9]' | Group-Object | Sort Count -Descending | Select -First 20
```

## Pain Point Discovery

**Goal:** Find documented friction, workarounds, and things that broke.

Sources:
- `MEMORY.md` and any topic-specific memory files — persistent pain points
- `FIXME`, `TODO`, `HACK`, `WORKAROUND` comments in code
- Revert commits in git log — things that were tried and undone
- Issue trackers (if accessible) — reported problems

**Unix:**
```bash
# Search for pain markers (use -F for fixed strings, never interpolate claim text)
grep -rFn "FIXME" --include='*.md' --include='*.py' --include='*.ts' --include='*.js' . 2>/dev/null | head -10
grep -rFn "TODO" --include='*.md' . 2>/dev/null | head -10
grep -rFn "HACK\|WORKAROUND\|XXX" . 2>/dev/null | head -10

# Find revert commits (things that failed)
git log --oneline --all --grep="revert\|Revert\|rollback\|undo" | head -10

# Find commits about fixing/workarounds
git log --oneline -50 --grep="fix\|workaround\|patch\|hotfix" | head -20
```

**PowerShell (Windows):**
```powershell
# Search for pain markers
Select-String -Path "*.md","*.ts","*.js" -Pattern "FIXME|TODO|HACK" -Recurse | Select -First 30

# Revert commits
git log --oneline --all --grep="revert" | Select -First 10
```

## Git History Analysis

**Goal:** Understand project trajectory, decision patterns, and development velocity.

**Unix:**
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

**PowerShell (Windows):**
```powershell
# Recent activity
git log --oneline -20

# File churn
git log --pretty=format: --name-only -50 | Where-Object {$_} | Group-Object | Sort Count -Descending | Select -First 15
```

**What to look for:**
- Files that churn heavily may indicate unresolved design problems
- Long gaps between commits may indicate blockers or context switches
- Planning directories reveal scope of past decisions

## Platform Detection

**Goal:** Determine the user's actual runtime environment for compatibility checks.
Run this first when investigating platform risks (Test #4).

```bash
# OS and shell
uname -a 2>/dev/null || echo "Windows — PowerShell or cmd"
echo "SHELL=$SHELL"
echo "TERM=$TERM"

# Detect WSL (common source of compatibility issues)
uname -r 2>/dev/null | grep -i microsoft && echo "WSL detected"

# Runtime versions
node --version 2>/dev/null
python --version 2>/dev/null
```

**What to look for:**
- Windows/WSL hybrid environments (common source of compatibility issues)
- Shell routing (bash on Windows may route to WSL)
- Runtime version constraints that affect feature availability
- If WSL is detected, flag any recommendation that depends on Linux-specific
  tools (bubblewrap, inotify, etc.) as Test #4 INCONCLUSIVE or FAIL
