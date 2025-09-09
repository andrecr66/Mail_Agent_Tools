from __future__ import annotations
from typing import Any, Dict, Optional, Iterable
import os
from .mail_tools import preview_mail, preview_mail_nl, deliver_mail

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


def _first_present(d: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    for k in keys:
        v = d.get(k)
        if v is not None and v != "":
            return v
    return None


def _maybe_find_email(d: Dict[str, Any]) -> Optional[str]:
    # Prefer common keys
    for key in (
        "email",
        "to",
        "recipient_email",
        "recipientEmail",
        "recipient",
        "address",
        "email_address",
        "recipient_email_address",
        "recipientEmailAddress",
    ):
        v = d.get(key)
        if isinstance(v, str) and "@" in v:
            return v
        if isinstance(v, dict):
            v2 = v.get("email")
            if isinstance(v2, str) and "@" in v2:
                return v2
    # Shallow scan
    for v in d.values():
        if isinstance(v, str) and "@" in v:
            return v
    return None


def _ensure_defaults(base: Dict[str, Any]) -> Dict[str, Any]:
    # Normalize into DraftRequest shape; do not mutate caller’s dict
    out: Dict[str, Any] = {
        "recipient": {},
        "purpose": str(_first_present(base, ("purpose", "email_purpose", "type", "category")) or "welcome"),
        "brand_id": str(_first_present(base, ("brand_id", "brandId", "brand", "sender_brand")) or "default"),
        "context": dict(base.get("context") or {}),
    }

    # Recipient normalization
    if isinstance(base.get("recipient"), dict):
        out["recipient"] = dict(base["recipient"])  # copy
    elif isinstance(base.get("recipient"), str) and "@" in str(base.get("recipient")):
        out["recipient"] = {"email": str(base.get("recipient"))}
    else:
        email = _maybe_find_email(base)
        name = _first_present(base, ("name", "recipient_name", "recipientName", "full_name", "first_name"))
        if email:
            out["recipient"] = {"email": email}
            if name:
                out["recipient"]["name"] = str(name)

    # Fallback name = email if missing
    rec = out["recipient"]
    if isinstance(rec, dict) and rec.get("email") and not rec.get("name"):
        rec["name"] = rec.get("email")

    ctx = out["context"]
    purpose = str(out["purpose"]).lower()
    bullets = ctx.get("bullets") or []
    if not bullets:
        ctx["bullets"] = DEFAULT_BY_PURPOSE.get(purpose, DEFAULT_BY_PURPOSE["welcome"])[:4]

    if not ctx.get("cta_text"):
        ctx["cta_text"] = CTA_BY_PURPOSE.get(purpose, "Get started")
    if not ctx.get("cta_url"):
        ctx["cta_url"] = "https://coderoad.com/"

    if os.getenv("DEBUG_MAIL_TOOLS"):
        print("[smart_preview] normalized base:", out)

    return out


async def smart_preview(base: Dict[str, Any]) -> Dict[str, Any]:
    return await preview_mail(_ensure_defaults(base))


async def smart_preview_nl(base: Dict[str, Any], instructions: str) -> Dict[str, Any]:
    # still ensure sensible defaults before NL iteration
    seeded = _ensure_defaults(base)
    return await preview_mail_nl(seeded, instructions)


async def smart_deliver(
    base: Dict[str, Any],
    updates: Optional[Dict[str, Any]] = None,
    mode: str = "draft",
) -> Dict[str, Any]:
    seeded = _ensure_defaults(base)
    return await deliver_mail(seeded, updates, mode=mode)


async def smart_deliver_nl(
    base: Dict[str, Any],
    instructions: str,
    mode: str = "draft",
) -> Dict[str, Any]:
    seeded = _ensure_defaults(base)
    # Reuse deliver_mail_nl via mail_tools (through agent wiring), or call API directly
    # Here we call preview first is optional; we directly deliver with NL updates
    from .mail_tools import deliver_mail_nl

    return await deliver_mail_nl(seeded, instructions, mode=mode)
