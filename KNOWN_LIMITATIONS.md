# Known Limitations

- The translation logic is mostly mocked for this exercise since a real LLM integration wasn't set up.
- Rule testing currently uses a naive substring approach rather than real semantic parsing or LLM-based verification against examples.
- The dependency graph only captures explicit source IDs from events; in a real system, the translator would need to record every piece of evidence used per line.
- The conflict resolution between dictionaries currently flags issues but lacks a sophisticated resolution merging strategy.
