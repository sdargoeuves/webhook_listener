

import pathlib
from datetime import datetime
from typing import Any, Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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


@app.get("/")
async def home_page():
    html_content = pathlib.Path("static/home.html").read_text()
    # with open("static/home.html", "r") as f:
    #     html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/ipf-webhook")
async def print_webhook(request: Request, cvp_webhook: List[AristaCvpWebhook]) -> HTMLResponse:
    data = (await request.json())
    print(f"Webhook sent by Arista: {cvp_webhook}")
    print(f"request: {request}")
    return HTMLResponse(
        content=f"<h3>IPF Webhook</h3><br>{data}",
        status_code=202
    )

@app.get("/simulate-cvp-webhook", response_class=HTMLResponse)
async def test_webhook(request: Request, simulated_webhook=None) -> HTMLResponse:
    if simulated_webhook is None:
        with open('static/webhook_example_down.json', 'r') as file:
            try:
                simulated_webhook = json.load(file)  # Parse the JSON data
            except json.JSONDecodeError:
                simulated_webhook = {"invalid_json": True}
    pretty_webhook = json.dumps(simulated_webhook, indent=4)
    return templates.TemplateResponse(
        "test_webhook.html", {"request": request, "simulated_webhook": simulated_webhook},
        status_code=200
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="debug")


