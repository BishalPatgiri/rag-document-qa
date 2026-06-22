from dataclasses import dataclass

import tiktoken

# text-embedding-3-* and gpt-4o* all use the cl100k_base / o200k families;
# cl100k_base is a safe token estimate for chunk sizing.
_encoding = tiktoken.get_encoding("cl100k_base")


@dataclass
class TextChunk:
    page: int
    text: str
    token_count: int


def chunk_pages(
    pages: list[str], chunk_size: int, overlap: int
) -> list[TextChunk]:
    """Split page texts into overlapping, token-bounded chunks.

    Chunking is done within each page so every chunk keeps a page number for
    citations. ``chunk_size`` and ``overlap`` are measured in tokens.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    step = chunk_size - overlap
    chunks: list[TextChunk] = []

    for page_number, text in enumerate(pages, start=1):
        if not text:
            continue
        tokens = _encoding.encode(text)
        start = 0
        while start < len(tokens):
            window = tokens[start : start + chunk_size]
            chunk_text = _encoding.decode(window).strip()
            if chunk_text:
                chunks.append(TextChunk(page_number, chunk_text, len(window)))
            if start + chunk_size >= len(tokens):
                break
            start += step

    return chunks
