# Steelman Examples

Three annotated examples from a real steelmanning session. Study the patterns,
not the specific content — these illustrate GOOD critique, BAD critique
(tinmanning), and GOOD critique that confirms with caveats.

---

## Example 1: Good Critique — Rank Inversion

**Original recommendation:** Custom subagents (`.claude/agents/`) — Tier 1 #2
**Original argument:** "Custom agents carry domain knowledge across sessions,
reducing context re-gathering. The frontmatter system supports specialized
agents for testing, review, and deployment."

**Investigation found:**
- `.claude/agents/` directory exists but is EMPTY
- Project has completed 81 GSD plans without ever creating a custom agent
- GSD framework already provides agent infrastructure (gsd-executor,
  gsd-verifier, gsd-planner, etc.)
- No mention of agent-related friction in MEMORY.md

**Tests applied:**
- Test #1 (Real vs Hypothetical): **FAIL** — No evidence of friction from lack
  of custom agents. 81 plans completed successfully without them.
- Test #2 (Already Solved): **FAIL** — GSD provides domain-specific agents
  already (executor, verifier, planner, debugger, researcher).
- Test #6 (Daily vs Rare): **FAIL** — Zero usage after months. **Note:** zero
  usage *alone* would be INCONCLUSIVE (absence of adoption ≠ proven non-need), but
  here it is corroborated by the completed-work evidence above, which makes it a
  demonstrated non-need rather than mere non-adoption.

**Verdict:** Tier 1 #2 → **Tier 3 (Skip)**

**Why this is GOOD critique:** Every counterargument cites specific discovered
evidence (empty directory, 81 plans, existing GSD agents). The investigation
brought NEW information that directly contradicted the original claim. Crucially,
the empty directory is NOT read as a hard FAIL *on its own* — it's the
*corroborating* evidence (81 completed plans, an existing GSD agent system) that
turns "unused" into "demonstrably not needed." A bare empty directory with no such
corroboration would be **INCONCLUSIVE**, not Skip (see rubric: zero-usage is
INCONCLUSIVE by default).

---

## Example 2: Bad Critique — Tinmanning (DO NOT DO THIS)

**Original recommendation:** `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` env var
**Hypothetical bad steelman response:**

> "While this env var addresses cwd-reset friction, there are concerns:
> - It might interfere with scripts that expect specific working directories
> - The feature is relatively new and may have undiscovered bugs
> - Users should learn to use absolute paths instead of relying on env vars
> - It could mask deeper issues with project configuration"

**Why this is BAD (tinmanning):**
1. "Might interfere" — speculation, no evidence of actual interference found
2. "May have undiscovered bugs" — unfalsifiable; applies to literally anything
3. "Should learn absolute paths" — prescriptive judgment, not evidence-based
4. "Could mask deeper issues" — vague concern with no specific issue identified

**None of these counterarguments cite discovered evidence.** They are generic
objections that could be copy-pasted onto any recommendation. This is
TINMANNING — manufacturing weak objections that look like critique but add no
information.

**What a GOOD critique would look like for this claim:**
The investigation found that MEMORY.md documents cwd-reset as recurring
friction, and no existing workaround fully addresses it. The env var is a
single-line change solving documented daily friction. **The correct verdict
is CONFIRMED — investigation validates the recommendation.**

A steelman that finds no problems with a recommendation is a validated
analysis, not a failed steelman.

---

## Example 3: Good Critique — Confirm with Caveats

**Original recommendation:** Sandboxing (`/sandbox`) — Tier 1 #5
**Original argument:** "Sandboxing reduces permission friction by replacing
individual allow rules with a sandbox that permits all operations within
defined boundaries."

**Investigation found:**
- `settings.local.json` contains 85 individual permission allow rules
  (real friction — significant user investment in managing permissions)
- Sandboxing could potentially replace all 85 rules (genuine value)
- BUT: Sandboxing uses `bubblewrap` on Linux, which runs via the same
  WSL routing layer that already causes hook failures on Windows
- No community reports of sandboxing working on Windows/WSL hybrid setups
- The user's documented hook workaround (PowerShell wrapper) suggests
  WSL-dependent features are risky in this environment

**Tests applied:**
- Test #1 (Real vs Hypothetical): **PASS** — 85 allow rules is documented,
  real friction
- Test #2 (Already Solved): **PARTIAL** — 85 rules work but are high-maintenance
- Test #3 (Works as Advertised): **INCONCLUSIVE** — no data for Windows/WSL
- Test #4 (Platform Risks): **FAIL** — bubblewrap + WSL = same routing issue
  that breaks hooks

**Verdict:** Tier 1 #5 → **Tier 1.5 (Spike First)**

The recommendation has genuine value (85 rules is real friction), but the
platform risk is unresolved. The correct action is a 30-minute spike to test
compatibility, not full commitment.

**Why this is GOOD critique:** It doesn't kill the recommendation — it
calibrates it. The evidence supports BOTH the value (85 rules = real friction)
AND the risk (WSL platform concerns). The verdict matches the evidence:
worth testing, not worth committing to blindly.

---

## Example 4: Good Critique — Runtime-Only, Routed to a Probe

**Original recommendation:** Consolidate the 12-cell CI ingest matrix into one
sequential bash loop to cut billed minutes — Tier 1 #1.
**Original argument:** "GitHub rounds each matrix cell up to a whole minute; the
12 cells bill ~12 min for ~3-4 min of real compute. A sequential loop bills one
rounded minute — ~8-9 wasted billed min/run recovered."

**Investigation found:**
- GitHub billing docs confirm per-cell round-up — a check ran.
- Instrumented run: cells finish 10-25s each *in parallel*; ~3-4 min summed compute.
- The 12 sources are independent (no cross-cell dependency) — a check ran.
- BUT the sequential loop's actual wall-clock — once each source's network/HTTP
  wait, currently overlapped across parallel cells, becomes additive — was never
  run or timed.

**Classification + verdict:**
- Rounding-waste claim → `groundable-now` → **CONFIRMED** (docs + measurement).
- Source independence → `groundable-now` → **CONFIRMED**.
- The decision-relevant claim — "the loop bills ~3-4 min, saving ~8-9" — is
  `runtime-only`: net billed minutes depend on serial wall-clock under real I/O,
  which only a run reveals. → **NEEDS PROBE.** A correct rounding spreadsheet does
  not settle the net once the loop runs.

**Verdict:** Tier 1 #1 → **Probe (runtime-only)** — *not* Strong (ceiling rule: a
runtime-only hinge cannot be Strong). Run the loop once as a canary, read the
actual billed minutes, then ship.

**Why this is GOOD critique:** it doesn't refute the idea — the arithmetic is
right and confirmed. It catches that the *bottom line* is a runtime quantity the
investigation couldn't ground, and routes it to the cheap probe that can, instead
of blessing the sound-looking math. (This is a real production miss that
motivated the runtime-only carve-out: the canary later timed out at 20 min, serial
wall-clock having erased the saving — exactly what a pre-execution CONFIRM missed.)

---

## Pattern Summary

| Pattern | Signal | Example |
|---------|--------|---------|
| **Good critique** | Every counter cites specific evidence | Empty dir, 81 plans, existing tools |
| **Tinmanning** | Counters use "might", "could", "may" without evidence | "Might interfere", "may have bugs" |
| **Confirm with caveats** | Evidence supports BOTH value and risk | 85 rules (value) + WSL risk (caveat) |
| **Validated analysis** | Investigation confirms original claim | Env var solving documented friction |

**The goal is accuracy, not contrarianism.** Some recommendations deserve to be
confirmed. Some deserve to be killed. Most deserve calibration — the evidence
tells you which.
