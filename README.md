# Steelman

**A Claude Code skill that challenges AI recommendations against empirical evidence.**

When an LLM produces an analysis and then you ask it to review that analysis, you have the same system evaluating its own output. The model has access to its own reasoning, its own framing, its own confidence -- and unsurprisingly, it tends to agree with itself. Even when prompted to "be critical," the result is usually superficial objections that don't challenge the underlying conclusions. The model is working from the same information it used to form the opinion in the first place.

Steelman breaks this by **not letting the model argue with itself.** Instead of reviewing the analysis through reasoning alone, it forces the model to go read the actual data -- your files, your git history, your configs, external documentation -- and form conclusions from what it finds there. Investigation agents receive only the extracted claims (no reasoning, no supporting arguments from the original analysis), so they must derive verdicts from what they discover, not from what the original analysis argued.

This is a structural solution, not a prompting trick. The skill includes specific guardrails to prevent the model from falling back into self-agreement:

## How It Prevents Self-Agreement

**The core problem:** When you ask an LLM to critique its own output, it has an inherent bias toward confirming what it already said. "Challenge this" prompts produce what looks like critical thinking but is actually the model generating plausible-sounding objections while preserving its original conclusions.

**How steelman avoids this:**

1. **Evidence over reasoning.** The skill's #1 rule: a discovered fact beats a logical argument. The investigation agents must find things in your environment -- empty directories, git patterns, existing configs, documented pain points -- not construct arguments for or against a claim. If no evidence is found, the verdict is "insufficient data," not a reasoned opinion.

2. **Pre-calibration lock.** Before any investigation begins, the model records its confidence in each claim and writes it to disk. This snapshot is immutable -- the file is re-read verbatim for the final comparison, so the model cannot retroactively revise it. The pre/post comparison exposes when the model's confidence shifted without new supporting evidence.

3. **Anti-tinmanning rule.** Every counterargument must cite a specific file:line or URL discovered during investigation. The skill explicitly names and rejects the failure mode: generic objections like "might interfere," "could have bugs," or "may not scale" that carry no information. The examples file includes a side-by-side comparison of real critique vs tinmanning.

4. **Single verdict cycle.** No re-reasoning after verdicts are produced. The model investigates once, synthesizes once, and stops. Research on self-refinement suggests that iterating on already-reached conclusions tends to drift back toward the original position rather than improving calibration.

5. **Counterargument cap (2-3 per claim).** More counterarguments doesn't mean better critique -- it means the model is padding. A small number of high-quality, evidence-backed counterarguments outperforms a long list of speculative ones.

6. **Confirmation is a valid outcome.** The skill explicitly states that finding no problems is a "validated analysis, not a failed steelman." This removes the implicit pressure to manufacture disagreement. If the evidence supports the original recommendation, the skill says so -- contrarianism without evidence is scored as a failure mode, same as sycophancy.

7. **Bilateral drift detection.** Both directions of miscalibration are flagged: confidence rising without evidence (sycophancy) and confidence falling without disconfirming evidence (contrarianism/tinmanning).

8. **Runtime-only honesty.** A claim is marked *Confirmed* only when an actual check grounded it — a file read, a query run, a measurement taken. Claims whose truth only emerges once the change runs under real load (net cost, latency under burst, "will the canary pass") are classified `runtime-only` and routed to a probe with a **Needs Probe** verdict, never a confident confirm. This stops the skill from blessing sound-looking arguments whose bottom line it could not actually test.

## What It Does

After Claude produces a multi-option analysis or recommendation ranking, `/steelman` runs a structured counter-investigation:

1. **Extracts testable claims** from the analysis (one per top-level recommendation, up to 10)
2. **Records pre-investigation confidence** (written to disk — cannot be revised after)
3. **Launches 3 parallel investigation agents** specialized by data source:
   - **Filesystem & Config** -- checks your settings, configs, and existing workarounds
   - **Git History** -- examines commit patterns, churn, and simpler alternatives
   - **External Docs** -- verifies claims against documentation and known issues (domain-allowlisted)
4. **Applies 6 critical tests** per claim (see below)
5. **Produces a revised ranking** with honest verdicts: Confirmed, Plausible–Unverified, Weakened, Refuted, Needs Probe, or Insufficient Data
6. **Flags confidence drift** -- in both directions, with evidence required to justify any shift

## The 6 Critical Tests

| Test | Question | Diagnosticity |
|------|----------|---------------|
| **Real vs Hypothetical** | Has the user actually experienced this friction (documented or detectable)? | HIGH |
| **Already Solved** | Does a working solution already exist? | HIGH |
| **Works as Advertised** | Does the tool actually do what the analysis claims? | MEDIUM |
| **Platform Risks** | Will this work in the user's specific environment? | MEDIUM |
| **Boring Alternatives** | Is there a simpler solution that was overlooked? | HIGH (generative) |
| **Daily vs Rare** | How often would the user actually benefit? | LOW (priority adj.) |

## Real Example

Claude analyzed a set of Claude Code optimizations and ranked "Custom Subagents" as Tier 1 priority #2, arguing they'd "carry domain knowledge across sessions."

`/steelman` investigated and found:
- The `.claude/agents/` directory existed but was **completely empty**
- The project had completed **81 plans** without ever creating a custom agent
- The existing framework already provided 6 specialized agents
- Zero mentions of agent-related friction in project memory

**Verdict: Tier 1 #2 → Tier 3 (Skip).** Test #2 (Already Solved) was a genuine FAIL backed by positive evidence (the existing agents). The other tests came back INCONCLUSIVE — not enough to downgrade on their own, but enough to remove the recommendation's supporting argument.

Meanwhile, a boring env var (`CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`) that the analysis ranked lower was *confirmed* -- it solved documented daily friction with a single-line change.

## Anti-Tinmanning

The skill enforces a strict rule: **every counterargument must cite a specific discovered evidence location** (file:line or URL). Generic objections like "might interfere" or "may have bugs" are explicitly flagged and rejected. This prevents the opposite failure mode -- manufacturing weak objections that look like critical thinking but add no information.

A steelman that finds no problems is a **validated analysis**, not a failed steelman.

## Changelog

### v2 — June 2026
Builds on jb-machemie's v1.1 review. Major additions:
- **Runtime-only vs groundable-now** claim classification → `Needs Probe` verdicts and a `Plausible — Unverified` gate, so the skill confirms only what a check actually grounded.
- **Hinge-claim lens** — surfaces the single load-bearing claim whose failure collapses the whole recommendation, and weights investigation toward it.
- **Strong-ceiling rule** — a recommendation can't be ranked *Strong* if its load-bearing claim was never grounded by a check that ran.
- jb-machemie's security rules shipped as **executable scripts** (`scripts/`): Mode-A path validation, per-run `0700` run-dir, secret redaction — each with unit tests (`tests/`, 20 passing).
- Investigation guide gains a **high-yield empirical-checks** section; rubric gains PARTIAL scoring and a citation gate.

### v1.1 — April 2026 (@jb-machemie)
A 30-point security / architecture / effectiveness review: claims-only subagent isolation, a persisted pre-calibration lock, bilateral drift detection, the `<ANALYSIS_DATA>` data fence, secret-redaction + domain-allowlist + injection rules, a 200KB input limit, PARTIAL / zero-usage→INCONCLUSIVE scoring, and cross-platform (PowerShell / WSL) investigation commands.

### v1.0 — April 2026
Initial release.

## Install

```bash
# Clone into Claude Code's skills directory
git clone https://github.com/Bobby-cell-commits/steelman-skill.git ~/.claude/skills/steelman
```

Restart Claude Code after installing.

## Usage

```
# After Claude produces a multi-option analysis:
/steelman

# Or point it at a file:
/steelman path/to/analysis.md

# Or pass text directly:
/steelman "your analysis text here"
```

The skill runs for 1-3 minutes (parallel agents investigating your environment), then outputs:
- Per-claim verdicts with evidence citations
- Pre/post calibration shift (bilateral — flags drift in both directions)
- Missed alternatives (evidence-backed only)
- Revised ranking with honest assessments
- Plain-language summary ("So What Does This Actually Mean?")

The full detailed matrix is written to a per-invocation private `0700` directory during the run and **removed automatically when the run completes** — the durable verdicts, calibration shift, and revised ranking are surfaced inline in the conversation.

## Structure

```
steelman/
  SKILL.md                          # Main skill definition (Claude Code reads this)
  references/
    rubric.md                       # 6 critical tests with scoring criteria
    investigation-targets.md        # Discovery checklist (Unix + PowerShell)
    examples.md                     # 4 annotated examples (good critique, tinmanning,
                                     #   confirm-with-caveats, runtime-only probe)
  scripts/
    prepare_run_dir.sh              # Per-invocation private 0700 run dir
    validate_analysis_path.py       # Mode-A path denylist (sensitive files, symlinks, root-escape)
    redact_secrets.py               # Masks secrets in evidence excerpts to names + counts
  tests/                            # Unit tests for the scripts (pytest + bash, 20 passing)
```

## Credits

- **[@jb-machemie](https://github.com/jb-machemie)** (Jean-Baptiste) — the v1.1 30-point review that forms the skill's security and architecture backbone. Merged via [#1](https://github.com/Bobby-cell-commits/steelman-skill/pull/1).

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI, desktop app, or IDE extension)
- Works with any Claude model (Opus recommended for investigation depth)
- Python 3 for the `scripts/` (path validation, secret redaction)

## License

MIT
