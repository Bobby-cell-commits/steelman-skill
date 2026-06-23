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
- Test #1 (Real vs Hypothetical): **INCONCLUSIVE** — No documented friction from
  lack of custom agents; latent signals not found either. Absence of evidence is
  not evidence of absence — but the recommendation carries the burden.
- Test #2 (Already Solved): **FAIL** — GSD provides domain-specific agents
  already (executor, verifier, planner, debugger, researcher). This is positive
  evidence of an existing solution, not merely absence.
- Test #6 (Daily vs Rare): **INCONCLUSIVE** — Zero usage observed, but this
  means the feature was never tried, not that it would never be used.

**Verdict:** Tier 1 #2 → **Tier 3 (Skip)**

**Why this is GOOD critique:** Test #2 is a genuine FAIL backed by positive
evidence — the GSD agents are a real, discovered existing solution. The
INCONCLUSIVE results on Tests #1 and #6 remove the recommendation's supporting
argument (assumed friction + assumed usage) without fabricating disconfirmation.
The verdict stands on the FAIL + absence of supporting evidence, not on invented
objections.

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
  real friction (`settings.local.json:1-85`)
- Test #2 (Already Solved): **PARTIAL** — 85 rules work but are high-maintenance;
  they cover the problem but not cleanly
- Test #3 (Works as Advertised): **INCONCLUSIVE** — no data for Windows/WSL
- Test #4 (Platform Risks): **FAIL** — bubblewrap + WSL = same routing issue
  that breaks hooks (documented in MEMORY.md)

**Verdict:** Tier 1 #5 → **Tier 1.5 (Spike First)**

The recommendation has genuine value (85 rules is real friction), but the
platform risk is unresolved. The correct action is a 30-minute spike to test
compatibility, not full commitment.

**Why this is GOOD critique:** It doesn't kill the recommendation — it
calibrates it. The evidence supports BOTH the value (85 rules = real friction)
AND the risk (WSL platform concerns, MEMORY.md citation). The verdict matches
the evidence: worth testing, not worth committing to blindly.

Note on PARTIAL: Test #2 PARTIAL means the existing solution (85 rules) covers
the problem but with significant maintenance overhead — not a clean solution.
This counts as 0.5 PASS + 0.5 INCONCLUSIVE: the recommendation isn't redundant,
but it's not solving a completely unaddressed gap either.

---

## Pattern Summary

| Pattern | Signal | Example |
|---------|--------|---------|
| **Good critique** | Every counter cites specific evidence | Test #2 FAIL: GSD agents discovered |
| **Tinmanning** | Counters use "might", "could", "may" without evidence | "Might interfere", "may have bugs" |
| **Confirm with caveats** | Evidence supports BOTH value and risk | 85 rules (value) + WSL risk (citation) |
| **Validated analysis** | Investigation confirms original claim | Env var solving documented friction |
| **INCONCLUSIVE** | Absence of evidence, not disconfirmation | Empty dir = never tried, not "won't work" |

**The goal is accuracy, not contrarianism.** Some recommendations deserve to be
confirmed. Some deserve to be killed. Most deserve calibration — the evidence
tells you which.
