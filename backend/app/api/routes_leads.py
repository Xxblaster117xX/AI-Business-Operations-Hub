from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.integrations import email_client
from app.models.db_models import Lead
from app.models.schemas import ApprovalResult, FollowupResult, LeadOut
from app.services.followup import check_and_followup

router = APIRouter()


@router.get("/api/leads", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db)) -> list[Lead]:
    return db.scalars(select(Lead).order_by(Lead.created_at.desc())).all()


@router.get("/api/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


class ReplyUpdate(BaseModel):
    replied: bool = True


@router.patch("/api/leads/{lead_id}/reply", response_model=LeadOut)
def mark_replied(lead_id: int, update: ReplyUpdate, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.replied = update.replied
    lead.status = "replied" if update.replied else lead.status
    db.commit()
    db.refresh(lead)
    return lead


@router.post("/api/leads/{lead_id}/approve", response_model=ApprovalResult)
def approve_lead(lead_id: int, db: Session = Depends(get_db)) -> ApprovalResult:
    """Human approves an AI-drafted response that was held back by the
    confidence guardrail (requires_approval=True), and it gets sent for real."""
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if not lead.requires_approval:
        return ApprovalResult(lead_id=lead.id, action="already_resolved")

    email_result = email_client.send_email(
        to=lead.email,
        subject=f"Re: {lead.need or 'your request'}",
        body=lead.ai_response or "",
    )

    lead.requires_approval = False
    lead.status = "approved_sent"
    db.commit()

    return ApprovalResult(lead_id=lead.id, action="sent", email_result=email_result)


@router.post("/api/leads/{lead_id}/followup", response_model=FollowupResult)
def trigger_followup(lead_id: int, force: bool = False, db: Session = Depends(get_db)) -> FollowupResult:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if force:
        lead.next_followup_at = datetime.now(timezone.utc)
    return check_and_followup(db, lead)
