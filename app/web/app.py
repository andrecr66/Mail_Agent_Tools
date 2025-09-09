from __future__ import annotations
from fastapi import FastAPI, Query

from app.agents.draft_agent import DraftAgent
from app.agents.types import DraftRequest, DraftResponse
from app.mail.types import PreviewResponse, SendResult
from app.mail.workflow import preview as wf_preview, deliver as wf_deliver
from app.web.cors import install_cors
from pydantic import BaseModel
from typing import Any, Dict


app = FastAPI(title="Mail Agent Tools - Draft API")
install_cors(app)
_agent = DraftAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/draft", response_model=DraftResponse)
def draft(req: DraftRequest) -> DraftResponse:
    return _agent.draft(req)


@app.post("/mail/preview", response_model=PreviewResponse)
def mail_preview(req: DraftRequest) -> PreviewResponse:
    data = wf_preview(req)
    return PreviewResponse(**data)


@app.post("/mail/deliver", response_model=SendResult)
def mail_deliver(
    req: DraftRequest,
    mode: str | None = Query(default=None, pattern="^(draft|send)$"),
) -> SendResult:
    data = wf_deliver(req, force_action=mode)
    return SendResult(**data)


@app.get("/version")
def version() -> dict[str, str]:
    try:
        from importlib.metadata import version as _v

        return {"version": _v("mail-agent-tools")}
    except Exception:
        return {"version": "0.0.0+local"}


@app.get("/settings")
def get_settings() -> dict[str, str]:
    from app.config.settings import settings

    return {
        "MAIL_AGENT_DEFAULT_ACTION": settings.MAIL_AGENT_DEFAULT_ACTION,
        "MAIL_AGENT_GMAIL_LABEL_PREFIX": settings.MAIL_AGENT_GMAIL_LABEL_PREFIX,
        "MAIL_AGENT_BRAND_ID": settings.MAIL_AGENT_BRAND_ID,
    }


# ---------- Iteration endpoints for chat-driven review/approval ----------
class DraftUpdate(BaseModel):
    # If set, replaces the whole bullets list; otherwise we can append with bullets_add
    bullets_replace: list[str] | None = None
    bullets_add: list[str] = []
    cta_text: str | None = None
    cta_url: str | None = None
    purpose: str | None = None


def _apply_updates(base: DraftRequest, updates: DraftUpdate) -> DraftRequest:
    ctx = dict(base.context or {})
    if updates.bullets_replace is not None:
        ctx["bullets"] = [b for b in updates.bullets_replace if str(b).strip()]
    elif updates.bullets_add:
        existing = [str(b) for b in ctx.get("bullets", []) if str(b).strip()]
        ctx["bullets"] = existing + [b for b in updates.bullets_add if str(b).strip()]
    if updates.cta_text is not None:
        ctx["cta_text"] = updates.cta_text
    if updates.cta_url is not None:
        ctx["cta_url"] = updates.cta_url
    if updates.purpose is not None:
        base.purpose = updates.purpose
    base.context = ctx
    return base


@app.post("/draft/iterate", response_model=DraftResponse)
def draft_iterate(base: DraftRequest, updates: DraftUpdate) -> DraftResponse:
    req2 = _apply_updates(base, updates)
    return _agent.draft(req2)


@app.post("/draft/iterate/preview", response_model=PreviewResponse)
def draft_iterate_preview(base: DraftRequest, updates: DraftUpdate) -> PreviewResponse:
    req2 = _apply_updates(base, updates)
    data = wf_preview(req2)
    return PreviewResponse(**data)


@app.post("/mail/iterate/deliver")
def mail_iterate_deliver(
    base: DraftRequest,
    updates: DraftUpdate,
    mode: str = "draft",
) -> Dict[str, Any]:
    req2 = _apply_updates(base, updates)
    data = wf_deliver(req2, force_action=mode)
    return data


from pydantic import BaseModel
from app.agents.interpret import interpret_instructions

class NLUpdate(BaseModel):
    instructions: str

@app.post("/draft/iterate/nl", response_model=PreviewResponse)
def draft_iterate_nl(base: DraftRequest, updates: NLUpdate) -> PreviewResponse:
    parsed = interpret_instructions(updates.instructions)
    req2 = _apply_updates(base, DraftUpdate(**parsed))
    data = wf_preview(req2)
    return PreviewResponse(**data)

@app.post("/mail/iterate/nl-deliver")
def mail_iterate_nl_deliver(base: DraftRequest, updates: NLUpdate, mode: str = "draft") -> Dict[str, Any]:
    parsed = interpret_instructions(updates.instructions)
    req2 = _apply_updates(base, DraftUpdate(**parsed))
    return wf_deliver(req2, force_action=mode)
