import csv
import html as _html
import io
from typing import List, Dict, Optional


def render_table_text(headers: List[str], rows: List[List[object]]) -> str:
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt_row(r):
        return " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(r))

    header = fmt_row(headers)
    sep = "-+-".join("-" * w for w in widths)
    body = "\n".join(fmt_row(r) for r in rows)
    return f"{header}\n{sep}\n{body}" if rows else f"{header}\n{sep}"


def render_table_md(headers: List[str], rows: List[List[object]]) -> str:
    def row_to_md(r):
        return "| " + " | ".join(str(c) for c in r) + " |"

    header = row_to_md(headers)
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = "\n".join(row_to_md(r) for r in rows)
    return f"{header}\n{sep}\n{body}" if rows else f"{header}\n{sep}"


def render_table_html(headers: List[str], rows: List[List[object]]) -> str:
    def esc(x):
        return _html.escape(str(x))

    thead = "<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr></thead>"
    tbody_rows = []
    for r in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in r)
        tbody_rows.append(f"<tr>{tds}</tr>")
    tbody = "<tbody>" + "".join(tbody_rows) + "</tbody>"
    return f"<table>{thead}{tbody}</table>"


def render_table_csv(headers: List[str], rows: List[List[object]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for r in rows:
        writer.writerow([str(c) for c in r])
    return buf.getvalue()


def print_histogram(items: List[Dict[str, int]], key_field: str = "char", top: Optional[int] = None, width: int = 50) -> None:
    if top is not None:
        items = items[:top]
    if not items:
        return
    max_num = max(x["num"] for x in items)
    for x in items:
        label = str(x[key_field])
        num = x["num"]
        bar_len = int(num / max_num * width) if max_num else 0
        bar = "#" * bar_len
        print(f"{label:>12} | {bar} {num}")

