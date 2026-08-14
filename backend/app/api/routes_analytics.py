from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.schemas import AnalyticsResponse
from app.services.analytics import compute_metrics

router = APIRouter()


@router.get("/api/analytics", response_model=AnalyticsResponse)
def analytics(db: Session = Depends(get_db)) -> AnalyticsResponse:
    return compute_metrics(db)
