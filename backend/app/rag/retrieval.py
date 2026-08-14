from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import KnowledgeChunk
from app.models.schemas import KnowledgeSearchResult
from app.rag.embeddings import embed_query


def search(db: Session, query: str, department: str | None = None, top_k: int = 5) -> list[KnowledgeSearchResult]:
    query_vector = embed_query(query)

    distance = KnowledgeChunk.embedding.cosine_distance(query_vector)
    stmt = select(KnowledgeChunk, distance.label("distance"))
    if department:
        stmt = stmt.where(KnowledgeChunk.department == department)
    stmt = stmt.order_by(distance).limit(top_k)

    rows = db.execute(stmt).all()
    return [
        KnowledgeSearchResult(
            source_path=chunk.source_path,
            department=chunk.department,
            content=chunk.content,
            similarity=round(1 - dist, 4),
        )
        for chunk, dist in rows
    ]
