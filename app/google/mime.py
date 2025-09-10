from __future__ import annotations
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from pathlib import Path
from typing import Sequence
import base64
import mimetypes

from app.tools.brand_loader import load_brand


def compose_email(
    *,
    to: str,
    subject: str,
    html_body: str,
    text_body: str,
    brand_id: str = "default",
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
    attachments: Sequence[str] | None = None,
    inline_images: bool | None = None,
) -> EmailMessage:
    """
    Build a multipart/alternative email with optional attachments.
    Uses brand defaults (from_name/from_email/reply_to if provided in brand).
    """
    brand = load_brand(brand_id)
    msg = EmailMessage()

    # From
    be = from_email or brand.from_email
    bn = from_name or brand.from_name or brand.name
    msg["From"] = f"{bn} <{be}>" if be else bn

    # To / Subject / Reply-To / Date / Message-Id
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to or brand.reply_to:
        msg["Reply-To"] = reply_to or brand.reply_to
    msg["Date"] = formatdate(localtime=True)
    msg["Message-Id"] = make_msgid("coderoad-agent")

    # Body (text + html)
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    # Attachments (respect brand policy)
    if attachments:
        allowed = set(brand.attachments_policy.allowed)
        max_mb = float(brand.attachments_policy.max_size_mb)
        for p in attachments:
            path = Path(p)
            if not path.exists():
                raise FileNotFoundError(path)
            ext = (path.suffix or "").lower().lstrip(".")
            if ext not in allowed:
                raise ValueError(f"Attachment type '.{ext}' not allowed by policy {allowed}")
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > max_mb:
                raise ValueError(f"Attachment {path.name} too large ({size_mb:.2f}MB > {max_mb}MB)")
            ctype, enc = mimetypes.guess_type(str(path))
            maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
            with path.open("rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=path.name)

    return msg


def to_gmail_raw(msg: EmailMessage) -> str:
    """Base64url for Gmail 'raw' field."""
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
"""MIME composition utilities for building text+HTML emails with attachments."""
