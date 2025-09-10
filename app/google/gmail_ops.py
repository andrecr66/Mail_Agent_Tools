from __future__ import annotations
from typing import Any, Dict
import logging

from app.config.settings import settings
from app.google.oauth import ensure_user_credentials
from app.google.gmail_service import build_gmail_service
from app.google.gmail_labels import ensure_hierarchy
from app.google.mime import compose_email, to_gmail_raw


def draft_or_send_message(
    *,
    to: str,
    subject: str,
    html_body: str,
    text_body: str,
    brand_id: str = "default",
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
    attachments: list[str] | None = None,
    force_action: str | None = None,
) -> Dict[str, Any]:
    """Create a Gmail draft (default) or send immediately, then apply labels."""
    logger = logging.getLogger("mail.delivery")
    creds = ensure_user_credentials(interactive=False)
    svc = build_gmail_service(creds)

    # Build MIME + raw
    msg = compose_email(
        to=to,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
        brand_id=brand_id,
        from_email=from_email,
        from_name=from_name,
        reply_to=reply_to,
        attachments=attachments or [],
    )
    raw = to_gmail_raw(msg)

    # Ensure labels exist
    label_prefix = settings.MAIL_AGENT_GMAIL_LABEL_PREFIX
    label_ids = ensure_hierarchy(svc, label_prefix, brand_id)

    action = (force_action or settings.MAIL_AGENT_DEFAULT_ACTION).strip().lower()
    if action == "send":
        res = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
        msg_id = res.get("id")
        logger.info("gmail.send id=%s to=%s subject=%r", msg_id, to, subject)
    else:
        # create draft, then label the underlying message
        d = svc.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
        msg_id = d.get("message", {}).get("id")
        logger.info("gmail.draft id=%s to=%s subject=%r", msg_id, to, subject)

    # Apply labels to the message
    svc.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"addLabelIds": label_ids, "removeLabelIds": []},
    ).execute()

    return {"status": action, "id": str(msg_id), "labels_applied": label_ids}
"""Gmail delivery operations (draft/send + labeling)."""
