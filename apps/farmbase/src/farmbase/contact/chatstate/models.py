from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field

from farmbase.contact.runresult.models import AgentRead


class ChatState(BaseModel):
    last_agent: AgentRead | None
    messages: List[dict[str, Any]] = Field(default_factory=list)
