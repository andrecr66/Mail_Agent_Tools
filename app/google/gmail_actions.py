from __future__ import annotations
from app.config.settings import settings


def dry_run_plan_send(*, to: str, subject: str) -> dict:
    # Deterministic, side-effect-free plan used by /mail/preview
    # Tests expect the label prefix "Agent-Sent" to be present.
    return {"action": "draft", "labels": [f"{settings.MAIL_AGENT_GMAIL_LABEL_PREFIX}/Draft"]}
