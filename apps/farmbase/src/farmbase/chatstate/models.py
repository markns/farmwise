from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field

from farmbase.runresult.models import AgentRead


class ChatState(BaseModel):
    last_agent: AgentRead | None
    input_list: List[dict[str, Any]] = Field(default_factory=list)
