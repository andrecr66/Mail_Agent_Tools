from app.agents.draft_agent import DraftAgent
from app.agents.types import DraftRequest, Recipient
from app.mail.workflow import preview


def test_no_bullets_fallback() -> None:
    agent = DraftAgent()
    req = DraftRequest(
        recipient=Recipient(email="pat@example.com", name="Pat"), purpose="welcome", context={}
    )
    resp = agent.draft(req)
    assert "Thanks for connecting with us!" in resp.body_text


def test_missing_name_uses_email() -> None:
    agent = DraftAgent()
    req = DraftRequest(recipient=Recipient(email="fin@acme.com", name=None), purpose="welcome")
    resp = agent.draft(req)
    assert "Hi fin@acme.com" in resp.body_text


def test_truncates_bullets_to_5() -> None:
    agent = DraftAgent()
    bullets = [f"Item {i}" for i in range(1, 9)]  # 8 bullets
    req = DraftRequest(
        recipient=Recipient(email="pat@example.com", name="Pat"),
        purpose="welcome",
        context={"bullets": bullets},
    )
    resp = agent.draft(req)
    # First 5 included, the 6th not included
    assert "- Item 5" in resp.body_text
    assert "- Item 6" not in resp.body_text


def test_no_cta_still_renders_html() -> None:
    # Ensure the preview renders valid HTML even if CTA text/url are absent
    req = DraftRequest(
        recipient=Recipient(email="pat@example.com", name="Pat"), purpose="welcome", context={}
    )
    data = preview(req)
    assert "subject" in data and "html" in data and "text" in data and "plan" in data
    assert "<" in data["html"]  # very light sanity: looks like HTML
