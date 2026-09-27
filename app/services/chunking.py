from dataclasses import dataclass
import re

from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.services.loaders import line_number_at, is_code_file


@dataclass
class Chunk:
    text: str
    path: str
    start_line: int
    end_line: int
    chunk_id: str
    page: int | None = None


def _hard_split(text: str, size: int, overlap: int):
    if size <= overlap:
        raise ValueError("CHUNK_SIZE must be greater than CHUNK_OVERLAP")

    step = size - overlap
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        yield start, end, text[start:end]

        if end >= len(text):
            break

        start += step


def _paragraph_chunks(text: str, size: int, overlap: int):
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    chunks = []
    current = ""
    current_start = 0
    cursor = 0

    for paragraph in paragraphs:
        pos = text.find(paragraph, cursor)
        pos = 0 if pos == -1 else pos
        cursor = pos + len(paragraph)

        if len(paragraph) > size:
            if current:
                chunks.append(
                    (
                        current_start,
                        current_start + len(current),
                        current,
                    )
                )
                current = ""

            for start, end, piece in _hard_split(
                paragraph,
                size,
                overlap,
            ):
                chunks.append(
                    (
                        pos + start,
                        pos + end,
                        piece,
                    )
                )

            current_start = cursor
            continue

        candidate = (
            paragraph
            if not current
            else current + "\n\n" + paragraph
        )

        if len(candidate) <= size:
            if not current:
                current_start = pos

            current = candidate

        else:
            chunks.append(
                (
                    current_start,
                    current_start + len(current),
                    current,
                )
            )

            tail = current[-overlap:] if overlap else ""

            current = (
                (tail + "\n\n" + paragraph).strip()
                if tail
                else paragraph
            )

            if len(current) > size:
                for start, end, piece in _hard_split(
                    current,
                    size,
                    overlap,
                ):
                    chunks.append(
                        (
                            pos - len(tail) + start,
                            pos - len(tail) + end,
                            piece,
                        )
                    )

                current = ""

            current_start = max(0, pos - len(tail))

    if current:
        chunks.append(
            (
                current_start,
                current_start + len(current),
                current,
            )
        )

    return chunks


def _code_chunks(text: str, size: int, overlap: int):
    """
    Lightweight code-aware boundaries:
    function/class/SQL statement headings,
    while retaining a hard maximum size.
    """

    lines = text.splitlines(keepends=True)

    groups = []
    start = 0

    for i, line in enumerate(lines):

        if (
            i > 0
            and re.match(
                r"^\s*(def |class |async def |function |"
                r"CREATE\s+(TABLE|VIEW|PROCEDURE|FUNCTION)|"
                r"SELECT\s+)",
                line,
                re.I,
            )
        ):
            groups.append(
                (
                    "".join(lines[start:i]),
                    start,
                    i,
                )
            )

            start = i

    groups.append(
        (
            "".join(lines[start:]),
            start,
            len(lines),
        )
    )

    chunks = []
    char_cursor = 0

    for group_text, line_start, line_end in groups:

        if not group_text.strip():
            char_cursor += len(group_text)
            continue

        if len(group_text) <= size:

            chunks.append(
                (
                    char_cursor,
                    char_cursor + len(group_text),
                    group_text,
                )
            )

        else:

            for a, b, piece in _hard_split(
                group_text,
                size,
                overlap,
            ):
                chunks.append(
                    (
                        char_cursor + a,
                        char_cursor + b,
                        piece,
                    )
                )

        char_cursor += len(group_text)

    return chunks


def _pdf_page_at_position(text: str, char_offset: int) -> int | None:
    """
    Find the PDF page containing the character position.

    PDF text contains markers such as:

        [PAGE 1]
        text...

        [PAGE 2]
        more text...

    We find the last page marker before the chunk starts.
    """

    matches = list(
        re.finditer(
            r"\[PAGE\s+(\d+)\]",
            text,
            re.IGNORECASE
        )
    )

    current_page = None

    for match in matches:
        if match.start() > char_offset:
            break

        current_page = int(match.group(1))

    return current_page


def chunk_document(
    text: str,
    path: str,
    size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
):
    """
    Split a document into chunks.

    Code files use code-aware chunking.
    Normal documents use paragraph-based chunking.
    PDFs additionally preserve their page number.
    """

    path_obj = __import__("pathlib").Path(path)

    is_pdf = path_obj.suffix.lower() == ".pdf"

    if is_code_file(path_obj):
        raw_chunks = _code_chunks(
            text,
            size,
            overlap,
        )
    else:
        raw_chunks = _paragraph_chunks(
            text,
            size,
            overlap,
        )

    result = []

    for index, (start, end, chunk_text) in enumerate(raw_chunks):

        if not chunk_text.strip():
            continue

        page = _pdf_page_at_position(text, start) if is_pdf else None

        result.append(
            Chunk(
                text=chunk_text,
                path=path,
                start_line=line_number_at(text, start),
                end_line=line_number_at(
                    text,
                    max(start, end - 1),
                ),
                chunk_id=f"{path}::chunk-{index}",
                page=page,
            )
        )

    return result