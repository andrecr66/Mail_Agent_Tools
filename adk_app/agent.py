from __future__ import annotations
import os

# Try both import paths across ADK versions
try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.function_tool import FunctionTool
except Exception:  # pragma: no cover
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool

from adk_app.tools.mail_tools import preview_mail, deliver_mail, preview_mail_nl, deliver_mail_nl

MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

# Minimal signature: just pass the function
preview_tool = FunctionTool(preview_mail)
deliver_tool = FunctionTool(deliver_mail)
preview_nl_tool = FunctionTool(preview_mail_nl)
deliver_nl_tool = FunctionTool(deliver_mail_nl)

INSTRUCTIONS = """
You help users compose emails safely with an approval loop.

Flow:
1) Gather base fields if missing: recipient email, (optional) name, purpose, brand (default 'default').
2) Always show a preview FIRST using `preview_mail` (or `preview_mail_nl` when the user gives NL changes).
3) If the user requests changes, call preview again with updates:
   - bullets_replace / bullets_add
   - cta_text / cta_url
   - purpose
   Edge cases handled by backend:
     • No bullets → “Thanks for connecting with us!”
     • Missing name → greet by email
     • No CTA → HTML still valid
4) Only when the user explicitly approves, call `deliver_mail` with mode="draft".
   Do NOT use mode="send" unless the user insists.
5) Summarize results (subject + key changes). Avoid dumping full HTML unless asked.
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
