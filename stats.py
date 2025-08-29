"""
Compatibility shim for legacy imports.

Re-exports functions and constants from the refactored bookbot package so
existing code that imports `stats` continues to work.
"""
from typing import Dict, List, Optional, Set, Tuple  # noqa: F401

from bookbot.metrics.counts import (  # noqa: F401
    get_num_words,
    get_num_chars_dict,
    sort_counts,
    get_word_counts,
    sort_words,
    count_ngrams,
    sort_ngrams,
    get_num_words_whitespace_stream,
    count_chars_stream,
    get_word_counts_stream,
    count_ngrams_stream,
)
from bookbot.metrics.readability import readability_metrics  # noqa: F401
from bookbot.metrics.vocabulary import (  # noqa: F401
    vocabulary_metrics,
    STOPWORDS_EN,
)
from bookbot.metrics.categories import category_counts  # noqa: F401
from bookbot.rendering import print_histogram  # noqa: F401


def report_list(book_path, num_words, dict_list):
    print("============ BOOKBOT ============")
    print(f"Analyzing book found at {book_path}...")
    print("------------ WORD COUNT ------------")
    print(f"Found {num_words} total words")
    print("--------- CHARACTER COUNT -----------")
    for item in dict_list:
        char = item["char"]
        count = item["num"]
        if str(char).isalpha():
            print(f"{char}: {count}")
    print("============= END =============")
