# Steelman

**A Claude Code skill that challenges AI recommendations against empirical evidence.**

LLMs are sycophantic by default -- they tend to validate your ideas rather than pressure-test them. Steelman fixes this by launching parallel investigation agents that check claims against your actual environment, git history, and external documentation before you act on them.

## What It Does

After Claude produces a multi-option analysis or recommendation ranking, `/steelman` runs a structured counter-investigation:

1. **Extracts testable claims** from the analysis (5-7 max)
2. **Records pre-investigation confidence** (so you can detect sycophantic drift later)
3. **Launches 3 parallel investigation agents:**
   - **Environment** -- checks your configs, settings, and existing workarounds
   - **Historical** -- examines git log, commit patterns, and simpler alternatives
   - **External** -- verifies claims against docs, changelogs, and known issues
4. **Applies 6 critical tests** per claim (see below)
5. **Produces a revised ranking** with honest verdicts: Confirmed, Weakened, Refuted, or Insufficient Data
6. **Flags confidence drift** -- if confidence rose without new evidence, that's sycophancy

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
git clone https://github.com/bogdanstate/steelman-skill.git ~/.claude/skills/steelman
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

## Why This Exists

AI assistants have a well-documented tendency toward sycophancy -- agreeing with users rather than challenging their assumptions. This is especially dangerous for recommendation-style outputs where the AI produces a ranked list and the user acts on it.

Steelman doesn't try to make Claude "more critical" through prompting alone (that just produces tinmanning -- fake objections). Instead, it forces **empirical investigation**: check the user's actual environment, git history, and external sources before rendering a verdict. Evidence beats reasoning.

The approach is grounded in calibration research:
- Single investigation cycle only -- calibration degrades with iteration ([Madaan et al., NeurIPS 2023](https://arxiv.org/abs/2303.17651))
- Counterarguments capped at 2-3 per claim -- more reduces persuasiveness ([Sanna et al., 2002](https://doi.org/10.1177/0146167202281009))
- Pre/post confidence tracking to detect drift

## License

MIT
