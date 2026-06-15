import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from .config import settings

logger = logging.getLogger("proxy")

TELEGRAM_API = "https://api.telegram.org"

telegram_client: httpx.AsyncClient | None = None
rf_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_client, rf_client
    telegram_client = httpx.AsyncClient(verify=True)
    rf_client = httpx.AsyncClient(verify=False)
    yield
    await telegram_client.aclose()
    await rf_client.aclose()


app = FastAPI(title="Telegram Proxy Bridge", lifespan=lifespan)


def strip_hop_headers(headers: dict) -> dict:
    hop = {
        "connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailers",
        "transfer-encoding", "upgrade", "host",
    }
    return {k: v for k, v in headers.items() if k.lower() not in hop}


@app.post("/api/{path:path}")
async def proxy_to_telegram(path: str, request: Request):
    auth = request.headers.get("X-Proxy-Auth")
    if auth != settings.auth_key:
        return JSONResponse(
            {"ok": False, "error": "Unauthorized"}, status_code=403
        )

    body = await request.body()
    url = f"{TELEGRAM_API}/{path}"
    if request.url.query_string:
        url += f"?{request.url.query_string.decode()}"

    headers = {}
    ct = request.headers.get("content-type")
    if ct:
        headers["content-type"] = ct

    try:
        resp = await telegram_client.post(url, content=body, headers=headers)
    except httpx.RequestError as e:
        logger.error("Telegram request failed: %s", e)
        return JSONResponse(
            {"ok": False, "error": str(e)}, status_code=502
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=strip_hop_headers(dict(resp.headers)),
    )


@app.post("/webhook/{token:path}")
async def proxy_webhook(token: str, request: Request):
    body = await request.body()

    headers = {}
    ct = request.headers.get("content-type")
    if ct:
        headers["content-type"] = ct

    url = f"{settings.rf_server_url}/webhook/{token}"

    try:
        resp = await rf_client.post(url, content=body, headers=headers)
    except httpx.RequestError as e:
        logger.error("Webhook forward failed: %s", e)
        return JSONResponse(
            {"ok": False, "error": str(e)}, status_code=502
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=strip_hop_headers(dict(resp.headers)),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
