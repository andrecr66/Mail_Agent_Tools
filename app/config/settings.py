from __future__ import annotations
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    GOOGLE_OAUTH_USER_FILE: str = ".secrets/google/token.json"
    GOOGLE_OAUTH_CLIENT_FILE: str = ".secrets/google/credentials.json"

    MAIL_AGENT_DEFAULT_ACTION: Literal["draft", "send"] = "draft"
    MAIL_AGENT_GMAIL_LABEL_PREFIX: str = "Agent-Sent"
    MAIL_AGENT_BRAND_ID: str = "default"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
