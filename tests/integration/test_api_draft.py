from __future__ import annotations
from typing import Any
import pytest
from httpx import AsyncClient, ASGITransport
from app.web.app import app

# Run with anyio but pin the backend to asyncio only
pytestmark = [pytest.mark.anyio, pytest.mark.parametrize("anyio_backend", ["asyncio"])]


async def test_api_draft_roundtrip(anyio_backend: str) -> None:  # param injected by anyio
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload: dict[str, Any] = {
            "recipient": {"email": "pat@example.com", "name": "Pat"},
            "purpose": "welcome",
            "context": {"bullets": ["Explore docs", "Book a demo"]},
        }
        r = await ac.post("/draft", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "Welcome" in data["subject"]
        assert "Explore docs" in data["body_text"]
