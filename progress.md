# BookBot Progress & Roadmap

This document tracks actionable work items for BookBot. Use the checkboxes to mark progress and keep sections updated after merges.

Conventions:
- [ ] = not started, [~] = in progress, [x] = done

## Milestone 0 — Baseline (completed)
- [x] CLI accepts a book path and validates it
- [x] Word count and character frequency
- [x] Sorted character report (letters filtered in report)
- [x] Basic README usage instructions

## Milestone 1 — Low-Lift Next Steps
- [x] Add `--top N` to limit items in reports (default: all)
- [x] Add `--letters-only` to filter at counting stage (not just printing)
- [x] Add JSON export: `--format json` and `--out <path>`
- [x] Add ASCII histogram for top characters/words: `--histogram [chars|words] --top 20`
- [x] Word frequency report with stopword filtering: `--words --stopwords english`

Verification examples:
- `python3 main.py books/mobydick.txt --top 10 --letters-only`
- `python3 main.py books/mobydick.txt --format json --out report.json`
- `python3 main.py books/mobydick.txt --histogram chars --top 15`

## Milestone 2 — CLI & UX
- [x] Support analyzing multiple files and directories (recursive): `bookbot chars <path...>`
- [x] Subcommands: `chars`, `words`, `compare`
- [x] Sorting flags: `--sort count|char` and `--desc/--asc`
- [x] Verbosity: `--quiet` (global); groundwork in place for `--verbose`

Verification examples:
- `python3 main.py chars books/ --top 5 --letters-only`
- `python3 main.py words books/mobydick.txt --stopwords english --top 10`
- `python3 main.py compare books/mobydick.txt books/prideandprejudice.txt --type words --stopwords english --top 5`

## Milestone 3 — Text Analysis
- [x] Word frequencies with proper tokenization and case-folding
- [x] N-grams (bigrams/trigrams) with top-K reporting
- [x] Readability metrics (Flesch–Kincaid, average sentence length)
- [x] Vocabulary richness (type–token ratio, hapax/dis legomena)
- [x] Category counts: uppercase, lowercase, digits, punctuation

Verification examples:
- `python3 main.py ngrams books/mobydick.txt --n 2 --top 10 --stopwords english`
- `python3 main.py ngrams books/mobydick.txt --n 3 --top 5 --histogram`
- `python3 main.py readability books/mobydick.txt`
- `python3 main.py vocab books/prideandprejudice.txt --stopwords english`
- `python3 main.py categories books/frankenstein.txt`

## Milestone 4 — Output & Reporting
- [x] Export formats: CSV, Markdown, HTML (`--format csv|md|html`)
- [x] Side-by-side comparison output for two inputs
- [x] Pretty tables for terminal and Markdown outputs

Verification examples:
- `python3 main.py chars books/ --top 5 --letters-only --format md`
- `python3 main.py words books/mobydick.txt --stopwords english --top 5 --format html`
- `python3 main.py compare books/mobydick.txt books/prideandprejudice.txt --type chars --letters-only --top 5 --format csv`

## Milestone 5 — Performance & Robustness
- [x] Stream file reading (line-by-line) for large inputs
- [x] Faster counting with `collections.Counter`
- [x] Multiprocessing for analyzing multiple books concurrently
- [x] Unicode handling: normalization (`unicodedata.normalize`), optional ASCII-only mode

Verification examples:
- Streaming + ASCII-only: `python3 main.py chars books/mobydick.txt --normalize NFKD --ascii-only --top 10`
- Parallel: `python3 main.py words books/ --stopwords english -j 4 --top 10`
- N-grams streaming: `python3 main.py ngrams books/mobydick.txt --n 2 --stopwords english -j 4 --top 10`

## Milestone 6 — Quality & Packaging
- [x] Tests with `pytest` for counting, sorting, and reporting
- [x] Packaging via `pyproject.toml` with a `bookbot` console script entry point
- [x] Lint/format config: `ruff` and `black` in `pyproject.toml`
- [x] Logging behind `--verbose` (basic configuration)
- [~] Type hints: incrementally added in code; mypy optional

Verification examples:
- `pytest -q`
- `pip install -e . && bookbot chars books/mobydick.txt --top 5 --letters-only`

## Notes
- Keep `README.md` and this file updated when flags or outputs change.
- Prefer small, focused changes that map cleanly to the items above.

## Milestone A — Package Layout & CLI Parity
- [x] Create `bookbot/` package and move code according to target layout
- [x] Convert `main.py` to a thin shim importing `bookbot.cli:main`
- [x] Split renderers to `bookbot/rendering.py`; unify table contract; preserve formats
- [x] Fix `run_with_subcommands(argv)` to accept injected argv; add CLI smoke test
- Acceptance: CLI subcommands work; README examples succeed; golden outputs unchanged

## Milestone B — Schemas & Golden Tests
- [x] Implement `formats.py` with TypedDict/dataclasses for JSON payloads
- [x] Add golden JSON snapshots under `tests/golden/` and tests to compare
- [x] Document schemas in README and root `AGENTS.MD` pointers
- Acceptance: Golden tests pass; schemas stable

## Milestone C — Tokenization & Streaming Consolidation
- [x] Move `_iter_words`, normalization, and streaming utilities into `utils/tokenization.py` + `corpus.py`
- [x] Ensure `--normalize` and `--ascii-only` are respected consistently across commands
- [x] Add unit tests for Unicode/ASCII-only paths
- Acceptance: All tokenization/stream tests pass; flags behave consistently

## Milestone D — Sorting, Flags, and UX Consistency
- [x] Support `--sort count|char|word` with dynamic key selection; default `desc` everywhere
- [x] Centralize logging/verbosity; ensure `--quiet` suppresses banners
- [x] Update `--help` texts; sync README
- Acceptance: CLI invariants tested; help matches docs

## Milestone E — AGENTS.md Mesh & Automation
- [x] Add root `AGENTS.MD` v2 (version header, repo map, global contracts, root checklist)
- [x] Create scaffold/validator script `scripts/scaffold_agents.py`
- [x] Add pre-commit hook to validate per-directory `AGENTS.md`
- [x] Add CI job to validate front-matter schema/link basics
- [x] Generate per-directory `AGENTS.md` (bookbot/, metrics/, utils/, scripts/, tests/) and validate
- Acceptance: Hook prevents missing/broken guides; CI validates graph

## Milestone F — Test & Release Hygiene
- [x] Expand pytest coverage for renderers and CLI (incl. error paths)
- [~] Ensure Ruff/Black pass; add type hints to public APIs (incremental)
- [x] Update this file with CHANGELOG-style notes (What/Why/Validation)
- Acceptance: All tests & linters pass; progress updated

### CHANGELOG — Milestone F
- Added renderer unit tests for text/MD/HTML/CSV tables and histogram output.
- Added CLI error-path tests (invalid paths, quiet banner suppression).
- Maintained JSON golden tests for core commands (chars/words/ngrams/compare).
- Centralized tokenization/streaming in utils/corpus; legacy `stats.py` now a shim.


## Post‑Merge QA Sweep
- [x] Console entrypoint set to `bookbot.cli:main` (shim `main.py` kept)
- [x] JSON stability: add `report_version: 1` to all JSON payloads and goldens
- [ ] Cross‑platform: run goldens on Windows/Linux (CSV quoting, HTML escaping)
- [x] Determinism: sort before applying `--top`; preserve file order with `-j`
- [x] Error UX: non‑zero exit on missing files/I/O; `--quiet` still prints machine output
- [x] Docs parity: README flags match `--help`; AGENTS.MD points to schemas/goldens
- [x] Agents mesh: CI validates presence/links/front‑matter

## Milestone G — Style Profiles & Thresholds (Author Mode v1)
- [ ] Add `profiles/` with YAML (e.g., `ya.yml`, `techdoc.yml`, `blog.yml`) defining targets:
  - readability bands (FRE/FK), max long‑sentence %, min TTR, max top‑5 repetition
- [ ] CLI: `--profile <name>` loads thresholds and prints PASS/FAIL per metric
- [ ] JSON: include `profile`, thresholds, and `violations[]`
- [ ] Docs: profile schema + examples; root AGENTS.MD points to profiles/
- Acceptance: `--enforce` returns exit code 1 on violation (opt‑in)

## Milestone H — Repetition & Pacing Lints
- [ ] Add lints module: overused words/phrases (top‑K share), sentence length distribution (mean/variance, % > N tokens), cliché detector seeds
- [ ] CLI: `lint` subcommand and `--lint all|repetition|pacing|cliche`
- [ ] JSON: `lints: [{id, description, score, threshold, status}]`
- Acceptance: `bookbot lint <paths>` produces text/JSON/MD/HTML; honors profiles and `--enforce`

## Milestone I — Draft Delta Reports (Compare++ for Authors)
- [ ] `compare-drafts` subcommand: compare two directories (old/new) by filename; per‑file deltas for readability, vocab, repetition, pacing
- [ ] Output: per‑file table + aggregate summary (regressions first); JSON bundle with `files[]` and totals
- [ ] Golden: capture a tiny fixture repo for stable diff formatting
- Acceptance: exits non‑zero if any enforced threshold regresses (`--enforce`)

## Milestone J — Watch Mode (Fast Feedback Loop)
- [ ] `watch` subcommand (watchfiles): on change, run selected analyses (`--on-save chars,readability,lint --profile ya`)
- [ ] Debounce + minimal reruns (only changed files); stable, concise terminal output
- [ ] Optional `--out-dir reports/` to write MD/HTML snapshots per file
- Acceptance: editing a test file re‑triggers analysis within ~1s; no duplicate runs on rapid saves
