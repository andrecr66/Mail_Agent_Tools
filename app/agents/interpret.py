from __future__ import annotations
import re
from typing import Any, Dict, List

# Heuristics-based parser that turns natural-language instructions
# into the DraftUpdate fields we already support.

_BULLET_SPLIT = re.compile(r"[;,]\s*")

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

    # CTA text
    m = re.search(r"(?:set\s+)?cta\s*text\s*(?:to)?\s*[:=]\s*['\"]?(.+?)['\"]?(?:\s|$)", instr, flags=re.I)
    if m:
        up["cta_text"] = m.group(1).strip()

    # CTA url
    m = re.search(r"(?:set\s+)?cta\s*url\s*(?:to)?\s*[:=]\s*['\"]?(\S+)['\"]?", instr, flags=re.I)
    if m:
        up["cta_url"] = m.group(1).strip()

    # Remove CTA entirely
    if re.search(r"\b(remove|clear|drop)\s+cta\b", instr, flags=re.I):
        # Use empty strings so templates treat as falsy
        up["cta_text"] = ""
        up["cta_url"] = ""

    # Purpose
    m = re.search(r"(?:set\s+)?purpose\s*(?:to)?\s*[:=]\s*['\"]?([A-Za-z][A-Za-z -]+)['\"]?", instr, flags=re.I)
    if m:
        up["purpose"] = m.group(1).strip()

    return up
