from io import StringIO
import sys

from bookbot.rendering import (
    render_table_text,
    render_table_md,
    render_table_html,
    render_table_csv,
    print_histogram,
)


def test_render_table_text_basic():
    headers = ["k", "v"]
    rows = [["a", 1], ["bb", 2]]
    out = render_table_text(headers, rows)
    assert "k | v" in out
    assert "a" in out and "bb" in out


def test_render_table_md_basic():
    headers = ["k", "v"]
    rows = [["a", 1]]
    out = render_table_md(headers, rows)
    assert out.splitlines()[0].strip() == "| k | v |"
    assert "| a | 1 |" in out


def test_render_table_html_basic():
    headers = ["k", "v"]
    rows = [["a", 1]]
    out = render_table_html(headers, rows)
    assert "<table>" in out and "</table>" in out
    assert "<th>k</th>" in out and "<th>v</th>" in out
    assert "<td>a</td>" in out and "<td>1</td>" in out


def test_render_table_csv_basic():
    headers = ["k", "v"]
    rows = [["a", 1]]
    out = render_table_csv(headers, rows)
    assert out.splitlines()[0] == "k,v"
    assert "a,1" in out


def test_print_histogram_output():
    items = [{"char": "e", "num": 10}, {"char": "t", "num": 5}]
    buf = StringIO()
    old = sys.stdout
    try:
        sys.stdout = buf
        print_histogram(items, key_field="char", top=2, width=10)
    finally:
        sys.stdout = old
    out = buf.getvalue()
    assert "e" in out and "10" in out
    assert "t" in out and "5" in out

