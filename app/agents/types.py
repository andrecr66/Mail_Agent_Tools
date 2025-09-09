from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr


class Recipient(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None


class DraftRequest(BaseModel):
    recipient: Recipient
    purpose: str = Field(default="generic", description="welcome|newsletter|outreach|generic...")
    brand_id: str = "default"
    tone: str = "neutral"
    subject_hint: Optional[str] = None
    body_hint: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)


class DraftResponse(BaseModel):
    subject: str
    body_text: str
