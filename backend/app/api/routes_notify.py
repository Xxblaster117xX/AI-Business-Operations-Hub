from fastapi import APIRouter
from pydantic import BaseModel

from app.integrations import slack_client

router = APIRouter()


class SlackNotifyRequest(BaseModel):
    text: str


@router.post("/api/notify/slack")
def notify_slack(req: SlackNotifyRequest) -> dict:
    return slack_client.notify(req.text)
