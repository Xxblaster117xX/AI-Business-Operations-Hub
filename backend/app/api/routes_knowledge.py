from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.schemas import KnowledgeSearchRequest, KnowledgeSearchResult
from app.rag.retrieval import search

router = APIRouter()


@router.post("/api/knowledge/search", response_model=list[KnowledgeSearchResult])
def knowledge_search(req: KnowledgeSearchRequest, db: Session = Depends(get_db)) -> list[KnowledgeSearchResult]:
    return search(db, query=req.query, department=req.department, top_k=req.top_k)
