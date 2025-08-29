# bookbot

[![CI](https://github.com/DieselRo/bookbot/actions/workflows/ci.yml/badge.svg)](https://github.com/DieselRo/bookbot/actions/workflows/ci.yml)

BookBot is my first [Boot.dev](https://www.boot.dev) project!

## Usage

There are two ways to run BookBot:

1) Legacy single-file mode (kept for compatibility):

- `python3 main.py books/mobydick.txt`
- Options: `--top`, `--letters-only`, `--format`, `--out`, `--words`, `--stopwords`, `--histogram`

2) Subcommands (recommended):

- Character analysis over files/directories (recursive):
  - `python3 main.py chars books/ --top 10 --letters-only`
  - `python3 main.py chars books/mobydick.txt --histogram chars --top 15`
  - JSON: `python3 main.py chars books/ --format json --top 5 --out chars.json`
  - Faster: add workers `-j 4`, normalize/fold: `--normalize NFKD --ascii-only`

- Word frequency analysis:
  - `python3 main.py words books/mobydick.txt --stopwords english --top 10`
  - `python3 main.py words books/ --histogram words --top 15 -j 4`
  - JSON: `python3 main.py words books/ --format json --out words.json`

- Compare two files:
  - Characters: `python3 main.py compare books/mobydick.txt books/prideandprejudice.txt --type chars --top 10`
  - Words: `python3 main.py compare books/mobydick.txt books/prideandprejudice.txt --type words --stopwords english --top 10`

- N-grams (bigrams/trigrams):
  - `python3 main.py ngrams books/mobydick.txt --n 2 --top 10 --stopwords english`
  - `python3 main.py ngrams books/mobydick.txt --n 3 --top 5 --histogram`

- Readability metrics:
  - `python3 main.py readability books/mobydick.txt`

- Vocabulary richness:
  - `python3 main.py vocab books/prideandprejudice.txt --stopwords english`

- Character categories:
  - `python3 main.py categories books/frankenstein.txt`

Common flags:
- `--top N`: limit items shown
- Sorting: `--sort count|char|word|ngram` (as applicable) with `--asc` or `--desc` (default desc)
- Output: `--format text|json|csv|md|html`, `--out PATH` for non-text files
- `--letters-only` (chars), `--stopwords none|english` (words)
- Unicode: `--normalize none|NFC|NFKC|NFD|NFKD`, `--ascii-only` to drop non-ASCII
- Parallelism: `-j/--jobs N` for multi-file subcommands (chars/words/ngrams)
- `--quiet` for minimal text output

## Development

- Setup a virtualenv and install dev tools (optional):
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -U pip pytest black ruff`
- Run tests:
  - `pytest -q`
  - Golden JSON fixtures live under `tests/golden/`; schema types are in `bookbot/formats.py`.
- Lint/format (optional):
  - `ruff check .`
  - `black .`
- Install CLI locally:
  - `pip install -e .`
  - Run as `bookbot ...` (equivalent to `python3 main.py ...`)


## Contributing

- See `CONTRIBUTING.md` for dev setup, checks, and golden tests.
