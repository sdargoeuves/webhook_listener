from typing import Any, Dict, List
from pydantic import BaseModel
from datetime import datetime


class CvpComponent(BaseModel):
    deviceId: str
    entityId: str
    hostname: str
    tags: Dict[str, Any]
    type: str


class AristaCvpWebhook(BaseModel):
    acknowledged: bool
    components: List[CvpComponent]
    description: str
    event_type: str
    fired_at: datetime
    is_firing: bool
    is_test: bool
    key: str
    resolved_at: datetime
    severity: str
    source: str
    title: str
