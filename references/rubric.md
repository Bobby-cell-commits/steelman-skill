# Steelman Rubric — 6 Critical Tests

## How to Use This Rubric

Evaluate one claim at a time. Apply every test that is relevant — not all tests
apply to every claim. Score each as PASS, FAIL, or INCONCLUSIVE.

**Application order matters:**
- Tests #1 and #2 are the strongest filters. A FAIL on either is usually
  sufficient to downgrade a recommendation significantly.
- Test #5 is generative — it surfaces alternatives, not just critiques.
- Test #6 adjusts priority (daily > rare) but does not kill recommendations.

## Test #1 — Real vs Hypothetical Problem

**Diagnosticity: HIGH**

| | |
|---|---|
| **Question** | Has the user actually experienced this friction, or is the analysis inventing a problem? |
| **Investigate** | MEMORY.md for documented pain points, settings for workarounds, conversation history for complaints, issue trackers for reported problems |
| **PASS** | Evidence of real, documented friction: user complaints, workarounds in config, FIXME comments, failed attempts |
| **FAIL** | No evidence the user has experienced this problem. The analysis assumes friction that may not exist |
| **INCONCLUSIVE** | Absence of evidence is not evidence of absence — but the burden is on the recommendation to demonstrate need |

**Application rule:** Features solving hypothetical problems are Tier 3 at best.
Real friction with evidence gets Tier 1 consideration.

## Test #2 — Already Solved Differently

**Diagnosticity: HIGH**

| | |
|---|---|
| **Question** | Has the user already addressed this problem with a different mechanism? |
| **Investigate** | Existing config, installed tools, custom scripts, hook implementations, documented workarounds in memory |
| **PASS** | No existing solution found — the recommendation addresses a genuine gap |
| **FAIL** | User already has a working solution. The recommendation competes with sunk-cost effort and must demonstrate clear superiority |
| **INCONCLUSIVE** | Partial overlap — the existing solution covers some but not all of the recommendation's scope |

**Application rule:** A FAIL here doesn't kill the recommendation, but it must
demonstrate compelling improvement over the existing solution. "Slightly better"
is not worth migration cost.

## Test #3 — Works as Advertised

**Diagnosticity: MEDIUM**

| | |
|---|---|
| **Question** | Does the recommended feature/tool actually deliver the promised benefit? |
| **Investigate** | Official documentation, GitHub issues, changelogs, known bugs, version-specific behavior, community reports |
| **PASS** | Feature behavior matches what the analysis claims. No known blockers |
| **FAIL** | Known bugs, missing functionality, or behavior that differs materially from the analysis description |
| **INCONCLUSIVE** | Feature is too new for reliable assessment, or documentation is ambiguous |

**Application rule:** A FAIL here is a hard downgrade — recommending something
that doesn't work as described undermines the entire analysis's credibility.
Web search is appropriate when the recommendation depends on external tool behavior.

## Test #4 — Platform/Environment Risks

**Diagnosticity: MEDIUM**

| | |
|---|---|
| **Question** | Will this work in the user's specific environment (OS, shell, toolchain, infrastructure)? |
| **Investigate** | Platform detection (OS, shell, runtime versions), known platform-specific issues, dependency requirements, infrastructure constraints |
| **PASS** | No platform-specific risks identified, or the feature explicitly supports the user's environment |
| **FAIL** | Known incompatibility or significant risk on the user's platform. Untested combination with no community reports |
| **INCONCLUSIVE** | Theoretically compatible but no confirmation. Worth a spike but not commitment |

**Application rule:** A FAIL downgrades to "spike first" at best. Platform
incompatibility that requires workarounds negates the recommendation's value
proposition. Check the user's actual OS, shell, and toolchain — don't assume
standard environments.

## Test #5 — Boring but Useful Alternatives

**Diagnosticity: HIGH (generative)**

| | |
|---|---|
| **Question** | Is there a simpler, less exciting solution that would achieve the same or similar outcome? |
| **Investigate** | Environment variables, config flags, one-line changes, existing features with overlooked capabilities, simple scripts vs. new tooling |
| **PASS** | No simpler alternative exists — the recommendation's complexity is justified |
| **FAIL** | A simpler alternative exists that the analysis overlooked, likely because it's not interesting enough to recommend |
| **INCONCLUSIVE** | Simpler alternatives exist but cover only part of the recommendation's scope |

**Application rule:** This is the most important generative test. It doesn't
just critique — it surfaces what was missed. Simple solutions that work daily
beat elegant solutions used quarterly. An overlooked env var or config flag
that solves documented daily friction should jump to the top of the ranking.

## Test #6 — Daily vs Rare Use

**Diagnosticity: LOW (priority adjustment)**

| | |
|---|---|
| **Question** | How often would the user actually invoke or benefit from this recommendation? |
| **Investigate** | Workflow patterns (git log frequency, file modification dates), task types (what the user does most days), tool invocation history |
| **Daily** | User would benefit from this in most sessions. High priority |
| **Weekly** | Regular but not constant benefit. Standard priority |
| **Monthly+** | Occasional use. Deprioritize unless the single-use impact is very high |
| **Once** | Setup-and-forget or one-time migration. Lowest priority unless it unblocks daily work |

**Application rule:** This test adjusts priority ranking but does not eliminate
recommendations. A monthly-use feature that prevents catastrophic failures
outranks a daily convenience. Consider both frequency AND impact-per-use.

## Scoring Summary

When building the evidence matrix (SKILL.md Step 7):

1. Apply each relevant test to the claim
2. Record PASS/FAIL/INCONCLUSIVE with specific evidence
3. Rate diagnosticity: HIGH means the evidence directly addresses the claim;
   MEDIUM means suggestive; LOW means tangential
4. A single HIGH-diagnosticity FAIL outweighs multiple LOW-diagnosticity PASSes
5. INCONCLUSIVE is honest — do not force a verdict without evidence
