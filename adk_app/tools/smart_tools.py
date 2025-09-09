from __future__ import annotations
from typing import Any, Dict
from .mail_tools import preview_mail, preview_mail_nl

DEFAULT_BY_PURPOSE: dict[str, list[str]] = {
    "welcome": [
        "Get started with docs and templates",
        "Book a 15-min onboarding call",
        "Explore best-practice examples",
        "Join our community for tips & support",
    ],
    "newsletter": [
        "Highlights from this week’s releases",
        "Upcoming webinars and office hours",
        "Customer stories and how-tos you may like",
    ],
    "promo": [
        "Limited-time discount for new users",
        "Bundle offer for teams",
        "Early access to upcoming features",
    ],
    "outreach": [
        "How we can help your team right now",
        "Two relevant use cases in your industry",
        "Offer to share a tailored demo",
    ],
    "notice": [
        "What’s changing and when",
        "Any action needed from you",
        "Link to full details and support",
    ],
    "maintenance": [
        "Maintenance window & expected impact",
        "Affected services",
        "Where to track live status",
    ],
}

CTA_BY_PURPOSE: dict[str, str] = {
    "welcome": "Start your trial",
    "newsletter": "Read the update",
    "promo": "Claim your offer",
    "outreach": "Book a quick demo",
    "notice": "Read the notice",
    "maintenance": "See status page",
}


def _ensure_defaults(base: Dict[str, Any]) -> Dict[str, Any]:
    # Copy-ish update (we don't mutate the caller’s dict)
    out: Dict[str, Any] = {
        "recipient": base.get("recipient") or {},
        "purpose": base.get("purpose") or "welcome",
        "brand_id": base.get("brand_id") or "default",
        "context": dict(base.get("context") or {}),
    }
    ctx = out["context"]

    purpose = str(out["purpose"]).lower()
    bullets = ctx.get("bullets") or []
    if not bullets:
        ctx["bullets"] = DEFAULT_BY_PURPOSE.get(purpose, DEFAULT_BY_PURPOSE["welcome"])[:4]

    if not ctx.get("cta_text"):
        ctx["cta_text"] = CTA_BY_PURPOSE.get(purpose, "Get started")
    if not ctx.get("cta_url"):
        # Gentle default; your template already tolerates empty CTA
        ctx["cta_url"] = "https://coderoad.com/"

    return out


async def smart_preview(base: Dict[str, Any]) -> Dict[str, Any]:
    return await preview_mail(_ensure_defaults(base))


async def smart_preview_nl(base: Dict[str, Any], instructions: str) -> Dict[str, Any]:
    # still ensure sensible defaults before NL iteration
    seeded = _ensure_defaults(base)
    return await preview_mail_nl(seeded, instructions)
