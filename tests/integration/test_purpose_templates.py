from __future__ import annotations
from typing import Any
import pytest
from httpx import AsyncClient, ASGITransport

from app.web.app import app

pytestmark = [pytest.mark.anyio, pytest.mark.parametrize("anyio_backend", ["asyncio"])]


async def _preview(payload: dict[str, Any]) -> dict[str, Any]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/mail/preview", json=payload)
        assert r.status_code == 200
        return r.json()


async def test_newsletter_preview_uses_template(anyio_backend: str) -> None:
    payload: dict[str, Any] = {
        "recipient": {"email": "reader@example.com", "name": "Reader", "company": "Acme"},
        "purpose": "newsletter",
        "brand_id": "default",
        "context": {"bullets": ["Highlights", "Upcoming webinars"]},
    }
    data = await _preview(payload)
    # Basic shape
    for k in ("subject", "html", "text", "plan"):
        assert k in data
    # Subject includes purpose when company present
    assert "Newsletter" in data["subject"]
    # Content contains our bullets
    assert "Highlights" in data["text"]


async def test_outreach_preview_uses_template(anyio_backend: str) -> None:
    payload: dict[str, Any] = {
        "recipient": {"email": "prospect@example.com", "name": "Fin", "company": "Acme"},
        "purpose": "outreach",
        "brand_id": "default",
        "context": {"bullets": ["Two use cases", "Short intro"]},
    }
    data = await _preview(payload)
    assert "Outreach" in data["subject"]
    assert "Two use cases" in data["text"]

