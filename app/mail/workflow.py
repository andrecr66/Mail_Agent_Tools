from __future__ import annotations
from typing import Any, Dict, Tuple

from app.agents.draft_agent import DraftAgent
from app.agents.types import DraftRequest, DraftResponse
from app.templating.render import render_generic_email
from app.google.gmail_actions import dry_run_plan_send
from app.google.gmail_ops import draft_or_send_message


def generate(req: DraftRequest) -> DraftResponse:
    return DraftAgent().draft(req)


def render(req: DraftRequest, draft: DraftResponse) -> Tuple[str, str]:
    html, text = render_generic_email(
        subject=draft.subject,
        body_text=draft.body_text,
        brand_id=req.brand_id,
        purpose=req.purpose,
        variables=req.context or {},
    )
    return html, text


def preview(req: DraftRequest) -> Dict[str, Any]:
    draft = generate(req)
    html, text = render(req, draft)
    plan = dry_run_plan_send(to=req.recipient.email, subject=draft.subject)
    return {"subject": draft.subject, "html": html, "text": text, "plan": plan}


def deliver(req: DraftRequest, force_action: str | None = None) -> Dict[str, Any]:
    draft = generate(req)
    html, text = render(req, draft)
    res = draft_or_send_message(
        to=req.recipient.email,
        subject=draft.subject,
        html_body=html,
        text_body=text,
        brand_id=req.brand_id,
        force_action=force_action,
    )
    res["to"] = req.recipient.email
    res["subject"] = draft.subject
    return res
