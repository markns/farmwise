from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="Role of the message (user or assistant).")
    content: str = Field(..., description="Message content.")


class MemoryCreate(BaseModel):
    messages: List[Message] = Field(..., description="List of messages to store.")
    # user_id: Optional[str] = None
    # agent_id: Optional[str] = None
    # run_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query.")
    filters: Optional[Dict[str, Any]] = None
