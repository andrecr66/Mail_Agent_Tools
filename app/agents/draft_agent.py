from __future__ import annotations
from app.agents.types import DraftRequest, DraftResponse
from app.tools.brand_loader import load_brand


class DraftAgent:
    def draft(self, req: DraftRequest) -> DraftResponse:
        name = req.recipient.name or req.recipient.email
        brand = load_brand(req.brand_id)

        # Subject: if company is present, "<Purpose Title>: <Company>", else "Welcome: For <name>"
        subject = (
            f"{req.purpose.title()}: {req.recipient.company}"
            if getattr(req.recipient, "company", None)
            else f"Welcome: For {name}"
        )

        bullets = []
        ctx = req.context or {}
        if isinstance(ctx.get("bullets"), list):
            bullets = [str(b) for b in ctx["bullets"] if str(b).strip()]

        lines = [f"Hi {name},", ""]
        if bullets:
            lines.append("Here are a few things to check out:")
            for b in bullets:
                lines.append(f"- {b}")
            lines.append("")
        else:
            lines.append("Thanks for connecting with us!")
            lines.append("")

        lines.append(f"Best,\n{brand.name}")
        body_text = "\n".join(lines)
        return DraftResponse(subject=subject, body_text=body_text)
