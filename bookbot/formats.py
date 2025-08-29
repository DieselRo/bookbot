from typing import List, Optional, Literal, TypedDict


class CharsItem(TypedDict):
    char: str
    num: int


class WordsItem(TypedDict):
    word: str
    num: int


class NgramItem(TypedDict):
    ngram: str
    num: int


class FileItems(TypedDict):
    path: str
    num_words: int
    items: List[dict]


class CharsReport(TypedDict):
    command: Literal["chars"]
    letters_only: bool
    sort: Literal["count", "char"]
    order: Literal["asc", "desc"]
    top: Optional[int]
    files: List[FileItems]


class WordsReport(TypedDict):
    command: Literal["words"]
    stopwords: Literal["none", "english"]
    sort: Literal["count", "word"]
    order: Literal["asc", "desc"]
    top: Optional[int]
    files: List[FileItems]


class CompareReport(TypedDict):
    command: Literal["compare"]
    type: Literal["chars", "words"]
    sort: Literal["count", "char"]
    order: Literal["asc", "desc"]
    top: Optional[int]
    files: List[FileItems]


class NgramsReport(TypedDict):
    command: Literal["ngrams"]
    n: Literal[2, 3]
    stopwords: Literal["none", "english"]
    sort: Literal["count", "ngram"]
    order: Literal["asc", "desc"]
    top: Optional[int]
    files: List[FileItems]


class ReadabilityFile(TypedDict):
    path: str
    num_sentences: float
    num_words: float
    num_syllables: float
    avg_sentence_length: float
    avg_syllables_per_word: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float


class ReadabilityReport(TypedDict):
    command: Literal["readability"]
    files: List[ReadabilityFile]


class VocabFile(TypedDict):
    path: str
    tokens: float
    types: float
    type_token_ratio: float
    hapax_legomena: float
    hapax_ratio: float
    dis_legomena: float
    dis_ratio: float


class VocabReport(TypedDict):
    command: Literal["vocab"]
    stopwords: Literal["none", "english"]
    files: List[VocabFile]


class CategoriesFile(TypedDict):
    path: str
    uppercase: int
    lowercase: int
    digits: int
    punctuation: int
    whitespace: int
    other: int


class CategoriesReport(TypedDict):
    command: Literal["categories"]
    files: List[CategoriesFile]


class LegacySingleReport(TypedDict):
    book_path: str
    num_words: int
    letters_only: bool
    top: Optional[int]
    chars: List[CharsItem]
    words: List[WordsItem]

