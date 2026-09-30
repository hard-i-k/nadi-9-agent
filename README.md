# Nadi-9 Subtitle Agent

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate it.
3. Install dependencies: `pip install -e .`

## Running
```bash
nadi9 run --data fixtures --provider mock --max-model-calls 25 --max-tool-calls 50
```

## Tests
Run tests with `pytest tests/`
