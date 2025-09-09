# mypy: disable-error-code=import-untyped
from __future__ import annotations
from typing import Any
from typing import Dict, Tuple, cast

from bs4 import BeautifulSoup
from premailer import transform

from app.tools.brand_loader import load_brand
from app.templating.env import render_template, jinja_env


def _clean_context_for_render(ctx: dict[str, Any] | None) -> dict[str, Any]:
    d = dict(ctx or {})
    # Avoid colliding with explicit kwargs passed to .render()
    d.pop("subject", None)
    return d



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
    if vars.get("subject"):
        subject = str(vars["subject"])
    preheader = vars.get("preheader") or derive_preheader(body_text)
    cta_text = vars.get("cta_text") or "Learn more"
    cta_url = vars.get("cta_url") or brand.links.get("website") or "#"

    # Optional long-form intro
    if vars.get("long_form") or vars.get("tone"):
        tone = str(vars.get("tone") or "friendly").lower()
        name = vars.get("recipient_name") or vars.get("recipient_email") or "there"
        bullets = vars.get("bullets") or []
        cta_text = (vars.get("cta_text") or "").strip()
        lines = []
        if tone in {"formal", "professional"}:
            lines.append(f"Hello {name},")
            lines.append("Welcome aboard—it's a pleasure to have you with us.")
        elif tone in {"warm", "enthusiastic", "friendly"}:
            lines.append(f"Hi {name} — welcome! We're thrilled to have you.")
        else:
            lines.append(f"Hi {name}, welcome!")
        if bullets:
            lines.append("To make your first days smooth, here are a few quick wins:")
            for b in bullets[:4]:
                lines.append(f"• {b}")
        else:
            # Provide a more substantial intro (~80–120 words when combined with signature/body)
            lines.append(
                "To help you get value fast, we suggest exploring a couple of real examples, "
                "reviewing a short quickstart, and trying one small task end‑to‑end."
            )
            lines.append(
                "Most new users create their first draft in minutes and then iterate—" 
                "if anything feels unclear, we’re here to help."
            )
        if cta_text:
            lines.append(f"When you're ready, {cta_text[0].lower() + cta_text[1:]}")
        lines.append("If anything feels unclear, just reply—happy to help.")
        lines.append("Best,\nThe Team")
        intro = "\n".join(lines).strip()
        body_text = (intro + ("\n\n" + body_text if body_text else "")).strip()

    # Re-render dynamic footer/signature strings as Jinja templates
    env = jinja_env()
    footer_html = brand.footer_html
    signature_html = brand.signature_html
    cleaned_vars = {k: v for k, v in (vars or {}).items() if k != "subject"}
    if footer_html:
        footer_html = env.from_string(footer_html).render(
            brand=brand, subject=subject, body_text=body_text, purpose=purpose, **cleaned_vars
        )
    if signature_html:
        signature_html = env.from_string(signature_html).render(
            brand=brand, subject=subject, body_text=body_text, purpose=purpose, **cleaned_vars
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
