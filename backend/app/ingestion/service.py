from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Chunk, Document
from app.ingestion.chunker import chunk_pages
from app.ingestion.embedder import embed_texts
from app.ingestion.pdf import extract_pages


class EmptyDocumentError(ValueError):
    """Raised when a PDF yields no extractable text."""


async def ingest_pdf(
    session: AsyncSession, filename: str, data: bytes
) -> Document:
    """Extract -> chunk -> embed -> store a PDF. Returns the saved Document."""
    pages = extract_pages(data)
    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise EmptyDocumentError("No extractable text found in the PDF.")

    vectors, _ = await embed_texts([c.text for c in chunks])

    document = Document(
        filename=filename,
        status="ready",
        page_count=len(pages),
        chunk_count=len(chunks),
    )
    session.add(document)
    await session.flush()  # assign document.id

    session.add_all(
        Chunk(
            document_id=document.id,
            ordinal=i,
            page=chunk.page,
            content=chunk.text,
            token_count=chunk.token_count,
            embedding=vector,
        )
        for i, (chunk, vector) in enumerate(zip(chunks, vectors))
    )
    await session.commit()
    await session.refresh(document)
    return document
