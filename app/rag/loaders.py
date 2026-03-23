from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def is_supported_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def load_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def load_document(file_path: Path) -> str:
    if not is_supported_file(file_path):
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    return load_text_file(file_path)