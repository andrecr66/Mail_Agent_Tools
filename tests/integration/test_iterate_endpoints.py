from typing import Any
from httpx import AsyncClient, Response

from httpx import ASGITransport
from app.web.app import app

BASE_REQ = {
    "recipient": {"email": "pat@example.com", "name": "Pat"},
    "purpose": "welcome",
    "brand_id": "default",
    "context": {
        "bullets": ["Explore docs"],
        "cta_text": "Visit CodeRoad",
        "cta_url": "https://coderoad.com/",
    },
}
UPD_REPLACE = {
    "bullets_replace": ["Book a demo", "See pricing"],
    "cta_text": "Start trial",
    "cta_url": "https://coderoad.com/start",
}


async def _iter_preview(
    client: AsyncClient, base: dict[str, Any], updates: dict[str, Any]
) -> Response:
    body = {"base": base, "updates": updates}
    return await client.post("/draft/iterate/preview", json=body)


async def test_iterate_preview_applies_updates(anyio_backend: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await _iter_preview(ac, BASE_REQ, UPD_REPLACE)
        assert r.status_code == 200
        data = r.json()
        assert "subject" in data and "html" in data and "text" in data and "plan" in data
        assert "Start trial" in data["html"]


async def test_iterate_bullets_append(anyio_backend: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        upd = {"bullets_add": ["Contact support"]}
        r = await _iter_preview(ac, BASE_REQ, upd)
        assert r.status_code == 200
        data = r.json()
        assert "Contact support" in data["text"]


async def test_iterate_deliver_draft(anyio_backend: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        body = {"base": BASE_REQ, "updates": UPD_REPLACE, "mode": "draft"}
        r = await ac.post("/mail/iterate/deliver", json=body)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "draft"
        assert data["to"] == "pat@example.com"
        assert "labels_applied" in data and len(data["labels_applied"]) >= 2
