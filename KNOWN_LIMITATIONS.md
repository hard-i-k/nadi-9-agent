# Known Limitations

## Intentionally Left Incomplete

1. **Real LLM integration**: The `AnthropicProvider` and `OpenAIProvider` are stubs. The project is designed to run entirely in mock mode for evaluation. Integrating a real provider would require adding API key management, retry logic with exponential backoff, and rate limiting.

2. **Audio transcription**: The `TranscriptionProvider` interface exists but the mock simply reads pre-made transcript files. Real audio processing would require Whisper or similar.

3. **Morphological analysis**: The vocabulary checker uses simple string matching. A real Nadi-9 system would need proper tokenization, stemming, and affix analysis.

4. **Grammar verification depth**: Grammar checks look for specific markers (e.g., `-va` for past tense) but don't perform full syntactic parsing. Complex grammatical constructions would be missed.

## Known Weaknesses

5. **Conflict resolution**: The system detects dictionary conflicts and flags them for human review, but has no automated conflict resolution strategy.

6. **Context window**: The translator processes lines independently within a scene. Cross-scene references and callbacks are not tracked.

7. **Humor and wordplay**: These are flagged as high-risk but the system has no special handling — they are always escalated to human review.

8. **The rule tester uses pattern matching**: In production, rules should be tested by attempting to apply them to generate translations and comparing against approved examples.

## Design Decisions

9. **Conservative by design**: The system prefers HUMAN_REVIEW over AUTO_APPROVE when in doubt. This means the review queue may be larger than necessary, but no invented translations slip through.

10. **Budget allocation is simple**: Risk-based ordering is a heuristic. A more sophisticated system could use bandit algorithms to allocate budget dynamically.
