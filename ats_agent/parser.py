from io import BytesIO


class ResumeParsingError(ValueError):
    """Raised when resume content cannot be parsed."""


def _decode_text(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="ignore")


def _extract_from_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ResumeParsingError(
            "PDF parsing dependency missing. Install 'pypdf'."
        ) from exc

    try:
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as exc:  # pragma: no cover - parser internals
        raise ResumeParsingError("Failed to parse PDF resume.") from exc


def _extract_from_docx(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ResumeParsingError(
            "DOCX parsing dependency missing. Install 'python-docx'."
        ) from exc

    try:
        document = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:  # pragma: no cover - parser internals
        raise ResumeParsingError("Failed to parse DOCX resume.") from exc


def extract_text_from_upload(filename: str, content: bytes) -> str:
    """Extract plain text from a supported uploaded resume file."""
    if not filename:
        raise ResumeParsingError("Uploaded resume must include a filename.")

    lowered = filename.lower()
    if lowered.endswith(".txt"):
        return _decode_text(content)
    if lowered.endswith(".pdf"):
        return _extract_from_pdf(content)
    if lowered.endswith(".docx"):
        return _extract_from_docx(content)

    raise ResumeParsingError("Unsupported file type. Use .txt, .pdf, or .docx.")

