# Steelman

**A Claude Code skill that challenges AI recommendations against empirical evidence.**

When an LLM produces an analysis and then you ask it to review that analysis, you have the same system evaluating its own output. The model has access to its own reasoning, its own framing, its own confidence -- and unsurprisingly, it tends to agree with itself. Even when prompted to "be critical," the result is usually superficial objections that don't challenge the underlying conclusions. The model is working from the same information it used to form the opinion in the first place.

Steelman breaks this by **not letting the model argue with itself.** Instead of reviewing the analysis through reasoning alone, it forces the model to go read the actual data -- your files, your git history, your configs, external documentation -- and form conclusions from what it finds there. The investigation agents don't see the original analysis's reasoning; they see the claims and go check whether the evidence supports them.

This is a structural solution, not a prompting trick. The skill includes specific guardrails to prevent the model from falling back into self-agreement:

## How It Prevents Self-Agreement

**The core problem:** When you ask an LLM to critique its own output, it has an inherent bias toward confirming what it already said. "Challenge this" prompts produce what looks like critical thinking but is actually the model generating plausible-sounding objections while preserving its original conclusions.

**How steelman avoids this:**

1. **Evidence over reasoning.** The skill's #1 rule: a discovered fact beats a logical argument. The investigation agents must find things in your environment -- empty directories, git patterns, existing configs, documented pain points -- not construct arguments for or against a claim. If no evidence is found, the verdict is "insufficient data," not a reasoned opinion.

2. **Pre-calibration lock.** Before any investigation begins, the model records its confidence in each claim. This snapshot is immutable -- it cannot be revised after the evidence comes in. The pre/post comparison exposes when the model's confidence shifted without new supporting evidence, which is the primary signal of sycophantic drift.

3. **Anti-tinmanning rule.** Every counterargument must cite specific discovered evidence. The skill explicitly names and rejects the failure mode: generic objections like "might interfere," "could have bugs," or "may not scale" that sound critical but carry no information. The examples file includes a side-by-side comparison of real critique vs tinmanning so the model has a concrete pattern to follow.

4. **Single investigation cycle.** No iteration. The model investigates once, reports what it found, and stops. Research shows calibration degrades with each self-refinement pass ([Madaan et al., NeurIPS 2023](https://arxiv.org/abs/2303.17651)) -- repeated review cycles let the model gradually talk itself back into its original position.

5. **Counterargument cap (2-3 per claim).** More counterarguments doesn't mean better critique -- it means the model is padding. Above 3, persuasiveness drops and the signal-to-noise ratio collapses ([Sanna et al., 2002](https://doi.org/10.1177/0146167202281009)).

6. **Confirmation is a valid outcome.** The skill explicitly states that finding no problems is a "validated analysis, not a failed steelman." This removes the implicit pressure to manufacture disagreement. If the evidence supports the original recommendation, the skill says so -- contrarianism without evidence is scored as a failure mode.

## What It Does

After Claude produces a multi-option analysis or recommendation ranking, `/steelman` runs a structured counter-investigation:

1. **Extracts testable claims** from the analysis (5-7 max)
2. **Records pre-investigation confidence** (immutable -- cannot be revised after)
3. **Launches 3 parallel investigation agents:**
   - **Environment** -- checks your configs, settings, and existing workarounds
   - **Historical** -- examines git log, commit patterns, and simpler alternatives
   - **External** -- verifies claims against docs, changelogs, and known issues
4. **Applies 6 critical tests** per claim (see below)
5. **Produces a revised ranking** with honest verdicts: Confirmed, Weakened, Refuted, or Insufficient Data
6. **Flags confidence drift** -- if confidence rose without new evidence, that's the signal

## The 6 Critical Tests

| Test | Question | Diagnosticity |
|------|----------|---------------|
| **Real vs Hypothetical** | Has the user actually experienced this friction? | HIGH |
| **Already Solved** | Does a working solution already exist? | HIGH |
| **Works as Advertised** | Does the tool actually do what the analysis claims? | MEDIUM |
| **Platform Risks** | Will this work in the user's specific environment? | MEDIUM |
| **Boring Alternatives** | Is there a simpler solution that was overlooked? | HIGH (generative) |
| **Daily vs Rare** | How often would the user actually benefit? | LOW (priority adj.) |

## Real Example

Claude analyzed a set of Claude Code optimizations and ranked "Custom Subagents" as Tier 1 priority #2, arguing they'd "carry domain knowledge across sessions."

`/steelman` investigated and found:
- The `.claude/agents/` directory existed but was **completely empty**
- The project had completed **81 GSD plans** without ever creating a custom agent
- The existing framework already provided 6 specialized agents
- Zero mentions of agent-related friction in project memory

**Verdict: Tier 1 #2 --> Tier 3 (Skip).** The recommendation solved a problem that didn't exist.

Meanwhile, a boring env var (`CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`) that the analysis ranked lower was *confirmed* -- it solved documented daily friction with a single-line change.

## Anti-Tinmanning

The skill enforces a strict rule: **every counterargument must cite specific discovered evidence.** Generic objections like "might interfere" or "may have bugs" are explicitly flagged and rejected. This prevents the opposite failure mode -- manufacturing weak objections that look like critical thinking but add no information.

A steelman that finds no problems is a **validated analysis**, not a failed steelman.

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
- Per-claim verdicts with evidence
- Pre/post calibration shift
- Missed alternatives
- Revised ranking with honest assessments
- Plain-language summary ("So What Does This Actually Mean?")

Full detailed report is saved to `/tmp/steelman/detailed-report.md`.

## Structure

```
steelman/
  SKILL.md                          # Main skill definition (Claude Code reads this)
  references/
    rubric.md                       # 6 critical tests with scoring criteria
    investigation-targets.md        # Discovery checklist for evidence gathering
    examples.md                     # 3 annotated examples (good critique, tinmanning, confirm-with-caveats)
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI, desktop app, or IDE extension)
- Works with any Claude model (Opus recommended for investigation depth)

## License

MIT
