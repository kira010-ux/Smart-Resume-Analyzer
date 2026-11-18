"""Text extraction and normalization for resume and job-description inputs."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
import string


MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
SUPPORTED_EXTENSIONS = frozenset({".pdf", ".docx", ".txt"})


class TextExtractionError(ValueError):
    """Base error for invalid or unreadable input documents."""


class UnsupportedFileTypeError(TextExtractionError):
    """Raised when an uploaded file is not PDF, DOCX, or TXT."""


class FileTooLargeError(TextExtractionError):
    """Raised when an uploaded file exceeds the configured size limit."""


class EmptyTextError(TextExtractionError):
    """Raised when extraction produces no usable text."""


# Kept local so cleaning stays dependency-free and predictable in the API.
STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "have", "in", "is", "it", "of", "on", "or", "that", "the",
        "their", "this", "to", "was", "were", "will", "with", "you", "your",
    }
)


def clean_text(text: str, *, remove_stopwords: bool = True) -> str:
    """Lowercase text, remove punctuation, and collapse whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = text.lower().translate(str.maketrans("", "", string.punctuation))
    words = re.findall(r"\S+", normalized)
    if remove_stopwords:
        words = [word for word in words if word not in STOPWORDS]
    return " ".join(words)


def extract_text_from_text(text: str) -> str:
    """Validate and clean pasted plain text."""
    if not text or not text.strip():
        raise EmptyTextError("Input text cannot be empty")
    cleaned = clean_text(text)
    if not cleaned:
        raise EmptyTextError("Input text contains no usable words")
    return cleaned


def _extract_pdf(file_content: bytes) -> str:
    import pdfplumber

    with pdfplumber.open(BytesIO(file_content)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _extract_docx(file_content: bytes) -> str:
    from docx import Document

    document = Document(BytesIO(file_content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(paragraphs)


def _extract_raw_file_text(file_content: bytes, filename: str) -> str:
    """Extract source text without normalization for readable annotations."""
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension or filename}'. Use {supported}."
        )
    if extension == ".pdf":
        return _extract_pdf(file_content)
    if extension == ".docx":
        return _extract_docx(file_content)
    return file_content.decode("utf-8-sig", errors="replace")


def extract_raw_text_from_file(
    file_content: bytes,
    filename: str,
    *,
    max_file_size: int = MAX_FILE_SIZE_BYTES,
) -> str:
    """Extract source text while retaining wording and line breaks."""
    if not file_content:
        raise EmptyTextError("Uploaded file is empty")
    if len(file_content) > max_file_size:
        raise FileTooLargeError(
            f"File exceeds the {max_file_size // (1024 * 1024)} MB size limit"
        )
    raw_text = _extract_raw_file_text(file_content, filename)
    extract_text_from_text(raw_text)
    return raw_text


def extract_text_from_file(
    file_content: bytes,
    filename: str,
    *,
    max_file_size: int = MAX_FILE_SIZE_BYTES,
) -> str:
    """Extract and clean text from a PDF, DOCX, or TXT byte payload."""
    if not file_content:
        raise EmptyTextError("Uploaded file is empty")
    if len(file_content) > max_file_size:
        raise FileTooLargeError(
            f"File exceeds the {max_file_size // (1024 * 1024)} MB size limit"
        )

    raw_text = extract_raw_text_from_file(
        file_content,
        filename,
        max_file_size=max_file_size,
    )
    return extract_text_from_text(raw_text)


if __name__ == "__main__":
    sample = extract_text_from_text("Python, SQL, and the art of problem-solving.")
    assert sample == "python sql art problemsolving"
    print(sample)
