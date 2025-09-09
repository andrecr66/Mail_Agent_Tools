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


def _apply_subject_and_tone(data: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    # Subject override
    subj = str(ctx.get("subject") or "").strip()
    if subj:
        data["subject"] = subj

    # Optional long-form rephrasing using bullets + CTA for a natural intro
    if ctx.get("long_form") or ctx.get("tone"):
        tone = str(ctx.get("tone") or "friendly").lower()
        name = ctx.get("recipient_name") or ctx.get("recipient_email") or "there"
        cta_text = str(ctx.get("cta_text") or "").strip()
        bullets = ctx.get("bullets") or []

        lines: list[str] = []
        if tone in {"formal"}:
            lines.append(f"Hello {name},")
        elif tone in {"enthusiastic", "warm"}:
            lines.append(f"Hi {name} — welcome! We're thrilled to have you.")
        else:
            lines.append(f"Hi {name}, and welcome!")

        if bullets:
            lines.append("Here’s how to get the most out of your first days:")
            for b in bullets[:4]:
                lines.append(f"• {b}")
        if cta_text:
            lines.append(f"When you’re ready, {cta_text.lower()} to take the next step.")
        lines.append("If anything feels unclear, just reply to this email—happy to help.")
        lines.append("Best,")
        lines.append("The Team")

        long_text = "\n".join(lines).strip()
        orig = (data.get("text") or "").strip()
        data["text"] = (long_text + ("\n\n" + orig if orig else "")).strip()

    return data
