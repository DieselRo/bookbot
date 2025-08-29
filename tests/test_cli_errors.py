import sys
from io import StringIO
import contextlib

from bookbot.cli import main as cli_main


@contextlib.contextmanager
def capture_io():
    old_out, old_err = sys.stdout, sys.stderr
    out, err = StringIO(), StringIO()
    try:
        sys.stdout, sys.stderr = out, err
        yield out, err
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def test_chars_nonexistent_path_exits_nonzero():
    with capture_io() as (out, err):
        try:
            cli_main(["chars", "does-not-exist.txt"])
            assert False, "expected SystemExit"
        except SystemExit as e:
            assert e.code != 0
    assert "no files to analyze" in err.getvalue().lower()


def test_legacy_mode_invalid_file_exits():
    with capture_io() as (out, err):
        try:
            cli_main(["does-not-exist.txt"])
            assert False, "expected SystemExit"
        except SystemExit as e:
            assert e.code != 0
    assert "not a valid file" in err.getvalue().lower()


def test_compare_quiet_suppresses_banner():
    with capture_io() as (out, err):
        cli_main([
            "compare",
            "books/mobydick.txt",
            "books/prideandprejudice.txt",
            "--type",
            "words",
            "--stopwords",
            "english",
            "--top",
            "3",
            "--format",
            "text",
            "--quiet",
        ])
    s = out.getvalue()
    assert "BOOKBOT (COMPARE" not in s
    assert "word  |" in s or "word |" in s

