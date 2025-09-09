from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Optional
import json
import re
from pydantic import BaseModel, Field, ValidationError

HEX_COLOR = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")


class UTMDefaults(BaseModel):
    source: str = "agent"
    medium: str = "email"
    campaign: str = "generic"


class UnsubscribePolicy(BaseModel):
    required_for: list[str] = Field(default_factory=lambda: ["newsletter", "outreach"])
    url: Optional[str] = None


class AttachmentsPolicy(BaseModel):
    allowed: list[str] = Field(default_factory=lambda: ["pdf", "png", "jpg", "jpeg"])
    max_size_mb: int = 10


class BrandConfig(BaseModel):
    # Required
    name: str

    # Visuals / layout
    logo_url: Optional[str] = None
    primary: str = "#2563EB"
    secondary: str = "#111827"
    background: str = "#FFFFFF"
    text_color: str = "#111827"
    content_width_px: int = 600
    font_family: str = "Arial, Helvetica, sans-serif"
    button_radius_px: int = 6

    # Links & copy blocks
    links: dict[str, Optional[str]] = Field(default_factory=dict)
    signature_html: Optional[str] = None
    footer_html: Optional[str] = None
    legal_address: Optional[str] = None

    # Sending metadata
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None
    label_prefix: str = "Agent-Sent"

    # Behavior
    utm_defaults: UTMDefaults = Field(default_factory=UTMDefaults)
    unsubscribe: UnsubscribePolicy = Field(default_factory=UnsubscribePolicy)
    attachments_policy: AttachmentsPolicy = Field(default_factory=AttachmentsPolicy)
    inline_images: bool = False

    def validate_semantics(self) -> None:
        for k in ("primary", "secondary", "background", "text_color"):
            v = getattr(self, k, None)
            if v and not HEX_COLOR.match(v):
                raise ValueError(f"Invalid color for {k}: {v}")
        if self.logo_url and not self.logo_url.startswith(("http", "cid:", "data:")):
            raise ValueError(f"Unexpected logo_url scheme: {self.logo_url}")


DEFAULTS: dict[str, object] = {
    "primary": "#2563EB",
    "secondary": "#111827",
    "background": "#FFFFFF",
    "text_color": "#111827",
    "links": {},
    "footer_html": "",
    "signature_html": "",
}


class BrandNotFound(FileNotFoundError):
    """Brand folder/brand.json is missing."""


@lru_cache(maxsize=64)
def load_brand(brand_id: str, base_dir: str | Path = "brands") -> BrandConfig:
    """Load, default, and validate a brand configuration."""
    base = Path(base_dir)
    path = base / brand_id / "brand.json"
    if not path.exists():
        raise BrandNotFound(f"Brand '{brand_id}' not found at {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    for k, v in DEFAULTS.items():
        raw.setdefault(k, v)

    try:
        cfg = BrandConfig(**raw)
        cfg.validate_semantics()
        return cfg
    except (ValidationError, ValueError) as e:
        raise ValueError(f"Invalid brand config for '{brand_id}': {e}") from e
