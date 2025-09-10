from __future__ import annotations
from app.config.settings import settings


def dry_run_plan_send(*, to: str, subject: str) -> dict[str, object]:
    # Deterministic, side-effect-free plan used by /mail/preview
    # Tests expect the label prefix "Agent-Sent" to be present.
    return {"action": "draft", "labels": [f"{settings.MAIL_AGENT_GMAIL_LABEL_PREFIX}/Draft"]}
"""Side-effect-free preview of a Gmail plan.

Used by `/mail/preview` to describe what labels would be applied and whether
the action would draft or send — without requiring network access to Gmail.
"""
