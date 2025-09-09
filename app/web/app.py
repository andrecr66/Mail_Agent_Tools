from __future__ import annotations
from fastapi import FastAPI, Query

from app.agents.draft_agent import DraftAgent
from app.agents.types import DraftRequest, DraftResponse
from app.mail.types import PreviewResponse, SendResult
from app.mail.workflow import preview as wf_preview, deliver as wf_deliver
from app.web.cors import install_cors

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
