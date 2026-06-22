import io

from pypdf import PdfReader


def extract_pages(data: bytes) -> list[str]:
    """Extract text per page from a PDF byte stream.

    Returns one string per page (empty string for pages with no extractable
    text). Index 0 is page 1.
    """
    reader = PdfReader(io.BytesIO(data))
    return [(page.extract_text() or "").strip() for page in reader.pages]
