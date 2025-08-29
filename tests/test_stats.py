import builtins

import stats as S


SAMPLE = """
Hello, world! Hello book. Ahab's whale; white whale.
""".strip()


def test_get_num_words_split_baseline():
    assert S.get_num_words(SAMPLE) == len(SAMPLE.split())


def test_char_counts_letters_only_filters_space():
    counts = S.get_num_chars_dict(SAMPLE)
    assert " " in counts
    counts_letters = S.get_num_chars_dict(SAMPLE, letters_only=True)
    assert " " not in counts_letters


def test_sort_counts_descending():
    counts = {"a": 2, "b": 5, "c": 1}
    items = S.sort_counts(counts)
    nums = [x["num"] for x in items]
    assert nums == sorted(nums, reverse=True)


def test_word_counts_and_sort():
    counts = S.get_word_counts(SAMPLE)
    # at least these tokens exist
    assert counts["hello"] == 2
    assert counts["whale"] == 2
    items = S.sort_words(counts)
    assert items[0]["num"] >= items[-1]["num"]


def test_bigrams_and_trigrams():
    bi = S.count_ngrams(SAMPLE, n=2)
    tri = S.count_ngrams(SAMPLE, n=3)
    assert ("white", "whale") in bi
    assert isinstance(next(iter(tri.keys())), tuple)


def test_readability_metrics_keys():
    m = S.readability_metrics(SAMPLE)
    for k in (
        "num_sentences",
        "num_words",
        "num_syllables",
        "avg_sentence_length",
        "avg_syllables_per_word",
        "flesch_reading_ease",
        "flesch_kincaid_grade",
    ):
        assert k in m


def test_vocab_metrics_ranges():
    m = S.vocabulary_metrics(SAMPLE)
    assert 0 < m["tokens"]
    assert 0 < m["types"] <= m["tokens"]
    assert 0.0 <= m["type_token_ratio"] <= 1.0


def test_category_counts_sums():
    m = S.category_counts(SAMPLE)
    total = sum(m.values())
    assert total == len(SAMPLE)

