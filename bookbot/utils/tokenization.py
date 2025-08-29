import re
import unicodedata
from typing import Iterable, Optional


def iter_words(text: str) -> Iterable[str]:
    for token in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower()):
        token = token.strip("'")
        if token:
            yield token


def prepare_text_chunk(s: str, normalize_form: Optional[str] = None, ascii_only: bool = False) -> str:
    if normalize_form and normalize_form.lower() != "none":
        s = unicodedata.normalize(normalize_form, s)
    if ascii_only:
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s

