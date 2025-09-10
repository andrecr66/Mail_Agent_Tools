from __future__ import annotations
from typing import Any, Optional, Sequence
from googleapiclient.discovery import Resource  # type: ignore[import-untyped]


def _list_labels(svc: Resource) -> list[dict[str, Any]]:
    resp: dict[str, Any] = svc.users().labels().list(userId="me").execute()
    return list(resp.get("labels", []))


def _find_label_id(labels: Sequence[dict[str, Any]], name: str) -> Optional[str]:
    for lb in labels:
        if lb.get("name") == name:
            lid = lb.get("id")
            return str(lid) if lid is not None else None
    return None


def ensure_label(svc: Resource, name: str) -> str:
    lid = _find_label_id(_list_labels(svc), name)
    if lid:
        return lid
    body = {
        "name": name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    created: dict[str, Any] = svc.users().labels().create(userId="me", body=body).execute()
    return str(created["id"])


def ensure_hierarchy(svc: Resource, parent: str, leaf: str) -> list[str]:
    parent_id = ensure_label(svc, parent)
    leaf_id = ensure_label(svc, f"{parent}/{leaf}")
    return [parent_id, leaf_id]
"""Helpers for creating and looking up Gmail labels.

We create a small hierarchy `<prefix>/<brand_id>` and apply both labels so
messages are easy to find under a common parent.
"""
