from bookbot.cli import main as cli_main


def test_cli_smoke_chars_letters_only(capsys):
    cli_main(["chars", "books/mobydick.txt", "--top", "3", "--letters-only"])
    out = capsys.readouterr().out
    assert "BOOKBOT" in out
    assert "e:" in out

