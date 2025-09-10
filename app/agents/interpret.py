from __future__ import annotations
import re
from typing import Any, Dict, List

# Heuristics-based parser that turns natural-language instructions
# into the DraftUpdate fields we already support.

_BULLET_SPLIT = re.compile(r"[;,]\s*")

DEFAULT_BY_PURPOSE: Dict[str, List[str]] = {
    "welcome": [
        "Get started quickly with our docs and templates",
        "Book a 15-min onboarding call if you'd like a walkthrough",
        "Explore examples to see best practices in action",
        "Join our community forum for tips and support",
    ],
    "newsletter": [
        "Highlights from this week's releases",
        "Upcoming webinars and office hours",
        "Customer stories and how-tos you may like",
    ],
    "promo": [
        "Limited-time discount for new users",
        "Bundle offer for teams getting started",
        "Early access to upcoming features",
    ],
    "outreach": [
        "Short intro on how we can help your team",
        "Two relevant use cases seen in your industry",
        "Offer to share a tailored demo or example",
    ],
    "notice": [
        "Summary of the change and when it takes effect",
        "What you need to do (if anything)",
        "Links to the full details and support",
    ],
    "maintenance": [
        "Maintenance window and expected impact",
        "What services are affected",
        "Where to track status in real time",
    ],
}

QA_RESPONSIBILITIES: List[str] = [
    "Develop and execute test plans and cases",
    "Automate regression and smoke tests where practical",
    "Log, track, and verify defects through resolution",
    "Collaborate with engineering to reproduce issues",
    "Report quality metrics and release readiness",
]


def _extract_list(text: str) -> List[str]:
    parts = _BULLET_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def interpret_instructions(instructions: str) -> Dict[str, Any]:
    instr = instructions.strip()
    up: Dict[str, Any] = {}

    # Replace bullets
    m = re.search(r"(?:replace|set)\s+bullets(?:\s+with)?\s*:\s*(.+)", instr, flags=re.I)
    if m:
        up["bullets_replace"] = _extract_list(m.group(1))

    # Add bullets
    m = re.search(r"(?:add|append)\s+bullets?\s*:\s*(.+)", instr, flags=re.I)
    if m:
        up["bullets_add"] = _extract_list(m.group(1))

    # Clear/remove bullets entirely
    if re.search(r"\b(clear|remove|drop)\s+bullets?\b", instr, flags=re.I):
        up["bullets_replace"] = []

    # CTA text
    m = re.search(
        r"(?:set\s+)?cta\s*text\s*(?:to)?\s*[:=]\s*['\"]?(.+?)['\"]?(?:\s|$)", instr, flags=re.I
    )
    if m:
        up["cta_text"] = m.group(1).strip()

    # CTA url
    m = re.search(r"(?:set\s+)?cta\s*url\s*(?:to)?\s*[:=]\s*['\"]?(\S+)['\"]?", instr, flags=re.I)
    if m:
        up["cta_url"] = m.group(1).strip()

    # Remove CTA entirely
    if re.search(r"\b(remove|clear|drop|no)\s+(cta|button)\b", instr, flags=re.I):
        up["cta_text"] = ""
        up["cta_url"] = ""

    # Subject override
    m = re.search(
        r"(?:set\s+)?subject\s*(?:to)?\s*[:=]\s*['\"]?(.+?)['\"]?(?:\s|$)", instr, flags=re.I
    )
    if m:
        up["subject"] = m.group(1).strip()

    # Tone setting (explicit)
    m = re.search(
        r"(?:set\s+)?tone\s*(?:to)?\s*[:=]\s*['\"]?([A-Za-z ]+)['\"]?",
        instr,
        flags=re.I,
    )
    if m:
        up["tone"] = m.group(1).strip().lower()

    # Tone heuristics via keywords
    # Prefer mapping "more friendly / friendlier" to "warm" so the change is visible.
    if re.search(r"\b(a\s+little\s+(bit\s+)?more\s+friendly|more\s+friendly|friendlier)\b", instr, flags=re.I):
        up["tone"] = "warm"
    elif re.search(r"\b(friendly|welcom(ing|e))\b", instr, flags=re.I):
        up.setdefault("tone", "friendly")
    if re.search(r"\b(warm|warmer|more\s+warm|more\s+welcoming|more\s+personal|softer|kinder|less\s+formal)\b", instr, flags=re.I):
        up.setdefault("tone", "warm")
    if re.search(r"\b(excit(ed|ing)|more\s+excited|enthusiastic|more\s+enthusiastic)\b", instr, flags=re.I):
        up.setdefault("tone", "enthusiastic")
    if re.search(r"\b(formal|more\s+formal|professional|more\s+professional)\b", instr, flags=re.I):
        up.setdefault("tone", "professional")
    if re.search(r"\b(casual|more\s+casual)\b", instr, flags=re.I):
        up.setdefault("tone", "casual")

    # If tone was requested and long_form not specified, enable long_form to
    # produce a clearly distinct intro in the template.
    if "tone" in up and "long_form" not in up:
        up["long_form"] = True

    # Length / detail hints
    if re.search(r"\b(short(en)?|more\s+concise|tighter)\b", instr, flags=re.I):
        up["long_form"] = False

    # Purpose
    m = re.search(
        r"(?:set\s+)?purpose\s*(?:to)?\s*[:=]\s*['\"]?([A-Za-z][A-Za-z -]+)['\"]?",
        instr,
        flags=re.I,
    )
    if m:
        up["purpose"] = m.group(1).strip().lower()

    # ---------- Heuristics for vague asks / length ----------
    if re.search(
        r"\b(more (helpful|detailed|useful|informative)|make.*longer|expand|add\s+detail|>\s*50\s*words)\b",
        instr,
        flags=re.I,
    ):
        if "bullets_add" not in up and "bullets_replace" not in up:
            purpose = up.get("purpose", "welcome")
            up["bullets_add"] = DEFAULT_BY_PURPOSE.get(purpose, DEFAULT_BY_PURPOSE["welcome"])
        if "cta_text" not in up:
            up["cta_text"] = "Get started"
        up.setdefault("long_form", True)

    # ---------- Role responsibilities (e.g., QA/AQ engineer) ----------
    if re.search(r"\b(QA|AQ|quality\s*assurance)\s+engineer\b", instr, flags=re.I):
        if "bullets_replace" not in up and "bullets_add" not in up:
            up["bullets_replace"] = QA_RESPONSIBILITIES
        elif "bullets_add" not in up:
            up["bullets_add"] = QA_RESPONSIBILITIES

    return up
"""Natural-language instruction interpreter.

Turns short user instructions (e.g., "make it more excited", "replace bullets:")
into the structured `DraftUpdate` fields consumed by the iteration endpoints.
This keeps the web API compact and allows the ADK agent to provide a friendly
editing experience without requiring the user to craft JSON.
"""
