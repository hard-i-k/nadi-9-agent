# Architecture

## Pipeline Overview

The Nadi-9 agent follows a staged pipeline where each stage has typed inputs and outputs:

```
Evidence Inspection → Hypothesis Creation → Hypothesis Testing → Planning → Translation → Verification → Escalation → Reporting
```

## Planning

The `TranslationPlanner` assigns a risk score to each episode line based on:
- Kinship/relationship terms (high risk due to status-dependent meanings)
- Humor and wordplay (high risk, often untranslatable)
- Code-switching (mixed language passages)
- Unknown vocabulary (words not found in any dictionary)
- Ambiguous phrases

Lines are processed in descending risk order so the model budget is spent on the hardest lines first. If budget runs out, remaining easy lines are marked `NOT_PROCESSED_BUDGET` rather than receiving unreliable translations.

The plan is revised when new findings emerge (e.g., a rule is contradicted, a dictionary entry is quarantined).

## Memory

State is stored as structured Pydantic models:
- **Evidence Registry**: All evidence items indexed by ID, with precedence tiers and reliability scores
- **Learned Rules**: Hypothesis rules with status (SUPPORTED/WEAK/CONTRADICTED/UNSUPPORTED), linked to evidence IDs
- **Conflict Records**: Explicit records of disagreements between sources
- **Subtitle Decisions**: Full decision objects with evidence trails
- **Dependency Graph**: Maps evidence/rule IDs to the subtitle lines that depend on them
- **State Snapshots**: Versioned snapshots allow reconstructing what the agent knew at each decision point

## Verification

Verification is **independent from translation** — it uses different code paths and (optionally) a different LLM with a different prompt.

Deterministic checks run first:
1. **Vocabulary support**: Every output token must trace to a dictionary entry or approved example
2. **Grammar support**: Word order, tense markers, negation, respect suffixes match SUPPORTED rules
3. **Names and numbers**: Proper names and numbers from source must appear in output
4. **Omissions**: Output length must be proportional to source (flags dramatic omissions or additions)
5. **Timing**: Duration, reading speed, line length, line count constraints
6. **Injection**: Output must not contain prompt injection artifacts

Then an optional independent LLM checker runs with a DIFFERENT prompt. If it disagrees with the deterministic checks, a "verifier agrees with translator's mistake" warning is raised.

## Failure Recovery

- **Budget exhaustion**: Pipeline stops cleanly, marks remaining lines `NOT_PROCESSED_BUDGET`, still produces the report
- **Model failure**: Catches exceptions, marks affected lines `HUMAN_REVIEW`, falls back to deterministic-only verification
- **Prompt injection**: Sanitizer quarantines the source, logs the event, never passes it as instructions
- **Poisoned data**: Cross-checking against approved examples detects and quarantines unreliable dictionary entries

## Trust Boundaries

All evidence loaded from files is treated as **UNTRUSTED DATA**:
- Sanitizer scans for instruction-like patterns before any content enters the pipeline
- Evidence is wrapped in delimited blocks (`\`\`\`untrusted_data`) when included in LLM prompts
- Quarantined items are never passed to the translator
- The system logs every quarantine event for audit

## Source Precedence

```
Tier 1: Approved examples (highest trust)
Tier 2: Dictionary B (community linguist) / Grammar notes
Tier 3: Expert notes (with disagreements kept visible)
Tier 4: Interviews
Tier 5: Dictionary A (earlier vendor, reliability unknown)
Tier 6: Viewer feedback (hints only)
```

Precedence is configurable and can be dynamically lowered for sources caught with bad entries.

## Scaling to 5,000 Episodes × 40 Dialects

- **Batch processing**: Each episode runs independently with its own budget
- **Shared evidence**: The evidence registry and learned rules are shared across episodes of the same dialect, amortizing the learning cost
- **Parallel execution**: Episodes are embarrassingly parallel
- **Incremental learning**: New approved examples from reviewed episodes feed back into the rule tester
- **What fails first**: The simple pattern-matching verification would need proper morphological analysis for complex dialects. The fixed budget of 25 model calls per episode would need scaling for longer episodes.
