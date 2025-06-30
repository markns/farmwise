from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.models import TimeStampMixin


# --------------------------------------------------------------------------- #
#  Agent – minimal, enough to satisfy FK relations.
# --------------------------------------------------------------------------- #
class Agent(Base):
    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    # Optional free-form JSON with the agent’s config / prompt / metadata
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)


class AgentBase(BaseModel):
    name: str
    # metadata_: dict[str, Any] | None = Field(default_factory=dict, alias="metadata")

    # class Config:
    #     populate_by_name = True


class AgentCreate(AgentBase):
    pass


class AgentRead(AgentBase):
    id: int


class RunResult(Base, TimeStampMixin):
    __tablename__ = "run_result"
    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    contact: Mapped[Contact] = relationship()
    input_: Mapped[Any] = mapped_column("input", JSON, nullable=False)
    final_output: Mapped[Any] = mapped_column(JSON, nullable=True)
    # FK to the last agent that handled the run
    last_agent_id: Mapped[int] = mapped_column(ForeignKey("agent.id", ondelete="SET NULL"), nullable=True)
    last_agent: Mapped[Optional[Agent]] = relationship()
    trace_id: Mapped[str]
    requests: Mapped[int] = mapped_column(doc="Total requests made to the LLM API.")
    input_tokens: Mapped[int] = mapped_column(doc="Total input tokens sent, across all requests.")
    input_tokens_cached: Mapped[int] = mapped_column(doc="The number of tokens that were retrieved from the cache.")
    output_tokens: Mapped[int] = mapped_column(doc="Total output tokens received, across all requests.")
    output_tokens_reasoning: Mapped[int] = mapped_column(doc="The number of reasoning tokens.")
    total_tokens: Mapped[int] = mapped_column(doc="The total number of tokens used.")


class RunResultBase(BaseModel):
    created_at: datetime
    contact_id: int = Field()
    input_: Any = Field(..., alias="input")
    final_output: Optional[Any] = None
    last_agent: Optional[AgentBase] = None
    trace_id: str
    requests: int
    input_tokens: int
    """The number of input tokens."""

    input_tokens_cached: int
    """The number of tokens that were retrieved from the cache.

    [More on prompt caching](https://platform.openai.com/docs/guides/prompt-caching).
    """
    output_tokens: int
    """The number of output tokens."""

    output_tokens_reasoning: int
    """The number of reasoning tokens."""

    total_tokens: int
    """The total number of tokens used."""


class RunResultCreate(RunResultBase):
    last_agent: Optional[AgentCreate] = None


class RunResultRead(RunResultBase):
    id: int
