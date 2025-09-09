from __future__ import annotations
from typing import Any
from app.templating.render import render_generic_email


def test_generic_v1_html_snapshot(snapshot: Any) -> None:
    html, text = render_generic_email(
        subject="Welcome to CodeRoad",
        body_text="Hello!\n\nThis is a short paragraph.\nAnd a second line.",
        brand_id="default",
        purpose="welcome",
        variables={"cta_text": "Visit CodeRoad", "cta_url": "https://coderoad.com/"},
    )
    assert html == snapshot
    assert len(text) > 10
