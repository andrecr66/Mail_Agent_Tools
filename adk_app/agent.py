from __future__ import annotations
import os

# Try both import paths across ADK versions
try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.function_tool import FunctionTool
except Exception:  # pragma: no cover
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool

from adk_app.tools.mail_tools import preview_mail_nl
from adk_app.tools.smart_tools import smart_preview, smart_preview_nl, smart_deliver, smart_deliver_nl

MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

# Minimal signature: just pass the function
preview_tool = FunctionTool(smart_preview)
deliver_tool = FunctionTool(smart_deliver)
preview_nl_tool = FunctionTool(smart_preview_nl)
deliver_nl_tool = FunctionTool(smart_deliver_nl)

INSTRUCTIONS = """
You help users compose emails safely with an approval loop.

Flow:
1) Gather base fields if missing: recipient email, (optional) name, purpose, brand (default 'default').
2) Always show a preview FIRST using `preview_mail` (or `preview_mail_nl` when the user gives NL changes).
3) If the user requests changes, call preview again with updates:
   - bullets_replace / bullets_add
   - cta_text / cta_url
   - purpose / subject / tone / long_form
   Edge cases handled by backend:
     • No bullets → “Thanks for connecting with us!”
     • Missing name → greet by email
     • No CTA → HTML still valid
4) Before delivery, explicitly ask: “Draft to Gmail or Send now?” Default to "draft".
   When the user approves, call `deliver_mail` with `mode` set to the choice.
   Never send without explicit approval.
5) Summarize results (subject + key changes). Avoid dumping full HTML unless asked.

Error handling with tools:
- The tools may return an object with `ok: false`, `status_code`, and an `error_json.detail` list if the API rejects the payload.
- If you see `status_code=422` or `ok=false`, ask the user for the missing fields and retry once:
  • At minimum the API requires recipient email. Name is optional (you can reuse the email as the name).
  • If the user gave a flat email (e.g., `andre@example.com`), proceed; the backend normalizes it.
"""

root_agent = LlmAgent(
    name="mail_companion",
    model=MODEL,
    description="Email drafting assistant with explicit approval loop.",
    instruction=INSTRUCTIONS,
    tools=[preview_tool, deliver_tool, preview_nl_tool, deliver_nl_tool],
)


# ADK Web top-level export
agent = root_agent
