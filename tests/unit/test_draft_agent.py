from __future__ import annotations
from app.agents.draft_agent import DraftAgent
from app.agents.types import DraftRequest, Recipient


def test_draft_minimal() -> None:
    agent = DraftAgent()
    req = DraftRequest(recipient=Recipient(email="pat@example.com", name="Pat"), purpose="welcome")
    resp = agent.draft(req)
    assert "Welcome" in resp.subject
    assert "Hi Pat" in resp.body_text


def test_draft_with_bullets() -> None:
    agent = DraftAgent()
    req = DraftRequest(
        recipient=Recipient(email="fin@acme.com", company="Acme"),
        purpose="outreach",
        context={"bullets": ["Try CodeRoad", "Cut cycle time by 20%"]},
    )
    resp = agent.draft(req)
    assert "- Try CodeRoad" in resp.body_text
    assert "Acme" in resp.subject
