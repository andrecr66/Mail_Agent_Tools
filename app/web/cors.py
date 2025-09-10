from __future__ import annotations
from typing import Any
from fastapi.middleware.cors import CORSMiddleware
import os


def install_cors(app: Any) -> None:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    origins = [o.strip() for o in origins if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["content-type"],
    )
"""CORS middleware helper for the FastAPI app."""
