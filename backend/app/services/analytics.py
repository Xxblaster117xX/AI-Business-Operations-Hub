from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.db_models import Lead, RequestLog
from app.models.schemas import AnalyticsResponse

HOURLY_RATE_EUR = 25.0


def compute_metrics(db: Session) -> AnalyticsResponse:
    total_leads = db.scalar(select(func.count(Lead.id))) or 0
    auto_resolved = db.scalar(select(func.count(Lead.id)).where(Lead.requires_approval.is_(False))) or 0

    avg_cost = db.scalar(select(func.avg(RequestLog.estimated_cost)).where(RequestLog.endpoint == "analyze")) or 0.0
    avg_before = db.scalar(select(func.avg(RequestLog.manual_minutes_baseline))) or 8.0
    avg_after = db.scalar(select(func.avg(RequestLog.manual_minutes_actual))) or 1.7

    total_requests = db.scalar(select(func.count(RequestLog.id))) or 0
    successful = db.scalar(select(func.count(RequestLog.id)).where(RequestLog.success.is_(True))) or 0

    automation_rate = (auto_resolved / total_leads * 100) if total_leads else 0.0
    success_rate = (successful / total_requests * 100) if total_requests else 100.0

    minutes_saved_per_request = float(avg_before) - float(avg_after)
    hours_saved = (minutes_saved_per_request * total_leads) / 60
    saving_eur = hours_saved * HOURLY_RATE_EUR

    return AnalyticsResponse(
        requests_processed=total_leads,
        automatically_resolved=auto_resolved,
        automation_rate=round(automation_rate, 1),
        average_ai_cost=round(float(avg_cost), 4),
        manual_minutes_before=round(float(avg_before), 1),
        manual_minutes_after=round(float(avg_after), 1),
        estimated_hours_saved_month=round(hours_saved, 1),
        estimated_saving_month_eur=round(saving_eur, 2),
        workflow_success_rate=round(success_rate, 1),
    )
