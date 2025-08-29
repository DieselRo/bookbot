import re
from typing import Dict

from ..utils.tokenization import iter_words


def _count_syllables(word: str) -> int:
    vowels = "aeiouy"
    w = word.lower()
    if not w:
        return 0
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    count = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def readability_metrics(text: str) -> Dict[str, float]:
    sentences = [s for s in re.split(r"(?<=[.!?])[\s\n]+", text.strip()) if s]
    num_sentences = max(1, len(sentences))
    tokens = list(iter_words(text))
    num_words = max(1, len(tokens))
    num_syllables = sum(_count_syllables(t) for t in tokens)
    asl = num_words / num_sentences
    asw = num_syllables / num_words
    flesch = 206.835 - 1.015 * asl - 84.6 * asw
    fk_grade = 0.39 * asl + 11.8 * asw - 15.59
    return {
        "num_sentences": float(num_sentences),
        "num_words": float(num_words),
        "num_syllables": float(num_syllables),
        "avg_sentence_length": float(asl),
        "avg_syllables_per_word": float(asw),
        "flesch_reading_ease": float(flesch),
        "flesch_kincaid_grade": float(fk_grade),
    }

