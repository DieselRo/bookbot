from collections import Counter, deque
from typing import Dict, List, Optional, Set, Tuple

from ..corpus import stream_normalized_lines
from ..utils.tokenization import iter_words


def get_num_words(text: str) -> int:
    return len(text.split())


def get_num_chars_dict(text: str, letters_only: bool = False) -> Dict[str, int]:
    char_count: Dict[str, int] = {}
    for ch in text:
        ch = ch.lower()
        if letters_only and not ch.isalpha():
            continue
        char_count[ch] = char_count.get(ch, 0) + 1
    return char_count


def sort_counts(counts: Dict[str, int]) -> List[Dict[str, int]]:
    items = [{"char": k, "num": v} for k, v in counts.items()]
    items.sort(key=lambda x: x["num"], reverse=True)
    return items


def get_word_counts(text: str, stopwords: Optional[Set[str]] = None) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for token in iter_words(text):
        if stopwords and token in stopwords:
            continue
        counts[token] = counts.get(token, 0) + 1
    return counts


def sort_words(counts: Dict[str, int]) -> List[Dict[str, int]]:
    items = [{"word": k, "num": v} for k, v in counts.items()]
    items.sort(key=lambda x: x["num"], reverse=True)
    return items


def count_ngrams(text: str, n: int = 2, stopwords: Optional[Set[str]] = None) -> Dict[Tuple[str, ...], int]:
    tokens = [t for t in iter_words(text) if not (stopwords and t in stopwords)]
    counts: Dict[Tuple[str, ...], int] = {}
    if n <= 1:
        return counts
    for i in range(len(tokens) - n + 1):
        gram = tuple(tokens[i : i + n])
        counts[gram] = counts.get(gram, 0) + 1
    return counts


def sort_ngrams(counts: Dict[Tuple[str, ...], int]) -> List[Dict[str, int]]:
    items = [{"ngram": " ".join(k), "num": v} for k, v in counts.items()]
    items.sort(key=lambda x: x["num"], reverse=True)
    return items


def get_num_words_whitespace_stream(
    file_path: str, normalize_form: Optional[str] = None, ascii_only: bool = False
) -> int:
    total = 0
    for line in stream_normalized_lines(file_path, normalize_form, ascii_only):
        total += len(line.split())
    return total


def count_chars_stream(
    file_path: str, letters_only: bool = False, normalize_form: Optional[str] = None, ascii_only: bool = False
) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for line in stream_normalized_lines(file_path, normalize_form, ascii_only):
        for ch in line:
            ch = ch.lower()
            if letters_only and not ch.isalpha():
                continue
            counter[ch] += 1
    return dict(counter)


def get_word_counts_stream(
    file_path: str, stopwords: Optional[Set[str]] = None, normalize_form: Optional[str] = None, ascii_only: bool = False
) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for line in stream_normalized_lines(file_path, normalize_form, ascii_only):
        for token in iter_words(line):
            if stopwords and token in stopwords:
                continue
            counter[token] += 1
    return dict(counter)


def count_ngrams_stream(
    file_path: str, n: int = 2, stopwords: Optional[Set[str]] = None, normalize_form: Optional[str] = None, ascii_only: bool = False
) -> Dict[Tuple[str, ...], int]:
    counter: Counter[Tuple[str, ...]] = Counter()
    prev = deque(maxlen=n - 1)
    for line in stream_normalized_lines(file_path, normalize_form, ascii_only):
        tokens = [t for t in iter_words(line) if not (stopwords and t in stopwords)]
        if not tokens and not prev:
            continue
        buf = list(prev) + tokens
        for i in range(len(buf) - n + 1):
            gram = tuple(buf[i : i + n])
            counter[gram] += 1
        if len(buf) >= n - 1:
            prev.clear()
            prev.extend(buf[-(n - 1) :])
    return dict(counter)

