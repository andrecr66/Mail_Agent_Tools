#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "❌ Failed at line $LINENO"; exit 1' ERR

# --- 0) Restore stable workflow (idempotent) ---
cat > app/mail/workflow.py <<'PY'
from __future__ import annotations
from typing import Any, Dict, Tuple

from app.agents.draft_agent import DraftAgent
from app.agents.types import DraftRequest, DraftResponse
from app.templating.render import render_generic_email
from app.google.gmail_actions import dry_run_plan_send
from app.google.gmail_ops import draft_or_send_message

def generate(req: DraftRequest) -> DraftResponse:
    return DraftAgent().draft(req)

def render(req: DraftRequest, draft: DraftResponse) -> Tuple[str, str]:
    html, text = render_generic_email(
        subject=draft.subject,
        body_text=draft.body_text,
        brand_id=req.brand_id,
        purpose=req.purpose,
        variables=req.context or {},
    )
    return html, text

def preview(req: DraftRequest) -> Dict[str, Any]:
    draft = generate(req)
    html, text = render(req, draft)
    plan = dry_run_plan_send(
        to=req.recipient.email,
        subject=draft.subject,
    )
    return {"subject": draft.subject, "html": html, "text": text, "plan": plan}

def deliver(req: DraftRequest, force_action: str | None = None) -> Dict[str, Any]:
    draft = generate(req)
    html, text = render(req, draft)
    res = draft_or_send_message(
        to=req.recipient.email,
        subject=draft.subject,
        html_body=html,
        text_body=text,
        brand_id=req.brand_id,
        force_action=force_action,
    )
    res["to"] = req.recipient.email
    res["subject"] = draft.subject
    return res
PY

# --- 1) Kill anything on 8080 and start clean ---
pkill -f 'uvicorn .*app.web.app:app' 2>/dev/null || true
PIDS="$(lsof -ti tcp:8080 || ss -ltnp 2>/dev/null | awk '/:8080/ {print $NF}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p')"
[ -n "${PIDS:-}" ] && kill $PIDS 2>/dev/null || true
sleep 0.3
[ -n "${PIDS:-}" ] && kill -9 $PIDS 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

MAIL_AGENT_DEFAULT_ACTION=draft \
CORS_ORIGINS='http://localhost:5173,http://127.0.0.1:5173' \
.venv/bin/uvicorn app.web.app:app --host 0.0.0.0 --port 8080 --reload > .uv.log 2>&1 & echo $! > .uv.pid

BASE=http://localhost:8080

# Wait for health
for i in $(seq 1 50); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health" || true)
  [ "$code" = "200" ] && break
  sleep 0.1
done

echo "== Admin =="
curl -s "$BASE/health"   | jq .
curl -s "$BASE/version"  | jq .
curl -s "$BASE/settings" | jq .

# --- 2) Draft/Preview/Deliver sanity ---
cat > req.json <<'JSON'
{
  "recipient": {"email":"pat@example.com","name":"Pat","company":"Acme"},
  "purpose":"outreach",
  "brand_id":"default",
  "context":{
    "cta_text":"Visit CodeRoad",
    "cta_url":"https://coderoad.com/",
    "bullets":["Explore docs","Book a demo"]
  }
}
JSON

echo "== Draft =="
curl -s "$BASE/draft" -H 'content-type: application/json' --data-binary @req.json \
| jq -r '.subject, .body_text'

echo "== Preview =="
curl -s "$BASE/mail/preview" -H 'content-type: application/json' --data-binary @req.json \
| jq '{subject, plan:.plan.action, hasCTA:(.html|test("Visit CodeRoad"))}'

echo "== Deliver (draft) =="
curl -s -D .hdr -o deliver.json "$BASE/mail/deliver?mode=draft" \
  -H 'content-type: application/json' --data-binary @req.json
head -1 .hdr
jq '{status,id,labels:.labels_applied[0:2]}' deliver.json
