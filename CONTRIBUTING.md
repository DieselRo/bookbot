# Contributing to BookBot

Thanks for considering a contribution! This project aims to provide a fast, scriptable text analytics CLI with stable outputs and clear guidance for human and AI agents.

## Development Setup

- Python 3.12+
- Optional virtualenv:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -U pip`
- Install dev tools:
  - `pip install pytest ruff black`
- Editable install (optional):
  - `pip install -e .`

## Run Checks Locally

- Lint: `ruff check .`
- Format check: `black --check .`
- Tests: `pytest -q`
- AGENTS mesh validation: `python scripts/scaffold_agents.py --validate`

## Golden Outputs

- JSON schemas live in `bookbot/formats.py`.
- Golden fixtures live under `tests/golden/` and are compared in tests.
- All JSON payloads include `report_version` (current: 1). Bump on breaking changes and update goldens intentionally.

## Commit Guidance

- Keep changes small and focused.
- Update README, AGENTS.MD, and progress.md when behavior or flags change.
- Ensure tests pass and linters are clean before opening a PR.
