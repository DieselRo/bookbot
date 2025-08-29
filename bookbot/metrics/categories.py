import string
import unicodedata
from typing import Dict


def category_counts(text: str) -> Dict[str, int]:
    upper = lower = digit = punct = space = other = 0
    for ch in text:
        if ch.isupper():
            upper += 1
        elif ch.islower():
            lower += 1
        elif ch.isdigit():
            digit += 1
        elif ch.isspace():
            space += 1
        elif unicodedata.category(ch).startswith('P') or ch in string.punctuation:
            punct += 1
        else:
            other += 1
    return {
        "uppercase": upper,
        "lowercase": lower,
        "digits": digit,
        "punctuation": punct,
        "whitespace": space,
        "other": other,
    }

