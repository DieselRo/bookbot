from pathlib import Path

from bookbot.utils.tokenization import prepare_text_chunk, iter_words
from bookbot.corpus import stream_normalized_lines
from bookbot.metrics.counts import count_chars_stream


def test_prepare_text_ascii_only_nfkd_drops_accents():
    s = "Café naïve coöperate — façade"
    out = prepare_text_chunk(s, normalize_form="NFKD", ascii_only=True)
    assert "é" not in out and "ö" not in out and "à" not in out
    assert "Cafe" in out and "naive" in out and "cooperate" in out


def test_iter_words_after_normalization_strips_quotes():
    s = prepare_text_chunk("Ahab's Café", normalize_form="NFKD", ascii_only=True)
    toks = list(iter_words(s))
    assert "ahab" in toks and "cafe" in toks


def test_stream_normalized_lines_reads_file(tmp_path: Path):
    p = tmp_path / "u.txt"
    p.write_text("Café\nüber", encoding="utf-8")
    lines = list(stream_normalized_lines(p, normalize_form="NFKD", ascii_only=True))
    assert lines[0].strip() == "Cafe"
    assert lines[1].strip() == "uber"


def test_chars_ascii_only_vs_unicode(tmp_path: Path):
    p = tmp_path / "u.txt"
    p.write_text("éé e", encoding="utf-8")
    # Without ascii_only, 'é' remains after NFC and is counted as non-ASCII letter
    counts1 = count_chars_stream(str(p), letters_only=True, normalize_form="NFC", ascii_only=False)
    counts2 = count_chars_stream(str(p), letters_only=True, normalize_form="NFKD", ascii_only=True)
    assert counts1.get("é", 0) >= 2
    # After ascii_only with NFKD, diacritics dropped -> 'e' increases
    assert counts2.get("é", 0) == 0
    assert counts2.get("e", 0) >= 3
