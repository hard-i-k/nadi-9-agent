# Architecture

## Planning
The planner uses heuristics to identify risky lines (humor, kinship terms, etc.) and prioritizes them to maximize value before the budget runs out.

## Memory
State is modeled as Pydantic objects. The dependency graph links evidence and rules to specific subtitles, allowing targeted replanning.

## Verification
A deterministic verifier (timing, omissions) acts first. 
An independent LLM check is intended to catch translation errors, isolating generation from verification.

## Failure Recovery
The pipeline degrades gracefully:
- If a budget limit is reached, it marks the remaining as `NOT_PROCESSED_BUDGET`.
- If prompt injection is found, the data is quarantined.

## Trust Boundaries
Any loaded text from evidence files is UNTRUSTED. The sanitizer inspects it, and when sent to the LLM, it is wrapped in delimiters.

## Scaling
To scale to 5,000 episodes x 40 dialects, we use batch processing and strict budgets. The mock provider allows parallel offline evaluations.

## What Fails First
The simple regex-based verification would fail for complex morphological rules.
