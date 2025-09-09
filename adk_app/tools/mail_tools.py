from __future__ import annotations
import os
from typing import Any, Dict, Optional, cast, TYPE_CHECKING
import httpx

if TYPE_CHECKING:
    from google.adk.tools import ToolContext
else:

    class ToolContext: ...  # minimal stub for runtime


BASE_URL = os.getenv("MAIL_API_BASE", "http://localhost:8080")


def _json_or_error(r: httpx.Response) -> Dict[str, Any]:
    try:
        r.raise_for_status()
        return cast(Dict[str, Any], r.json())
    except httpx.HTTPStatusError:
        payload: Dict[str, Any] = {
            "ok": False,
            "status_code": r.status_code,
            "endpoint": str(r.request.url),
        }
        try:
            payload["error_json"] = r.json()
        except Exception:
            payload["error"] = r.text
        return payload


async def preview_mail(
    base: Dict[str, Any],
    updates: Optional[Dict[str, Any]] = None,
    tool_context: Optional["ToolContext"] = None,
) -> Dict[str, Any]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as ac:
        if updates:
            r = await ac.post("/draft/iterate/preview", json={"base": base, "updates": updates})
        else:
            r = await ac.post("/mail/preview", json=base)
        return _json_or_error(r)


async def deliver_mail(
    base: Dict[str, Any],
    updates: Optional[Dict[str, Any]] = None,
    mode: str = "draft",
    tool_context: Optional["ToolContext"] = None,
) -> Dict[str, Any]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as ac:
        if updates:
            r = await ac.post(
                "/mail/iterate/deliver", json={"base": base, "updates": updates, "mode": mode}
            )
        else:
            r = await ac.post(f"/mail/deliver?mode={mode}", json=base)
        return _json_or_error(r)


async def preview_mail_nl(
    base: Dict[str, Any],
    instructions: str,
    tool_context: Optional["ToolContext"] = None,
) -> Dict[str, Any]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as ac:
        r = await ac.post(
            "/draft/iterate/nl", json={"base": base, "updates": {"instructions": instructions}}
        )
        return _json_or_error(r)


async def deliver_mail_nl(
    base: Dict[str, Any],
    instructions: str,
    mode: str = "draft",
    tool_context: Optional["ToolContext"] = None,
) -> Dict[str, Any]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as ac:
        r = await ac.post(
            "/mail/iterate/nl-deliver",
            json={"base": base, "updates": {"instructions": instructions}, "mode": mode},
        )
        return _json_or_error(r)
