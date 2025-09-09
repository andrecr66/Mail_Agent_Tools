# mypy: disable-error-code=import-untyped
from __future__ import annotations
from typing import Any, Dict, Tuple, cast

from bs4 import BeautifulSoup
from premailer import transform

from app.tools.brand_loader import load_brand
from app.templating.env import render_template, jinja_env


def derive_preheader(plain_text: str, limit: int = 90) -> str:
    s = " ".join(plain_text.split())
    return s[:limit]


def to_plain_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    txt: str = soup.get_text(separator=" ", strip=True)
    return " ".join(txt.split())


def inline_css(html: str) -> str:
    # premailer returns Any to mypy; cast to str for our contract
    return cast(str, transform(html, disable_validation=True))


def render_generic_email(
    *,
    subject: str,
    body_text: str,
    brand_id: str = "default",
    purpose: str = "generic",
    variables: Dict[str, Any] | None = None,
) -> Tuple[str, str]:
    """
    Render the generic_v1 Jinja template with a brand and content variables.
    Returns (html_inlined, plaintext).
    """
    brand = load_brand(brand_id)
    vars = variables or {}
    preheader = vars.get("preheader") or derive_preheader(body_text)
    cta_text = vars.get("cta_text") or "Learn more"
    cta_url = vars.get("cta_url") or brand.links.get("website") or "#"

    # Re-render dynamic footer/signature strings as Jinja templates
    env = jinja_env()
    footer_html = brand.footer_html
    signature_html = brand.signature_html
    if footer_html:
        footer_html = env.from_string(footer_html).render(
            brand=brand, subject=subject, body_text=body_text, purpose=purpose, **vars
        )
    if signature_html:
        signature_html = env.from_string(signature_html).render(
            brand=brand, subject=subject, body_text=body_text, purpose=purpose, **vars
        )

    context = {
        "brand": brand,
        "subject": subject,
        "preheader": preheader,
        "body_text": body_text,
        "cta_text": cta_text,
        "cta_url": cta_url,
        "purpose": purpose,
        "footer_html": footer_html,
        "signature_html": signature_html,
    }
    raw_html = render_template("families/generic/generic_v1.html.j2", context)
    html = inline_css(raw_html)
    text = to_plain_text(html)
    return html, text
