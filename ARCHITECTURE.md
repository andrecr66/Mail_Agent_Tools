Mail Agent Tools – Architecture Overview

Overview
- Purpose: Draft emails, iterate on content with user feedback (structured or natural language), render with a brand template, and draft/send via Gmail after explicit approval.
- Layers:
  - API: FastAPI app exposes draft/preview/deliver + iteration endpoints (`app/web/app.py`).
  - Agent: Deterministic `DraftAgent` composes subject/body seeds (`app/agents/draft_agent.py`).
  - Rendering: Jinja template + Premailer CSS inlining + plaintext derivation (`app/templating/*`).
  - Workflow: Orchestrates draft → render → preview/deliver (`app/mail/workflow.py`).
  - Gmail Ops: OAuth, labels, MIME composition, and draft/send (`app/google/*`).
  - Brands: Sender identity, styling, links, and policies (`brands/*`).

Request Flow
1) Client sends `DraftRequest` (recipient, purpose, brand, context variables).
2) `DraftAgent` returns a `DraftResponse` (subject, body_text) – deterministic to keep tests stable.
3) `render_generic_email` builds HTML + plain text using brand + variables.
4) `/mail/preview` returns a dry-run plan; `/mail/deliver` drafts or sends using Gmail.

Iteration
- Structured updates: `/draft/iterate/preview`, `/mail/iterate/deliver` accept fields like `bullets_add`, `bullets_replace`, `cta_text`, `cta_url`, `purpose`, `subject`, `tone`, `long_form`.
- Natural-language updates: `/draft/iterate/nl`, `/mail/iterate/nl-deliver` parse instructions to structured updates (`app/agents/interpret.py`).
- Update application merges into `DraftRequest.context` so the renderer sees changes (`_apply_updates`).

Templating
- Template: `templates/jinja/families/generic/generic_v1.html.j2` with header/footer/button partials.
- Variables: subject, preheader, body_text, cta_text/url, purpose, brand; long-form intro can be enabled via `context.long_form` (defaults to true for `purpose='welcome'`).
- Plaintext: Extracted from HTML via BeautifulSoup for readability.

Gmail Integration
- OAuth token loaded from `.secrets/google/token.json` (non-interactive by default: tests mock send).
- Labels: Ensures a hierarchy `<prefix>/<brand_id>` before applying.
- MIME: Text+HTML body, attachments per brand policy.

Testing
- Unit tests: Agent edges, brand loader, and renderer snapshot.
- Integration tests: ASGITransport calls endpoints in-process. Deliver calls are monkeypatched to avoid network.

Extensibility
- ADK tools (`adk_app/*`) invoke this API, enabling use as a tool/sub-agent. The default behavior is to preview first and draft by default; only send when explicitly approved.

