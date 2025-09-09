from __future__ import annotations
from typing import Any
import pytest
from httpx import AsyncClient, ASGITransport

from app.web.app import app
import app.mail.workflow as wf  # for monkeypatching

# Run with anyio but pin the backend to asyncio only (avoid Trio deps)
pytestmark = [pytest.mark.anyio, pytest.mark.parametrize("anyio_backend", ["asyncio"])]

PREVIEW_PAYLOAD: dict[str, Any] = {
    "recipient": {"email": "pat@example.com", "name": "Pat"},
    "purpose": "welcome",
    "brand_id": "default",
    "context": {"cta_text": "Visit CodeRoad", "cta_url": "https://coderoad.com/"},
}


async def test_mail_preview_roundtrip(anyio_backend: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/mail/preview", json=PREVIEW_PAYLOAD)
        assert r.status_code == 200
        data = r.json()
        # shape checks
        for k in ("subject", "html", "text", "plan"):
            assert k in data
        # content sanity
        assert "Welcome" in data["subject"]
        assert "Visit CodeRoad" in data["html"]
        assert "Visit CodeRoad" in data["text"]
        # plan sanity
        assert data["plan"]["action"] in ("draft", "send")
        assert "Agent-Sent" in " ".join(data["plan"]["labels"])


SEND_PAYLOAD = dict(PREVIEW_PAYLOAD)  # deliver uses same DraftRequest shape


async def test_mail_deliver_roundtrip(anyio_backend: str, monkeypatch: pytest.MonkeyPatch) -> None:
    # avoid real Gmail by faking the send function the workflow module uses
    def fake_send(**kwargs: Any) -> dict[str, Any]:
        return {
            "status": "draft",
            "id": "test-message-id",
            "labels_applied": ["Label_1", "Label_2"],
            "to": kwargs["to"],
            "subject": kwargs["subject"],
        }

    monkeypatch.setattr(wf, "draft_or_send_message", fake_send, raising=False)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/mail/deliver", json=SEND_PAYLOAD)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("draft", "send")
        assert data["id"]
        assert data["to"] == SEND_PAYLOAD["recipient"]["email"]
        assert "Welcome" in data["subject"]
