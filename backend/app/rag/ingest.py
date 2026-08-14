"""Chunk the company-knowledge markdown docs, embed them with Gemini, and
load them into the pgvector-backed knowledge_chunks table.

Run with:  python -m app.rag.ingest
"""

from __future__ import annotations

import re
from pathlib import Path

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models.db_models import KnowledgeChunk
from app.rag.embeddings import embed_text

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split on markdown headers/paragraphs first, then hard-wrap long ones."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[str] = []
    buffer = ""
    for para in paragraphs:
        candidate = f"{buffer}\n\n{para}".strip() if buffer else para
        if len(candidate) <= size:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
        if len(para) <= size:
            buffer = para
        else:
            start = 0
            while start < len(para):
                chunks.append(para[start:start + size])
                start += size - overlap
            buffer = ""
    if buffer:
        chunks.append(buffer)
    return chunks


def load_documents(knowledge_dir: Path) -> list[tuple[str, str, str]]:
    """Returns list of (source_path, department, content)."""
    docs = []
    for path in sorted(knowledge_dir.rglob("*.md")):
        department = path.relative_to(knowledge_dir).parts[0]
        content = path.read_text(encoding="utf-8")
        docs.append((str(path.relative_to(knowledge_dir)), department, content))
    return docs


def ingest(knowledge_dir: Path | None = None) -> int:
    knowledge_dir = knowledge_dir or settings.knowledge_dir
    Base.metadata.create_all(bind=engine, tables=[KnowledgeChunk.__table__])

    docs = load_documents(knowledge_dir)
    if not docs:
        print(f"No markdown files found under {knowledge_dir.resolve()}")
        return 0

    db = SessionLocal()
    total = 0
    try:
        db.query(KnowledgeChunk).delete()
        for source_path, department, content in docs:
            for chunk in chunk_text(content):
                vector = embed_text(chunk, task_type="RETRIEVAL_DOCUMENT")
                db.add(
                    KnowledgeChunk(
                        source_path=source_path,
                        department=department,
                        content=chunk,
                        embedding=vector,
                    )
                )
                total += 1
        db.commit()
    finally:
        db.close()

    print(f"Ingested {total} chunks from {len(docs)} documents into knowledge_chunks.")
    return total


if __name__ == "__main__":
    ingest()
