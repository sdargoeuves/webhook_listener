import json
import pathlib
import httpx
from datetime import datetime, timezone
from typing import List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.AristaCvp import AristaCvpWebhook
from modules.functions import action_ipfabric, write_logs

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home_page():
    html_content = pathlib.Path("static/home.html").read_text()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/ipf-webhook")
async def receive_webhook(
    request: Request, cvp_webhooks: List[AristaCvpWebhook]
) -> HTMLResponse:
    # data = await request.json()
    print(f"Webhook sent by Arista: {cvp_webhooks}")
    timestamp = f"{datetime.now(timezone.utc).isoformat()}"
    write_logs(timestamp, cvp_webhooks)
    action_ipfabric(timestamp, cvp_webhooks)
    return HTMLResponse(content="<h3>IPF Webhook Received</h3>", status_code=202)


@app.get("/simulate-cvp-webhook", response_class=HTMLResponse)
async def test_webhook(request: Request, simulated_webhooks=None) -> HTMLResponse:
    if simulated_webhooks is None:
        with open("static/webhook_example_down.json", "r") as file:
            try:
                simulated_webhooks = json.load(file)  # Parse the JSON data
            except json.JSONDecodeError:
                simulated_webhooks = [{"invalid_json": True}]
    pretty_webhook = json.dumps(simulated_webhooks, indent=4)
    timestamp = f"{datetime.now(timezone.utc).isoformat()}"
    # edit timestamp of the file, and comment to show it's a TEST
    # ...
    write_logs(timestamp, simulated_webhooks)
    return templates.TemplateResponse(
        "test_webhook.html",
        {"request": request, "simulated_webhook": pretty_webhook},
        status_code=200,
    )


# @app.get("/simulate-cvp-webhook2", response_class=HTMLResponse)
# async def test_webhook2(request: Request, simulated_webhooks=None) -> HTMLResponse:
#     if simulated_webhooks is None:
#         with open("static/webhook_example_down.json", "r") as file:
#             try:
#                 simulated_webhooks = json.load(file)  # Parse the JSON data
#             except json.JSONDecodeError:
#                 simulated_webhooks = [{"invalid_json": True}]
#     pretty_webhook = json.dumps(simulated_webhooks, indent=4)
#     # encoded_data = simulated_webhooks.encode('utf-8')
#     headers = {
#         'accept': 'application/json',
#         'Content-Type': 'application/json',
#         'Location': '/ipf-webhook'
#     }
#     # return Response(content=pretty_webhook, status_code=307, headers=headers)
#     response = httpx.post("http://localhost:8081/ipf-webhook", headers=headers, data=pretty_webhook)
#     if response.status_code == 202:
#         return templates.TemplateResponse(
#             "test_webhook.html",
#             {"request": request, "simulated_webhook": pretty_webhook},
#             status_code=200,
#         )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="debug")
