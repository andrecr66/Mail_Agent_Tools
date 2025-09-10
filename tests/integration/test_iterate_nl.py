from typing import Any
import pytest
from httpx import AsyncClient, Response
from httpx import ASGITransport
from app.web.app import app
import app.mail.workflow as wf  # for monkeypatching

BASE_REQ: dict[str, Any] = {
    "recipient": {"email": "pat@example.com", "name": "Pat"},
    "purpose": "welcome",
    "brand_id": "default",
    "context": {
        "bullets": ["Explore docs"],
        "cta_text": "Visit CodeRoad",
        "cta_url": "https://coderoad.com/",
    },
}


async def _iter_nl_preview(
    client: AsyncClient, base: dict[str, Any], instructions: str
) -> Response:
    body = {"base": base, "updates": {"instructions": instructions}}
    return await client.post("/draft/iterate/nl", json=body)


async def test_iterate_nl_preview_adds_bullets_and_cta(anyio_backend: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        instr = "add bullets: Book a demo; See pricing; set cta text: Start trial; set cta url: https://coderoad.com/start"
        r = await _iter_nl_preview(ac, BASE_REQ, instr)
        assert r.status_code == 200
        data = r.json()
        assert "Start trial" in data["html"]
        assert "Book a demo" in data["text"]
        assert "See pricing" in data["text"]


async def test_iterate_nl_deliver_draft(anyio_backend: str, monkeypatch: pytest.MonkeyPatch) -> None:
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
        body = {
            "base": BASE_REQ,
            "updates": {"instructions": "replace bullets: One, Two; remove cta"},
            "mode": "draft",
        }
        r = await ac.post("/mail/iterate/nl-deliver", json=body)
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "draft"
        assert d["to"] == "pat@example.com"
        assert "labels_applied" in d
