# Nadi-9 Evidence-Grounded Subtitle Agent

An agentic system that learns a fictional dialect (Nadi-9) from limited and conflicting evidence, then produces subtitles without pretending to know more than it does.

## Core Philosophy

- **Abstain over invent**: The system prefers sending a line for human review with a precise question rather than producing a fluent but invented translation.
- **Evidence-grounded**: Every translation decision links back to inspectable evidence IDs.
- **Independent verification**: The verifier is separate from the translator and can disagree.
- **Traceable mistakes**: All decisions, conflicts, and assumptions are logged.

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install the package
pip install -e .
```

## Running

### Full pipeline (mock mode, no API key needed)
```bash
nadi9 run --data fixtures --provider mock --max-model-calls 25 --max-tool-calls 50
```

### With surprise events
```bash
nadi9 run --data fixtures --provider mock --inject-event fixtures/correction_event.json
```

### Apply a correction to an existing run
```bash
nadi9 correct --run sample_run --correction fixtures/correction_event.json
```

### Explain a specific subtitle decision
```bash
nadi9 explain --run sample_run --subtitle S014
```

### Generate report
```bash
nadi9 report --run sample_run
```

## Running Tests

```bash
pytest tests/ -v
```

All 10 required tests cover:
1. Dictionary conflict (A vs B) → HUMAN_REVIEW
2. Unsupported term flagged
3. Correction event re-runs only affected subtitles
4. Tool/model failure → safe degradation
5. Prompt injection quarantined
6. LLM-proposed unsupported rule → UNSUPPORTED
7. Poisoned dictionary entries detected
8. Budget limit enforced (26th call refused)
9. Status-dependent word handling
10. SRT timing validity checks

## Mock Mode

The default `--provider mock` mode uses pre-recorded LLM responses from `fixtures/mock_llm_responses.json`. No API key is needed. All runs are deterministic and reproducible.

## Project Structure

```
submission/
  README.md
  ARCHITECTURE.md
  AI_COLLABORATION.md
  KNOWN_LIMITATIONS.md
  src/nadi9/
    cli.py          - CLI entry point
    config.py       - Configuration and precedence policy
    budget.py       - Budget manager with limits
    providers/      - LLM/transcription provider abstraction
    evidence/       - Evidence loading, registry, sanitization
    memory/         - State, claims, dependency graph
    learning/       - Hypothesis extraction and testing
    translate/      - Planning and translation
    verify/         - Independent verification checks
    escalation/     - Review queue and escalation logic
    replan/         - Correction handling and impact analysis
    report/         - SRT, JSONL, and final report generation
  tests/
  fixtures/
  sample_run/
```
