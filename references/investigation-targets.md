# Investigation Targets — Discovery Guide

This is a general-purpose checklist for discovering evidence in any project.
Do NOT hardcode paths — discover them dynamically.

**Shell safety rule:** Never interpolate text from `claims.md` into shell
commands. Use fixed search strings — `grep -F` (fixed-string) for any claim-
derived term. Pass values via stdin or quoted literals, never as unquoted
variables from untrusted input.

**Platform note:** Commands below are Unix (macOS/Linux). If `uname` is
unavailable the host is likely Windows — run Platform Detection first and select
the matching command set. PowerShell equivalents are given where commands differ
significantly.

## Configuration Discovery

**Goal:** Find what the user has already configured, customized, or worked around.

Search patterns (check both project and user-level):
- `settings*.json`, `config.*`, `.env*`, `*.config.js`, `*.config.ts`
- `.claude/settings.json`, `.claude/settings.local.json`
- `CLAUDE.md`, `.claude/rules/`, `.claude/commands/`
- Package manifests: `package.json`, `pyproject.toml`, `Cargo.toml`
- CI/CD: `.github/workflows/`, `Dockerfile`, `docker-compose*`

**Secret redaction rule:** when reading `.env*`, `*.local.*`, or any config file,
**never quote values** from lines matching
`(KEY|TOKEN|SECRET|PASSWORD|BEARER|sk-[A-Za-z0-9]{20,})`. Report only whether the
file exists, the key *names* present, and the entry count — e.g. *"`.env` exists
with 4 entries including `OPENAI_API_KEY` and `DATABASE_URL` (values not shown)."*

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
# Search for pain markers in code (fixed strings — never interpolate claim text)
grep -rn "FIXME\|TODO\|HACK\|WORKAROUND\|XXX" --include='*.md' --include='*.py' --include='*.ts' --include='*.js' . 2>/dev/null | head -30

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

**Key commands:**
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

## Filter / Threshold / Gate Validation

**Goal:** When the analysis defends a filter, threshold, dedup heuristic, quality
gate, or any rule that drops/keeps items based on input shape, verify against
**live upstream input** — not historical post-gate storage.

**Why this matters:** Storage data is biased toward what survived prior gates.
A new gate's false-positive risk is invisible if you only sample what already
made it through the old gates. The most expensive class of post-ship surprise
is a filter that drops far more than the audit-data predicted, because the
audit was post-filter and the live feed isn't.

**Investigation pattern:**
1. **Identify the upstream source.** Where does the raw input come from?
   (RSS feed URL, API endpoint, user input stream, file watch directory.)
2. **Sample it live.** `curl` the feed, hit the API, generate a fresh batch.
   Get raw entries before any gate runs.
3. **Apply the proposed filter to the live sample.** Measure drop rate.
4. **Compare to the analysis's projected impact.** If divergence is >2×,
   the analysis used the wrong population.
5. **Cite the live-vs-historical comparison** in the verdict for that claim.

**Key commands:**
```bash
# RSS / HTTP feed sample
curl -s "<feed-url>" | head -200

# Pre-gate sample via direct DB query against pipeline_processed (or equivalent)
# — counts what came IN, not just what was kept
supabase db query --linked "SELECT COUNT(*) FILTER (WHERE source LIKE '%-filtered') AS dropped, COUNT(*) FILTER (WHERE source NOT LIKE '%-filtered') AS kept FROM pipeline_processed WHERE feed = '<url>' AND processed_at > now() - interval '7 days';"

# For API gates: replay a recent input batch through the new gate locally
# rather than against post-gate storage
```

**Real example:** A body-length filter for an aggregator-source table was
defended with "28% of stored captures are link-only-or-short." A live fetch
from one of the RSS feeds revealed 24/25 of that day's frontpage entries fall
under the 100-char threshold — the feed publishes title-only by design.
Storage had been showing the LLM-actionability-survivor rate, not the live
upstream rate. The filter was operationally 4× more aggressive than predicted.

**Skip when:** the filter targets internal data with no upstream feed (e.g.,
purely-derived metrics, post-processing classifiers); the analysis is about
correctness of a transform, not selection of inputs.

## High-Yield Empirical Checks

These four checks account for the load-bearing wins seen across real steelman
runs — each one is steelman dragging in a fact the analysis decided without. When
a claim is `groundable-now`, reach for whichever fits before settling a verdict:
a CONFIRMED is only as good as the check behind it.

### 1. Measure the candidate in isolation

**When it pays:** the analysis asserts a perf/quality property of a *specific*
function, query, model, or RPC. Don't reason about it — run it once and read the
number. (Seen in production: a claim about a function's write behavior was settled
by measuring the candidate directly, not by arguing it.)

```bash
# time the actual statement / RPC against real data
EXPLAIN (ANALYZE, BUFFERS) <the query the analysis defends>;   -- psql, \timing on
```

### 2. Hunt interacting background / scheduled jobs

**When it pays:** the analysis proposes a change to a value, table, or job *in
isolation* — but a different scheduled job may write the same surface and undo or
collide with it. Grep the schedulers before trusting "this fixes it." (Seen in
production: a fix looked sound until a **nightly regen job** was found silently
overwriting the exact value it set.)

```bash
# every scheduler that might touch the same surface
grep -rn "cron\|schedule\|setInterval\|pg_cron" .github/workflows/ .
# in-DB scheduled jobs:  SELECT jobname, schedule, command FROM cron.job;
```

### 3. Run a distribution on the real table

**When it pays:** the analysis picks a threshold, cap, or magnitude ("7 days",
"top 20", "0.45"). A one-line aggregate over the *actual* column tells you whether
the number matches the data's shape or was guessed. (Seen in production: a "4 days"
staleness threshold was corrected to 7 by running the real inter-write gap
distribution — conditional writes ≠ nominal cadence.)

```bash
# the gap / value distribution the threshold will gate on
# SELECT percentile_cont(ARRAY[0.5,0.95]) WITHIN GROUP (ORDER BY <col>) FROM <table>;
```

### 4. Read the DEPLOYED call-path, not the spec

**When it pays:** the analysis describes how something "works" from a design doc, a
function name, or an older mental model. The deployed code may blend in a factor
the spec omits. Open the actual file on the actual request path. (Seen in
production: a ranking was reasoned about as a single similarity signal; reading the
deployed code showed prod blends two signals — which changed the whole
recommendation.)

```bash
# find the real callsite, then READ it — don't trust the doc's description
grep -rn "<the function / RPC / constant the analysis names>" --include=*.ts --include=*.py
```

**The through-line:** each check converts a claim from *argued* to *grounded*. If
none of them can settle it — if the truth only emerges when the change runs under
real conditions/load — the claim is `runtime-only`: stop and route it to a probe
(SKILL.md Step 8 `NEEDS PROBE` / Step 11 `Probe (runtime-only)`), do not
manufacture a verdict.
