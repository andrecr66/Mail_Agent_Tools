from typing import Any
import pytest
from httpx import AsyncClient, ASGITransport
from app.web.app import app
import app.mail.workflow as wf  # for monkeypatching

BASE_REQ: dict[str, Any] = {
    "recipient": {"email": "pat@example.com", "name": "Pat"},
    "purpose": "welcome",
    "brand_id": "default",
    "context": {"bullets": ["Explore docs"]},
}
UPD: dict[str, Any] = {"bullets_add": ["Contact support"]}


async def test_iterate_deliver_draft(anyio_backend: str, monkeypatch: pytest.MonkeyPatch) -> None:
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
        body: dict[str, Any] = {"base": BASE_REQ, "updates": UPD, "mode": "draft"}
        r = await ac.post("/mail/iterate/deliver", json=body)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "draft"
        assert "labels_applied" in data
