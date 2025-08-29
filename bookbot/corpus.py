from pathlib import Path
from typing import Iterable, List, Optional

from .utils.tokenization import prepare_text_chunk


def get_book_text(file_path: str | Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def stream_normalized_lines(
    file_path: str | Path, normalize_form: Optional[str] = None, ascii_only: bool = False
) -> Iterable[str]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            yield prepare_text_chunk(line, normalize_form, ascii_only)


def collect_files(paths: List[str | Path]) -> List[Path]:
    files: List[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for fp in path.rglob("*"):
                if fp.is_file():
                    files.append(fp)
    return sorted(set(files))

