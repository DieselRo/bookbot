import json
from pathlib import Path
from io import StringIO
import sys

from bookbot.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "tests" / "golden"


def run_cli(argv):
    buf = StringIO()
    old = sys.stdout
    try:
        sys.stdout = buf
        cli_main(argv)
        return buf.getvalue()
    finally:
        sys.stdout = old


def j(s: str):
    return json.loads(s)


def load_golden(name: str):
    return json.loads((GOLD / name).read_text(encoding="utf-8"))


def test_golden_chars_json():
    out = run_cli(["chars", "books/mobydick.txt", "--letters-only", "--top", "3", "--format", "json"]) 
    assert j(out) == load_golden("chars_moby_top3.json")


def test_golden_words_json():
    out = run_cli(["words", "books/mobydick.txt", "--stopwords", "english", "--top", "3", "--format", "json"]) 
    assert j(out) == load_golden("words_moby_stop_en_top3.json")


def test_golden_ngrams_json():
    out = run_cli(["ngrams", "books/mobydick.txt", "--n", "2", "--stopwords", "english", "--top", "3", "--format", "json"]) 
    assert j(out) == load_golden("ngrams_moby_bi_top3.json")


def test_golden_compare_json():
    out = run_cli(["compare", "books/mobydick.txt", "books/prideandprejudice.txt", "--type", "words", "--stopwords", "english", "--top", "3", "--format", "json"]) 
    assert j(out) == load_golden("compare_words_top3.json")
