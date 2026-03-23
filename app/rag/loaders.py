from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def load_document(file_path: Path) -> str:
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    return load_text_file(file_path)