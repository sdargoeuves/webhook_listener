import os
from dotenv import load_dotenv, find_dotenv
from typing import Any, Dict, List
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from datetime import datetime

load_dotenv(find_dotenv(), override=True)


class Settings(BaseSettings):
    BASE_URL: str = "http://localhost"
    LOG_FOLDER: str = os.getenv("LOG_FOLDER", "logs")
    HTTP_PORT: int = int(os.getenv("HTTP_PORT", 8080))
    USE_NGROK: bool = eval(os.getenv("USE_NGROK", "False").title())

    IPF_URL: str = os.getenv("IPF_URL")
    IPF_TOKEN: str = os.getenv("IPF_TOKEN")
    IPF_SNAPSHOT_ID: str = os.getenv("IPF_SNAPSHOT_ID", "$last")
    IPF_VERIFY: bool = eval(os.getenv("IPF_VERIFY", "False").title())


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
