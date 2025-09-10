Developer Guide – Running with ADK Web UI

Prereqs
- Python 3.12, virtualenv created at `.venv` with requirements installed.
- Environment variables:
  - `MAIL_API_BASE` → URL for the API (default: `http://localhost:8080`).
  - `GOOGLE_API_KEY` → API key for ADK (Gemini). Store securely (not in VCS).

Run the API
- Start FastAPI locally:
  - `.venv/bin/uvicorn app.web.app:app --host 0.0.0.0 --port 8080 --reload`

Run ADK Web UI
- In another terminal (same env):
  - `export MAIL_API_BASE=http://localhost:8080`
  - `export GOOGLE_API_KEY=...` (your key)
  - `adk web` (or `adk web --app adk_app` if not auto-detected)

Using the UI
- Provide recipient, purpose, and optional brand (default `default`).
- Click preview; iterate using structured inputs or natural language (e.g., “tone: friendly; subject: Welcome; add bullets: Explore docs; Book a demo; set cta text: Start trial”).
- When satisfied, the agent will ask: “Draft to Gmail or Send now?” Choose one (defaults to Draft).

Notes
- Delivery integration is live only if Gmail OAuth token exists at `.secrets/google/token.json`. Tests mock delivery.
- Brands are under `brands/<id>/brand.json`; default id is `default`.

Troubleshooting Gmail send
- If preview/draft works but send doesn’t show up in Sent or Inbox:
  1) Confirm which Gmail account the token belongs to:
     - `.venv/bin/python -c "from app.google.oauth import ensure_user_credentials; from app.google.gmail_service import build_gmail_service; c=ensure_user_credentials(interactive=False); s=build_gmail_service(c); print(s.users().getProfile(userId='me').execute())"`
  2) Check API response after deliver: it returns `{status: 'send'|'draft', id, labels_applied, to, subject}`.
  3) Ensure the token has required scopes. If not, re-run interactive auth once:
     - `.venv/bin/python -c "from app.google.oauth import ensure_user_credentials as e; e(interactive=True)"`
  4) In Gmail, search for the applied label (default prefix `Agent-Sent`) or check All Mail.
