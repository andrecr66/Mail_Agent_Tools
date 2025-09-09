from typing import Any
from httpx import AsyncClient, ASGITransport
from app.web.app import app

BASE_REQ: dict[str, Any] = {
    "recipient": {"email": "pat@example.com", "name": "Pat"},
    "purpose": "welcome",
    "brand_id": "default",
    "context": {"bullets": ["Explore docs"]},
}
UPD: dict[str, Any] = {"bullets_add": ["Contact support"]}


async def test_iterate_deliver_draft(anyio_backend: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        body: dict[str, Any] = {"base": BASE_REQ, "updates": UPD, "mode": "draft"}
        r = await ac.post("/mail/iterate/deliver", json=body)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "draft"
        assert "labels_applied" in data
