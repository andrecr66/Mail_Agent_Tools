from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, EmailStr


class PreviewResponse(BaseModel):
    subject: str
    html: str
    text: str
    plan: dict[str, Any]


class SendResult(BaseModel):
    status: Literal["draft", "send"]
    id: str
    labels_applied: list[str]
    to: EmailStr
    subject: str
