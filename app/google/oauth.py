from __future__ import annotations
from pathlib import Path
from typing import Sequence, cast

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from google.auth.transport.requests import Request

from app.config.settings import settings

# Scopes: compose, send, manage labels, and modify messages (needed to apply labels)
SCOPES: Sequence[str] = (
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
)


def ensure_user_credentials(*, interactive: bool = False) -> Credentials:
    """
    Load or obtain a user OAuth token with Gmail scopes.
    - If token exists but expired and has a refresh_token, refresh it.
    - If token missing/invalid:
        * interactive=True -> run browser flow and save token.
        * interactive=False -> raise a clear RuntimeError.
    """
    token_path = Path(settings.GOOGLE_OAUTH_USER_FILE)
    client_path = Path(settings.GOOGLE_OAUTH_CLIENT_FILE)

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
            str(token_path), SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore[no-untyped-call]
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(cast(str, creds.to_json()), encoding="utf-8")  # type: ignore[no-untyped-call]
        elif interactive:
            if not client_path.exists():
                raise FileNotFoundError(
                    f"Client secrets not found at {client_path}. "
                    "Download OAuth client JSON and place it there."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES)
            creds = flow.run_local_server(port=0)
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(cast(str, creds.to_json()), encoding="utf-8")
        else:
            raise RuntimeError(
                "No valid Gmail OAuth token. Run interactive auth once:\n"
                "  python -c 'from app.google.oauth import ensure_user_credentials as e; e(interactive=True)'"
            )
    return creds


def get_scopes() -> tuple[str, ...]:
    return tuple(SCOPES)
