---
name: steelman
description: >
  Challenge an analysis by investigating the user's actual environment for
  counter-evidence. Use when the user says "steelman this", "challenge your
  analysis", "test these recommendations against reality", or invokes
  /steelman. Applies 6 critical tests, gathers empirical evidence from
  settings/config/history, and produces a revised ranking with honest
  assessments. NOT for simple tasks — use after multi-option analyses
  where the ranking itself is the decision.
disable-model-invocation: false
---

# Steelman

## Frame

A colleague submitted the following analysis for peer review. Your job is to
check their claims against empirical evidence — not to agree, not to
manufacture objections, but to calibrate. The analysis may be largely correct.
It may be largely wrong. You don't know yet.

## Step 1 — Load the Analysis

**Mode A — File path:** If `$ARGUMENTS` contains a file path, read that file as
the analysis to challenge.

**Mode B — Conversation context:** If no file path is given, look through ALL
messages above this skill prompt in the current conversation. Search for the most
recent multi-option analysis, recommendation set, or ranked list. Patterns to match:
- Tiered rankings (Tier 1/2/3, High/Medium/Low)
- Numbered recommendation lists with supporting arguments
- Comparative analyses ("Option A vs Option B", side-by-side tables)
- Feature evaluations with priority ordering
- Review assessments with numbered points or key differences

Extract the full analysis text — include all recommendations, supporting arguments,
comparison tables, and key observations. Do not summarize; preserve the original
claims so they can be tested.

**Mode C — Inline argument:** If `$ARGUMENTS` contains analysis text (not a file
path), use that text directly.

**If no analysis is found in any mode:**

> **No analysis found.** `/steelman` challenges an existing analysis against
> empirical evidence. Either:
> - Run it after producing a multi-option analysis in this conversation
> - Pass a file path: `/steelman path/to/analysis.md`
> - Pass inline text: `/steelman "your analysis text here"`

Then stop.

## Step 1.5 — Persist the Analysis

Write the extracted analysis to a temporary file so investigation subagents can
reference it independently:

```bash
mkdir -p /tmp/steelman
```

Write the analysis to `/tmp/steelman/analysis.md` using the Write tool. Include:
- The full analysis text from Step 1
- Source attribution (file path, or "conversation context")

This file is the single source of truth for all subsequent investigation steps.
Subagents will read this file rather than depending on conversation context.

## Step 2 — Extract Testable Claims

From the analysis, extract **5-7 testable claims** maximum. Each claim is an
implicit assertion that can be checked against reality.

For each claim, also identify the **unstated assumption** — what must be true
for the recommendation to deliver its promised value.

Skip pure judgment calls ("X is elegant") — only extract claims where evidence
could confirm or refute them.

Format:
```
CLAIM 1: [recommendation] → [testable assertion]
  Assumption: [what must be true]
CLAIM 2: ...
```

## Step 3 — Pre-Calibration

**Before any investigation**, record your initial confidence in each claim.
Use epistemic markers, not bare numbers:

- **HIGH** — Strong prior evidence supports this; would be surprised if wrong
- **MEDIUM** — Plausible but untested; could go either way
- **LOW** — Speculative or based on general assumptions, not project-specific evidence

```
PRE-CALIBRATION (recorded before investigation):
  Claim 1: [HIGH/MEDIUM/LOW] — [one-line reasoning]
  Claim 2: ...
```

**This section is immutable.** Do not revise it after investigation begins.
The value is in comparing pre vs post, not in getting the pre-calibration "right."

## Steps 4-7 — Investigation (subagent, not displayed)

Launch a single **orchestrator Agent** that performs all investigation and
evidence evaluation internally. The user does not see this work — only the
results surfaced in later steps.

The orchestrator agent receives:
- The analysis file path: `/tmp/steelman/analysis.md`
- The extracted claims and pre-calibration from Steps 2-3
- The rubric: [references/rubric.md](references/rubric.md)
- The investigation targets guide: [references/investigation-targets.md](references/investigation-targets.md)

The orchestrator should launch **3 parallel sub-agents** internally:

### Agent A — Environment Investigation
Apply **Test #1 (Real vs Hypothetical)** and **Test #2 (Already Solved)**.
- Settings and configuration (what the user already invested in solving)
- Memory and documented pain points (what's broken before, what workarounds exist)
- Unused features and empty directories (what the user chose NOT to use)

### Agent B — Historical Investigation
Apply **Test #5 (Boring Alternatives)** and **Test #6 (Daily vs Rare)**.
- Git log, commit patterns, file churn
- Planning history, completed phases, roadmap direction
- Simpler alternatives the analysis may have overlooked

### Agent C — External Verification
Apply **Test #3 (Works as Advertised)** and **Test #4 (Platform Risks)**.
- Documentation, known issues, changelogs
- Platform compatibility with the user's OS/environment
- Web search when claims depend on external tool behavior

### What the orchestrator produces

After all sub-agents complete, the orchestrator:

1. Combines findings into a unified evidence record organized by claim
2. Builds the **full evidence matrix** (Step 7) — evaluating each claim with
   chain-of-thought, scoring each test, rating diagnosticity, stating at most
   2-3 counterarguments per claim, and determining net assessment
3. Applies the **anti-tinmanning rule**: every counterargument MUST cite specific
   discovered evidence. Speculation dressed as critique is not allowed.
4. Writes the **complete detailed report** to `/tmp/steelman/detailed-report.md`

The orchestrator returns to the main conversation:
- Per-claim verdict: 1-2 sentence summary of what the evidence showed
- Net assessment per claim: CONFIRMED / WEAKENED / REFUTED / INSUFFICIENT DATA
- Any missed alternatives discovered during investigation
- The key evidence citations (not the full matrix, just the decisive findings)

## Step 8 — Verdict Per Claim (displayed)

Using the orchestrator's returned findings, display a **condensed verdict**
for each claim. Keep each to 2-3 lines maximum:

```
Claim 1: [SHORT CLAIM TEXT]
  Verdict: [CONFIRMED/WEAKENED/REFUTED] — [1-2 sentences: what the evidence
  showed and why it matters]

Claim 2: ...
```

This replaces the full evidence matrix in the user-facing output. The detailed
matrix is available in `/tmp/steelman/detailed-report.md` if needed.

## Step 9 — What Changed (displayed)

Show the pre→post calibration shift for each claim:

```
What shifted:
  Claim 1: [HIGH→HIGH] — held up as expected
  Claim 2: [MEDIUM→LOW] — [brief reason, e.g. "no real instances found in project history"]
  ...
```

**Flag any confidence that ROSE without new supporting evidence.** This is the
primary signal of sycophantic drift.

## Step 10 — Missed Alternatives (displayed)

Ask: **What did the original analysis NOT consider?**

Look for:
- Simple solutions overlooked because they're not interesting to recommend
- Existing features or tools that already solve part of the problem
- Environmental factors that change the cost/benefit calculation

Label new recommendations clearly as **NEW**. Keep to 2-3 items max.

## Step 11 — Revised Ranking (displayed)

Produce a comparison table:

```
| Original | Recommendation | Revised | Assessment |
|----------|---------------|---------|------------|
| #1 | [name] | #X | [honest 1-line with key evidence] |
| ... | ... | ... | ... |
| NEW | [missed item] | #X | [why it belongs + caveat] |
```

Assessment uses: **Strong**, **Moderate**, **Weak**, **Spike first**, or **Skip**.

## Step 12 — So What Does This Actually Mean? (displayed)

This is the most important output — written for someone who skipped everything
above. Conversational tone, like explaining to a colleague over coffee.

Rules:
- No jargon: no "diagnosticity", "epistemic markers", "calibration drift"
- No test numbers: don't say "Test #1 FAIL" — say what you found in plain words
- For each claim, say one of:
  - "This holds up — here's why it matters"
  - "This sounded right but doesn't hold up — here's what we found"
  - "This is technically true but doesn't matter in practice"
- End with a concrete **"What to actually do"** list: the 2-4 actions the user
  should take based on the revised analysis
- If the original analysis was mostly right, say so — don't manufacture drama
- Mention that the full detailed report is at `/tmp/steelman/detailed-report.md`
- Keep it under ~300 words

## Rules

1. **One investigation cycle only.** Do not iterate. Calibration degrades with
   iteration (Madaan et al. NeurIPS 2023 — ECE rises with each self-refinement pass).
2. **Evidence over reasoning.** A discovered fact beats a logical argument.
   Prioritize what you found in Steps 4-6 over what you can argue in Step 7.
3. **Cap counterarguments at 2-3 per claim.** More than 3 reduces persuasiveness
   and signals tinmanning (Sanna et al. 2002).
4. **No iteration on calibration.** The pre/post comparison IS the calibration
   mechanism. Do not add a third round.
5. **Confirm when confirmed.** If evidence supports the original analysis, the
   revised ranking should reflect that. Contrarianism without evidence is worse
   than agreement.
