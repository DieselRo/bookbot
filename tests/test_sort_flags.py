from io import StringIO
import sys
import json

from bookbot.cli import main as cli_main


def run(argv):
    old = sys.stdout
    buf = StringIO()
    try:
        sys.stdout = buf
        cli_main(argv)
        return buf.getvalue()
    finally:
        sys.stdout = old


def test_default_desc_order_words():
    out = run(["words", "books/mobydick.txt", "--stopwords", "english", "--top", "5", "--format", "json"])
    data = json.loads(out)
    items = data["files"][0]["items"]
    nums = [it["num"] for it in items]
    assert nums == sorted(nums, reverse=True)


def test_compare_sort_by_word_key():
    out = run([
        "compare",
        "books/mobydick.txt",
        "books/prideandprejudice.txt",
        "--type",
        "words",
        "--stopwords",
        "english",
        "--top",
        "5",
        "--sort",
        "word",
        "--asc",
        "--format",
        "json",
    ])
    data = json.loads(out)
    # Just ensure command accepted and returned correct structure
    assert data["command"] == "compare"
    assert data["type"] == "words"
