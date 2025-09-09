from __future__ import annotations
from typing import Protocol
from app.agents.types import DraftRequest, DraftResponse


class DraftProvider(Protocol):
    def generate(self, req: DraftRequest) -> DraftResponse: ...
