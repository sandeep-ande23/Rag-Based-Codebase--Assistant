from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

from app.config import ALLOWED_EXTENSIONS, IGNORED_DIRS


def iter_supported_files(root: Path) -> Iterator[Path]:
    root = root.resolve()

    # Single file
    if root.is_file():
        if (
            root.suffix.lower() in ALLOWED_EXTENSIONS
            or root.name.lower() == "dockerfile"
        ):
            yield root
        return

    # Directory
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if (
            path.suffix.lower() in ALLOWED_EXTENSIONS
            or path.name.lower() == "dockerfile"
        ):
            yield path


def read_text_file(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def read_pdf_file(path: Path) -> str:
    """
    Extract text from a PDF while keeping page information.
    """

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        pages.append(
            f"[PAGE {page_number}]\n{text}"
        )

    return "\n\n".join(pages)


def line_number_at(text: str, char_offset: int) -> int:
    return text.count("\n", 0, char_offset) + 1


def is_code_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".sql",
    }


def load_file(path: Path) -> str:
    """
    Load a supported file.

    PDF files are extracted using pypdf.
    All other supported files are treated as text.
    """

    # PDF
    if path.suffix.lower() == ".pdf":
        return read_pdf_file(path)

    # Dockerfile and all configured text/code files
    if (
        path.name.lower() == "dockerfile"
        or path.suffix.lower() in ALLOWED_EXTENSIONS
    ):
        return read_text_file(path)

    return ""