# AI Collaboration Log

## What the AI Helped With

- Generated the initial project structure and boilerplate code
- Drafted Pydantic model schemas for evidence items, rules, and subtitle decisions
- Created the mock provider implementation
- Wrote initial test cases
- Generated fixture data for the synthetic Nadi-9 dialect

## What I Rejected or Corrected

- Rejected initial approach that used `dict()` instead of `model_dump()` for Pydantic v2
- Corrected the default_factory for metadata field (was using `list` instead of `dict`)
- Rejected a single monolithic verifier in favor of separate verification modules
- Corrected the evidence ID format to match the assignment specification
- Rejected initial fixture data that was too simple to demonstrate the pipeline

## How Output Was Verified

- All 10 required test cases pass via `pytest tests/ -v`
- The full pipeline runs end-to-end in mock mode: `nadi9 run --data fixtures --provider mock`
- Sample outputs were manually inspected to verify correct JSON structure
- Evidence IDs were checked to ensure traceability from source to final decision
- The review queue was verified to contain focused, specific review questions
