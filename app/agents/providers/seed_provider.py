from __future__ import annotations
from app.agents.types import DraftRequest, DraftResponse


def _titlecase(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _derive_subject(req: DraftRequest) -> str:
    who = req.recipient.name or req.recipient.company or req.recipient.email
    purpose = _titlecase(req.purpose)
    return f"{purpose}: For {who}"


def _derive_body(req: DraftRequest) -> str:
    parts: list[str] = []
    greet = f"Hi {req.recipient.name}," if req.recipient.name else "Hello,"
    parts.append(greet)
    parts.append("")
    if req.body_hint:
        parts.append(req.body_hint)
        parts.append("")
    else:
        parts.append(f"This is a {req.purpose} message from CodeRoad.")
        parts.append("")
    bullets = req.context.get("bullets", [])
    if isinstance(bullets, list) and bullets:
        parts.append("Key points:")
        for b in bullets:
            parts.append(f"- {b}")
        parts.append("")
    parts.append("Best regards,")
    parts.append("CodeRoad Team")
    return "\n".join(parts)


class SeedProvider:
    """Deterministic provider to drive tests; swap for ADK later."""

    def generate(self, req: DraftRequest) -> DraftResponse:
        return DraftResponse(subject=_derive_subject(req), body_text=_derive_body(req))
