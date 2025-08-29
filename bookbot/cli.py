import argparse
import json
import logging
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List

from .corpus import collect_files, get_book_text
from .metrics.categories import category_counts
from .metrics.counts import (
    count_ngrams,
    count_ngrams_stream,
    count_chars_stream,
    get_num_chars_dict,
    get_num_words,
    get_num_words_whitespace_stream,
    get_word_counts,
    get_word_counts_stream,
    sort_counts,
    sort_ngrams,
    sort_words,
)
from .metrics.readability import readability_metrics
from .metrics.vocabulary import STOPWORDS_EN, vocabulary_metrics
from .rendering import (
    print_histogram,
    render_table_csv,
    render_table_html,
    render_table_md,
    render_table_text,
)


logger = logging.getLogger("bookbot")


def _sort_items(items, sort_by: str, desc: bool, key_field: str):
    if sort_by == "count":
        return sorted(items, key=lambda x: x["num"], reverse=desc)
    return sorted(items, key=lambda x: str(x[key_field]), reverse=desc)


def _mp_chars_task(path: str, letters_only: bool, sort: str, asc: bool, top: int | None, normalize: str, ascii_only: bool):
    try:
        nw = get_num_words_whitespace_stream(path, normalize_form=normalize, ascii_only=ascii_only)
        counts = count_chars_stream(path, letters_only=letters_only, normalize_form=normalize, ascii_only=ascii_only)
        items = sort_counts(counts)
        items = _sort_items(items, sort, not asc, key_field="char")
        to_show = items if top is None else items[: top]
        return {"path": path, "num_words": nw, "items": items, "to_show": to_show}
    except Exception as e:
        return {"path": path, "error": str(e)}


def _mp_words_task(path: str, stopwords_key: str, sort: str, asc: bool, top: int | None, normalize: str, ascii_only: bool):
    try:
        stopwords = STOPWORDS_EN if stopwords_key == "english" else None
        nw = get_num_words_whitespace_stream(path, normalize_form=normalize, ascii_only=ascii_only)
        counts = get_word_counts_stream(path, stopwords=stopwords, normalize_form=normalize, ascii_only=ascii_only)
        items = sort_words(counts)
        items = _sort_items(items, sort, not asc, key_field="word")
        to_show = items if top is None else items[: top]
        return {"path": path, "num_words": nw, "items": items, "to_show": to_show}
    except Exception as e:
        return {"path": path, "error": str(e)}


def _mp_ngrams_task(path: str, n: int, stopwords_key: str, sort: str, asc: bool, top: int | None, normalize: str, ascii_only: bool):
    try:
        stopwords = STOPWORDS_EN if stopwords_key == "english" else None
        counts = count_ngrams_stream(path, n=n, stopwords=stopwords, normalize_form=normalize, ascii_only=ascii_only)
        items = sort_ngrams(counts)
        items = _sort_items(items, sort, not asc, key_field="ngram")
        to_show = items if top is None else items[: top]
        return {"path": path, "n": n, "items": items, "to_show": to_show}
    except Exception as e:
        return {"path": path, "error": str(e)}


def run_chars_cmd(args):
    files = collect_files(args.paths)
    if not files:
        print("Error: no files to analyze", file=sys.stderr)
        sys.exit(1)

    results = []
    flat_rows = []

    def handle_result(res):
        if res.get("error"):
            if not args.quiet:
                print(f"Error reading '{res['path']}': {res['error']}", file=sys.stderr)
            return
        results.append({"path": res["path"], "num_words": res["num_words"], "items": res["to_show"]})
        for it in res["to_show"]:
            flat_rows.append([res["path"], it["char"], it["num"]])
        if args.format == "text":
            if not args.quiet:
                print("============ BOOKBOT ============")
                print(f"Analyzing book found at {res['path']}...")
                print("------------ WORD COUNT ------------")
                print(f"Found {res['num_words']} total words")
                print("--------- CHARACTER COUNT -----------")
            else:
                print(f"-- {res['path']}")
            for it in res["to_show"]:
                ch = it["char"]
                if args.letters_only and not str(ch).isalpha():
                    continue
                print(f"{ch}: {it['num']}")
            if args.format == "text" and not args.quiet:
                print("============= END =============")
            if args.histogram == "chars":
                print("\n--------- CHARACTER HISTOGRAM ---------")
                print_histogram(res["items"], key_field="char", top=args.top)

    if args.jobs and args.jobs > 1 and len(files) > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futs = [
                ex.submit(
                    _mp_chars_task, str(f), args.letters_only, args.sort, args.asc, args.top, args.normalize, args.ascii_only
                )
                for f in files
            ]
            for fut in futs:
                handle_result(fut.result())
    else:
        for f in files:
            res = _mp_chars_task(str(f), args.letters_only, args.sort, args.asc, args.top, args.normalize, args.ascii_only)
            handle_result(res)

    if args.format == "json":
        payload = {
            "report_version": 1,
            "command": "chars",
            "letters_only": args.letters_only,
            "sort": args.sort,
            "order": "asc" if args.asc else "desc",
            "top": args.top,
            "files": results,
        }
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format in ("csv", "md", "html"):
        headers = ["path", "char", "count"]
        if args.format == "csv":
            output = render_table_csv(headers, flat_rows)
        elif args.format == "md":
            output = render_table_md(headers, flat_rows)
        else:
            output = render_table_html(headers, flat_rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)


def run_words_cmd(args):
    files = collect_files(args.paths)
    if not files:
        print("Error: no files to analyze", file=sys.stderr)
        sys.exit(1)

    results = []
    flat_rows = []

    def handle_result(res):
        if res.get("error"):
            if not args.quiet:
                print(f"Error reading '{res['path']}': {res['error']}", file=sys.stderr)
            return
        results.append({"path": res["path"], "num_words": res["num_words"], "items": res["to_show"]})
        for it in res["to_show"]:
            flat_rows.append([res["path"], it["word"], it["num"]])
        if args.format == "text":
            if not args.quiet:
                print("============ BOOKBOT (WORDS) ============")
                print(f"Analyzing book found at {res['path']}...")
                print("------------ WORD COUNT ------------")
                print(f"Found {res['num_words']} total words")
                print("----------- WORD FREQUENCY -----------")
            else:
                print(f"-- {res['path']}")
            for it in res["to_show"]:
                print(f"{it['word']}: {it['num']}")
            if args.histogram == "words":
                print("\n----------- WORD HISTOGRAM ------------")
                print_histogram(res["items"], key_field="word", top=args.top)

    if args.jobs and args.jobs > 1 and len(files) > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futs = [
                ex.submit(
                    _mp_words_task, str(f), args.stopwords, args.sort, args.asc, args.top, args.normalize, args.ascii_only
                )
                for f in files
            ]
            for fut in futs:
                handle_result(fut.result())
    else:
        for f in files:
            res = _mp_words_task(str(f), args.stopwords, args.sort, args.asc, args.top, args.normalize, args.ascii_only)
            handle_result(res)

    if args.format == "json":
        payload = {
            "report_version": 1,
            "command": "words",
            "stopwords": args.stopwords,
            "sort": args.sort,
            "order": "asc" if args.asc else "desc",
            "top": args.top,
            "files": results,
        }
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format in ("csv", "md", "html"):
        headers = ["path", "word", "count"]
        if args.format == "csv":
            output = render_table_csv(headers, flat_rows)
        elif args.format == "md":
            output = render_table_md(headers, flat_rows)
        else:
            output = render_table_html(headers, flat_rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)


def run_compare_cmd(args):
    paths = [Path(args.path1), Path(args.path2)]
    for p in paths:
        if not p.is_file():
            print(f"Error: not a file: {p}", file=sys.stderr)
            sys.exit(1)
    results = []
    counts_list = []

    def analyze(p: Path):
        nw = get_num_words_whitespace_stream(p, normalize_form=args.normalize, ascii_only=args.ascii_only)
        if args.type == "chars":
            counts = count_chars_stream(p, letters_only=args.letters_only, normalize_form=args.normalize, ascii_only=args.ascii_only)
            items = sort_counts(counts)
            items = _sort_items(items, args.sort, not args.asc, key_field="char")
        else:
            stopwords = STOPWORDS_EN if args.stopwords == "english" else None
            counts = get_word_counts_stream(p, stopwords=stopwords, normalize_form=args.normalize, ascii_only=args.ascii_only)
            items = sort_words(counts)
            items = _sort_items(items, args.sort, not args.asc, key_field="word")
        if args.top is not None:
            items = items[: args.top]
        return nw, counts, items

    for p in paths:
        try:
            nw, counts, items = analyze(p)
            results.append({"path": str(p), "num_words": nw, "items": items})
            counts_list.append(counts)
        except OSError as e:
            if not args.quiet:
                print(f"Error reading '{p}': {e}", file=sys.stderr)
            sys.exit(1)

    label = "char" if args.type == "chars" else "word"
    path1, path2 = results[0]["path"], results[1]["path"]
    top_keys = { (it.get("char") or it.get("word")) for it in results[0]["items"] } | { (it.get("char") or it.get("word")) for it in results[1]["items"] }
    cap = args.top if args.top is not None else 20
    if args.sort == "count":
        combined_sorted = sorted(
            top_keys,
            key=lambda k: counts_list[0].get(k, 0) + counts_list[1].get(k, 0),
            reverse=not args.asc,
        )[:cap]
    else:
        combined_sorted = sorted(top_keys, key=lambda k: str(k), reverse=not args.asc)[:cap]
    rows = []
    for k in combined_sorted:
        c1 = counts_list[0].get(k, 0)
        c2 = counts_list[1].get(k, 0)
        rows.append([k, c1, c2, c1 - c2])
    headers = [label, f"{path1}", f"{path2}", "delta"]
    if args.format == "text":
        if not args.quiet:
            print(f"============ BOOKBOT (COMPARE {label.upper()}) ============")
        print(render_table_text(headers, rows))
    elif args.format in ("csv", "md", "html"):
        if args.format == "csv":
            output = render_table_csv(headers, rows)
        elif args.format == "md":
            output = render_table_md(headers, rows)
        else:
            output = render_table_html(headers, rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format == "json":
        payload = {
            "report_version": 1,
            "command": "compare",
            "type": args.type,
            "sort": args.sort,
            "order": "asc" if args.asc else "desc",
            "top": args.top,
            "files": results,
        }
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)


def run_ngrams_cmd(args):
    files = collect_files(args.paths)
    if not files:
        print("Error: no files to analyze", file=sys.stderr)
        sys.exit(1)
    results = []
    flat_rows = []

    def handle_result(res):
        if res.get("error"):
            if not args.quiet:
                print(f"Error reading '{res['path']}': {res['error']}", file=sys.stderr)
            return
        results.append({"path": res["path"], "n": args.n, "items": res["to_show"]})
        for it in res["to_show"]:
            flat_rows.append([res["path"], it["ngram"], it["num"]])
        if args.format == "text":
            if not args.quiet:
                print(f"============ BOOKBOT (NGRAMS n={args.n}) ============")
                print(f"Analyzing book found at {res['path']}...")
                print("----------- NGRAM FREQUENCY -----------")
            for it in res["to_show"]:
                print(f"{it['ngram']}: {it['num']}")
            if args.histogram:
                print("\n----------- NGRAM HISTOGRAM -----------")
                print_histogram(res.get("items", res["to_show"]), key_field="ngram", top=args.top)

    if args.jobs and args.jobs > 1 and len(files) > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futs = [
                ex.submit(
                    _mp_ngrams_task, str(f), args.n, args.stopwords, args.sort, args.asc, args.top, args.normalize, args.ascii_only
                )
                for f in files
            ]
            for fut in futs:
                handle_result(fut.result())
    else:
        for f in files:
            res = _mp_ngrams_task(str(f), args.n, args.stopwords, args.sort, args.asc, args.top, args.normalize, args.ascii_only)
            handle_result(res)

    if args.format == "json":
        payload = {
            "report_version": 1,
            "command": "ngrams",
            "n": args.n,
            "stopwords": args.stopwords,
            "sort": args.sort,
            "order": "asc" if args.asc else "desc",
            "top": args.top,
            "files": results,
        }
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format in ("csv", "md", "html"):
        headers = ["path", f"{args.n}-gram", "count"]
        if args.format == "csv":
            output = render_table_csv(headers, flat_rows)
        elif args.format == "md":
            output = render_table_md(headers, flat_rows)
        else:
            output = render_table_html(headers, flat_rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)


def run_readability_cmd(args):
    files = collect_files(args.paths)
    if not files:
        print("Error: no files to analyze", file=sys.stderr)
        sys.exit(1)
    results = []
    flat_rows = []
    for f in files:
        try:
            text = get_book_text(f)
        except OSError as e:
            if not args.quiet:
                print(f"Error reading '{f}': {e}", file=sys.stderr)
            continue
        m = readability_metrics(text)
        results.append({"path": str(f), **m})
        flat_rows.append([
            str(f),
            int(m['num_sentences']),
            int(m['num_words']),
            int(m['num_syllables']),
            f"{m['avg_sentence_length']:.2f}",
            f"{m['avg_syllables_per_word']:.2f}",
            f"{m['flesch_reading_ease']:.2f}",
            f"{m['flesch_kincaid_grade']:.2f}",
        ])

    if args.format == "json":
        payload = {"report_version": 1, "command": "readability", "files": results}
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format in ("csv", "md", "html"):
        headers = [
            "path",
            "sentences",
            "words",
            "syllables",
            "avg_sentence_length",
            "avg_syllables_per_word",
            "flesch_reading_ease",
            "flesch_kincaid_grade",
        ]
        if args.format == "csv":
            output = render_table_csv(headers, flat_rows)
        elif args.format == "md":
            output = render_table_md(headers, flat_rows)
        else:
            output = render_table_html(headers, flat_rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    else:
        for m in results:
            if not args.quiet:
                print("============ BOOKBOT (READABILITY) ============")
                print(f"Analyzing book found at {m['path']}...")
                print("----------- METRICS -----------")
            print(f"Sentences: {int(m['num_sentences'])}")
            print(f"Words: {int(m['num_words'])}")
            print(f"Syllables: {int(m['num_syllables'])}")
            print(f"Avg sentence length: {m['avg_sentence_length']:.2f}")
            print(f"Avg syllables/word: {m['avg_syllables_per_word']:.2f}")
            print(f"Flesch Reading Ease: {m['flesch_reading_ease']:.2f}")
            print(f"Flesch-Kincaid Grade: {m['flesch_kincaid_grade']:.2f}")


def run_vocab_cmd(args):
    files = collect_files(args.paths)
    if not files:
        print("Error: no files to analyze", file=sys.stderr)
        sys.exit(1)
    results = []
    flat_rows = []
    stopwords = STOPWORDS_EN if args.stopwords == "english" else None
    for f in files:
        try:
            text = get_book_text(f)
        except OSError as e:
            if not args.quiet:
                print(f"Error reading '{f}': {e}", file=sys.stderr)
            continue
        m = vocabulary_metrics(text, stopwords=stopwords)
        results.append({"path": str(f), **m})
        flat_rows.append([
            str(f),
            int(m['tokens']),
            int(m['types']),
            f"{m['type_token_ratio']:.4f}",
            int(m['hapax_legomena']),
            f"{m['hapax_ratio']:.4f}",
            int(m['dis_legomena']),
            f"{m['dis_ratio']:.4f}",
        ])

    if args.format == "json":
        payload = {"report_version": 1, "command": "vocab", "stopwords": args.stopwords, "files": results}
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format in ("csv", "md", "html"):
        headers = [
            "path",
            "tokens",
            "types",
            "type_token_ratio",
            "hapax_legomena",
            "hapax_ratio",
            "dis_legomena",
            "dis_ratio",
        ]
        if args.format == "csv":
            output = render_table_csv(headers, flat_rows)
        elif args.format == "md":
            output = render_table_md(headers, flat_rows)
        else:
            output = render_table_html(headers, flat_rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    else:
        for m in results:
            if not args.quiet:
                print("============ BOOKBOT (VOCAB) ============")
                print(f"Analyzing book found at {m['path']}...")
                print("----------- METRICS -----------")
            print(f"Tokens: {int(m['tokens'])}")
            print(f"Types: {int(m['types'])}")
            print(f"Type-Token Ratio: {m['type_token_ratio']:.4f}")
            print(f"Hapax Legomena: {int(m['hapax_legomena'])} ({m['hapax_ratio']:.4f})")
            print(f"Dis Legomena: {int(m['dis_legomena'])} ({m['dis_ratio']:.4f})")


def run_categories_cmd(args):
    files = collect_files(args.paths)
    if not files:
        print("Error: no files to analyze", file=sys.stderr)
        sys.exit(1)
    results = []
    flat_rows = []
    for f in files:
        try:
            text = get_book_text(f)
        except OSError as e:
            if not args.quiet:
                print(f"Error reading '{f}': {e}", file=sys.stderr)
            continue
        m = category_counts(text)
        results.append({"path": str(f), **m})
        flat_rows.append([
            str(f),
            m['uppercase'],
            m['lowercase'],
            m['digits'],
            m['punctuation'],
            m['whitespace'],
            m['other'],
        ])

    if args.format == "json":
        payload = {"report_version": 1, "command": "categories", "files": results}
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.format in ("csv", "md", "html"):
        headers = [
            "path",
            "uppercase",
            "lowercase",
            "digits",
            "punctuation",
            "whitespace",
            "other",
        ]
        if args.format == "csv":
            output = render_table_csv(headers, flat_rows)
        elif args.format == "md":
            output = render_table_md(headers, flat_rows)
        else:
            output = render_table_html(headers, flat_rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
    else:
        for m in results:
            if not args.quiet:
                print("============ BOOKBOT (CATEGORIES) ============")
                print(f"Analyzing book found at {m['path']}...")
                print("----------- COUNTS -----------")
            print(f"Uppercase: {m['uppercase']}")
            print(f"Lowercase: {m['lowercase']}")
            print(f"Digits: {m['digits']}")
            print(f"Punctuation: {m['punctuation']}")
            print(f"Whitespace: {m['whitespace']}")
            print(f"Other: {m['other']}")


def run_with_subcommands(argv: List[str]):
    parser = argparse.ArgumentParser(prog="bookbot", description="Analyze text files.")
    parser.add_argument("--quiet", action="store_true", help="Minimal text output")
    parser.add_argument("--verbose", action="store_true", help="Extra diagnostic output")
    sub = parser.add_subparsers(dest="command")

    # chars subcommand
    p_chars = sub.add_parser("chars", help="Character frequency analysis")
    p_chars.add_argument("paths", nargs="+", help="Files and/or directories to analyze (recursive)")
    p_chars.add_argument("--letters-only", action="store_true", help="Count only alphabetic characters")
    p_chars.add_argument("--ascii-only", action="store_true", help="Drop non-ASCII characters (after normalization)")
    p_chars.add_argument("--normalize", choices=["none", "NFC", "NFKC", "NFD", "NFKD"], default="none", help="Unicode normalization form")
    p_chars.add_argument("--top", type=int, default=None, help="Limit report to top N items")
    p_chars.add_argument("--sort", choices=["count", "char"], default="count", help="Sort by count or char")
    order = p_chars.add_mutually_exclusive_group()
    order.add_argument("--asc", action="store_true", help="Sort ascending")
    order.add_argument("--desc", action="store_true", help="Sort descending (default)")
    p_chars.add_argument("--format", choices=["text", "json", "csv", "md", "html"], default="text", help="Output format")
    p_chars.add_argument("--out", type=str, default=None, help="Write JSON output to file")
    p_chars.add_argument("--histogram", choices=["chars"], default=None, help="Print ASCII histogram")
    p_chars.add_argument("-j", "--jobs", type=int, default=1, help="Parallel workers for multi-file analysis")
    p_chars.set_defaults(func=run_chars_cmd)

    # words subcommand
    p_words = sub.add_parser("words", help="Word frequency analysis")
    p_words.add_argument("paths", nargs="+", help="Files and/or directories to analyze (recursive)")
    p_words.add_argument("--stopwords", choices=["none", "english"], default="none", help="Stopword list")
    p_words.add_argument("--ascii-only", action="store_true", help="Drop non-ASCII characters (after normalization)")
    p_words.add_argument("--normalize", choices=["none", "NFC", "NFKC", "NFD", "NFKD"], default="none", help="Unicode normalization form")
    p_words.add_argument("--top", type=int, default=None, help="Limit report to top N items")
    p_words.add_argument("--sort", choices=["count", "word"], default="count", help="Sort by count or word")
    order = p_words.add_mutually_exclusive_group()
    order.add_argument("--asc", action="store_true", help="Sort ascending")
    order.add_argument("--desc", action="store_true", help="Sort descending (default)")
    p_words.add_argument("--format", choices=["text", "json", "csv", "md", "html"], default="text", help="Output format")
    p_words.add_argument("--out", type=str, default=None, help="Write JSON output to file")
    p_words.add_argument("--histogram", choices=["words"], default=None, help="Print ASCII histogram")
    p_words.add_argument("-j", "--jobs", type=int, default=1, help="Parallel workers for multi-file analysis")
    p_words.set_defaults(func=run_words_cmd)

    # compare subcommand
    p_cmp = sub.add_parser("compare", help="Compare two files")
    p_cmp.add_argument("path1", help="First file")
    p_cmp.add_argument("path2", help="Second file")
    p_cmp.add_argument("--type", choices=["chars", "words"], default="chars", help="Comparison type")
    p_cmp.add_argument("--letters-only", action="store_true", help="Count only letters (chars mode)")
    p_cmp.add_argument("--stopwords", choices=["none", "english"], default="none", help="Stopwords (words mode)")
    p_cmp.add_argument("--ascii-only", action="store_true", help="Drop non-ASCII (after normalization)")
    p_cmp.add_argument("--normalize", choices=["none", "NFC", "NFKC", "NFD", "NFKD"], default="none", help="Unicode normalization")
    p_cmp.add_argument("--top", type=int, default=10, help="Top N items to show")
    p_cmp.add_argument("--sort", choices=["count", "char", "word"], default="count", help="Sort by count or key")
    order = p_cmp.add_mutually_exclusive_group()
    order.add_argument("--asc", action="store_true", help="Sort ascending")
    order.add_argument("--desc", action="store_true", help="Sort descending (default)")
    p_cmp.add_argument("--format", choices=["text", "json", "csv", "md", "html"], default="text", help="Output format")
    p_cmp.add_argument("--out", type=str, default=None, help="Write JSON output to file")
    p_cmp.set_defaults(func=run_compare_cmd)

    # ngrams subcommand
    p_ng = sub.add_parser("ngrams", help="N-gram frequency analysis (bigrams/trigrams)")
    p_ng.add_argument("paths", nargs="+", help="Files and/or directories to analyze (recursive)")
    p_ng.add_argument("--n", type=int, choices=[2, 3], default=2, help="Size of n-gram")
    p_ng.add_argument("--stopwords", choices=["none", "english"], default="none", help="Stopword list")
    p_ng.add_argument("--ascii-only", action="store_true", help="Drop non-ASCII characters (after normalization)")
    p_ng.add_argument("--normalize", choices=["none", "NFC", "NFKC", "NFD", "NFKD"], default="none", help="Unicode normalization form")
    p_ng.add_argument("--top", type=int, default=None, help="Limit report to top N items")
    p_ng.add_argument("--sort", choices=["count", "ngram"], default="count", help="Sort by count or ngram text")
    order = p_ng.add_mutually_exclusive_group()
    order.add_argument("--asc", action="store_true", help="Sort ascending")
    order.add_argument("--desc", action="store_true", help="Sort descending (default)")
    p_ng.add_argument("--format", choices=["text", "json", "csv", "md", "html"], default="text", help="Output format")
    p_ng.add_argument("--out", type=str, default=None, help="Write JSON output to file")
    p_ng.add_argument("--histogram", action="store_true", help="Print ASCII histogram")
    p_ng.add_argument("-j", "--jobs", type=int, default=1, help="Parallel workers for multi-file analysis")
    p_ng.set_defaults(func=run_ngrams_cmd)

    args = parser.parse_args(argv)

    # logging config
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    logger.setLevel(level)

    # Default desc unless --asc was provided
    if not getattr(args, "asc", False) and not getattr(args, "desc", False):
        setattr(args, "asc", False)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


def main(argv: List[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    first = next((a for a in argv if not a.startswith("-")), None)
    if first in {"chars", "words", "compare", "ngrams", "readability", "vocab", "categories"}:
        run_with_subcommands(argv)
        return

    parser = argparse.ArgumentParser(description="Analyze a book text file.")
    parser.add_argument("book_path", help="Path to the book text file")
    parser.add_argument("--top", type=int, default=None, help="Limit report to top N items")
    parser.add_argument("--letters-only", action="store_true", help="Count only alphabetic characters")
    parser.add_argument("--ascii-only", action="store_true", help="Drop non-ASCII characters (after normalization)")
    parser.add_argument("--normalize", choices=["none", "NFC", "NFKC", "NFD", "NFKD"], default="none", help="Unicode normalization form")
    parser.add_argument("--format", choices=["text", "json", "csv", "md", "html"], default="text", help="Output format")
    parser.add_argument("--out", type=str, default=None, help="Write output to a file (for non-text formats)")
    parser.add_argument("--words", action="store_true", help="Include word frequency report")
    parser.add_argument("--stopwords", choices=["none", "english"], default="none", help="Stopword list for word frequency report")
    parser.add_argument("--histogram", choices=["chars", "words"], default=None, help="Print an ASCII histogram for the selected category")
    parser.add_argument("--verbose", action="store_true", help="Extra diagnostic output")
    args = parser.parse_args(argv)

    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    logger.setLevel(level)

    book_path = Path(args.book_path)
    if not book_path.exists() or not book_path.is_file():
        print(f"Error: '{book_path}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    try:
        num_words = get_num_words_whitespace_stream(book_path, normalize_form=args.normalize, ascii_only=args.ascii_only)
        counts = count_chars_stream(book_path, letters_only=args.letters_only, normalize_form=args.normalize, ascii_only=args.ascii_only)
    except FileNotFoundError:
        print(f"Error: File not found: '{book_path}'.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: '{book_path}'.", file=sys.stderr)
        sys.exit(1)
    except IsADirectoryError:
        print(f"Error: Expected a file but got a directory: '{book_path}'.", file=sys.stderr)
        sys.exit(1)

    sorted_counts = sort_counts(counts)
    display_chars = [i for i in sorted_counts if str(i["char"]).isalpha()]
    if args.top is not None:
        display_chars = display_chars[: args.top]

    word_items = None
    if args.words or args.histogram == "words" or args.format in ("json", "csv", "md", "html"):
        stopwords = STOPWORDS_EN if args.stopwords == "english" else None
        word_counts = get_word_counts_stream(book_path, stopwords=stopwords, normalize_form=args.normalize, ascii_only=args.ascii_only)
        word_items = sort_words(word_counts)
        if args.top is not None and args.format == "text":
            word_items = word_items[: args.top]

    if args.format == "json":
        payload = {
            "report_version": 1,
            "book_path": str(book_path),
            "num_words": num_words,
            "letters_only": args.letters_only,
            "top": args.top,
            "chars": sorted_counts[: args.top] if args.top is not None else sorted_counts,
            "words": (word_items[: args.top] if args.top is not None else word_items) if word_items is not None else [],
        }
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
        return
    elif args.format in ("csv", "md", "html"):
        headers = ["path", "type", "key", "count"]
        rows = []
        for it in display_chars:
            rows.append([str(book_path), "char", it["char"], it["num"]])
        if args.words and word_items is not None:
            for it in (word_items[: args.top] if args.top is not None else word_items):
                rows.append([str(book_path), "word", it["word"], it["num"]])
        if args.format == "csv":
            output = render_table_csv(headers, rows)
        elif args.format == "md":
            output = render_table_md(headers, rows)
        else:
            output = render_table_html(headers, rows)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output)
        return

    # Text output
    print("============ BOOKBOT ============")
    print(f"Analyzing book found at {book_path}...")
    print("------------ WORD COUNT ------------")
    print(f"Found {num_words} total words")
    print("--------- CHARACTER COUNT -----------")
    for item in display_chars:
        print(f"{item['char']}: {item['num']}")
    print("============= END =============")

    if args.words and word_items is not None:
        print("\n----------- WORD FREQUENCY -----------")
        to_show = word_items[: args.top] if args.top is not None else word_items
        for item in to_show:
            print(f"{item['word']}: {item['num']}")

    if args.histogram == "chars":
        print("\n--------- CHARACTER HISTOGRAM ---------")
        print_histogram(sorted_counts, key_field="char", top=args.top)
    elif args.histogram == "words" and word_items is not None:
        print("\n----------- WORD HISTOGRAM ------------")
        print_histogram(word_items, key_field="word", top=args.top)
