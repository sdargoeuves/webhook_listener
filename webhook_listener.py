import asyncio
import json
import sys
from datetime import datetime, timezone
from pydantic import BaseSettings
from typing import List

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.AristaCvp import AristaCvpWebhook
from modules.functions import action_ipfabric, write_logs


class Settings(BaseSettings):
    LOG_FOLDER = "logs"
    BASE_URL = "http://localhost"
    DEFAULT_PORT = 8080
    USE_NGROK = True


settings = Settings()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home_page(request: Request):
    context = {"title": "Arista CloudVision & IP Fabric"}
    return templates.TemplateResponse(
        "index.html", {"request": request, "context": context}, status_code=200
    )


@app.post("/ipf-webhook")
async def receive_webhook(
    request: Request, cvp_webhooks: List[AristaCvpWebhook]
) -> HTMLResponse:
    # data = await request.json()
    print(f"Webhook sent by Arista: {cvp_webhooks}")
    timestamp = f"{datetime.now(timezone.utc).isoformat()}"
    write_logs(timestamp, cvp_webhooks, settings.LOG_FOLDER)
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
    write_logs(timestamp, simulated_webhooks, settings.LOG_FOLDER)
    return templates.TemplateResponse(
        "test_webhook.html",
        {"request": request, "simulated_webhook": pretty_webhook},
        status_code=200,
    )


async def log_reader(n=1):
    log_lines = []
    timestamp = f"{datetime.now(timezone.utc).isoformat()}"
    today_log_file = f"log_{timestamp[:10]}.txt"
    with open(f"{settings.LOG_FOLDER}/{today_log_file}", "r") as file:
        lines = file.readlines()
        lines.reverse()  # Reverse the order of the lines
        for line in lines[:n]:
            if "ERROR" in line:
                log_lines.append(f'<span class="error-line"">{line}</span><br/>')
            elif "WARNING" in line:
                log_lines.append(f'<span class="warning-line"">{line}</span><br/>')
            elif "TEST" in line:
                log_lines.append(f'<span class="test-line"">{line}</span><br/>')
            else:
                log_lines.append(f'<span class="regular-line">{line}</span><br/>')
            log_lines.append("<br/>")
        return log_lines


@app.websocket("/ws/log")
async def websocket_endpoint_log(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await asyncio.sleep(1)
            logs = await log_reader(10)
            await websocket.send_text(logs)
    except Exception as e:
        print(e)
    finally:
        await websocket.close()


@app.get("/logs")
async def get(request: Request):
    timestamp = f"{datetime.now(timezone.utc).isoformat()}"
    today_log_file = f"log_{timestamp[:10]}.txt"
    context = {
        "title": "AristaCVP Webhook - Log Viewer over WebSockets",
        "log_file": f"{settings.LOG_FOLDER}/{today_log_file}",
        "base_url": settings.BASE_URL,
        "port": settings.DEFAULT_PORT,
    }
    return templates.TemplateResponse(
        "log.html", {"request": request, "context": context}
    )


def main():
    # start ngrok and show the URL to use
    if settings.USE_NGROK:
        # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
        from pyngrok import ngrok

        # Get the server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
        settings.DEFAULT_PORT = (
            sys.argv[sys.argv.index("--port") + 1]
            if "--port" in sys.argv
            else settings.DEFAULT_PORT
        )
        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(settings.DEFAULT_PORT).public_url
        print(
            f'ngrok tunnel "{public_url}" -> "http://127.0.0.1:{settings.DEFAULT_PORT}"'
        )
        # Update any base URLs or webhooks to use the public ngrok URL
        settings.BASE_URL = public_url
    uvicorn.run(app, host="0.0.0.0", port=settings.DEFAULT_PORT, log_level="info")


if __name__ == "__main__":
    main()
