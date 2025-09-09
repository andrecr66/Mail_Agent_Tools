# mypy: disable-error-code=import-untyped
from __future__ import annotations
from typing import Any
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from app.google.oauth import get_scopes


def has_required_scopes(creds: Any) -> bool:
    scopes = set(getattr(creds, "scopes", []) or [])
    return set(get_scopes()).issubset(scopes)


def build_gmail_service(creds: Credentials) -> Resource:
    return build("gmail", "v1", credentials=creds, cache_discovery=False)
