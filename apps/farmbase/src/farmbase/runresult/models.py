from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact
from farmbase.database.core import Base


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


# --------------------------------------------------------------------------- #
#  RunResult – corresponds to RunResult (non-streaming).
#  Stores input, final_output, etc.
# --------------------------------------------------------------------------- #
class RunResult(Base):
    __tablename__ = "run_result"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    contact: Mapped[Contact] = relationship()

    # Raw OpenAI Agents SDK attributes
    input_: Mapped[Any] = mapped_column("input", JSON, nullable=False)
    final_output: Mapped[Any] = mapped_column(JSON, nullable=True)
    input_guardrails: Mapped[Optional[dict]] = mapped_column(JSON)
    output_guardrails: Mapped[Optional[dict]] = mapped_column(JSON)

    # FK to the last agent that handled the run
    last_agent_id: Mapped[int] = mapped_column(ForeignKey("agent.id", ondelete="SET NULL"), nullable=True)
    last_agent: Mapped[Optional[Agent]] = relationship()

    # Collections
    raw_responses: Mapped[List["ModelResponse"]] = relationship(
        back_populates="run_result", cascade="all, delete-orphan"
    )
    new_items: Mapped[List["RunItem"]] = relationship(back_populates="run_result", cascade="all, delete-orphan")

    input_list: Mapped[list[dict]] = mapped_column(JSON)
    trace_id: Mapped[str]


class RunResultBase(BaseModel):
    contact_id: int = Field()
    input_: Any = Field(..., alias="input")
    created_at: datetime
    final_output: Optional[Any] = None
    input_guardrails: Optional[dict[str, Any]] = None
    output_guardrails: Optional[dict[str, Any]] = None
    last_agent: Optional[AgentBase] = None
    input_list: List[dict[str, Any]]
    raw_responses: List[ModelResponseCreate] = Field(default_factory=list)
    new_items: List[RunItemBase] = Field(default_factory=list)
    trace_id: str


class RunResultCreate(RunResultBase): ...


class RunResultRead(RunResultBase):
    id: int
    # created_at: datetime
    # raw_responses: List[ModelResponseRead]


# --------------------------------------------------------------------------- #
#  ModelResponse – one entry per LLM call.
# --------------------------------------------------------------------------- #
class ModelResponse(Base):
    __tablename__ = "model_response"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_result_id: Mapped[int] = mapped_column(ForeignKey("run_result.id", ondelete="CASCADE"), nullable=False)
    run_result: Mapped[RunResult] = relationship(back_populates="raw_responses")

    response_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, unique=True)
    output: Mapped[Any] = mapped_column(JSON, nullable=True)
    usage: Mapped[Optional[dict]] = mapped_column(JSON)  # tokens, cost etc.

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ModelResponseBase(BaseModel):
    response_id: str
    output: Any
    usage: Optional[dict[str, Any]] = None


class ModelResponseCreate(ModelResponseBase):
    pass


class ModelResponseRead(ModelResponseBase):
    id: int
    created_at: datetime


# --------------------------------------------------------------------------- #
#  RunItem – polymorphic base (table-per-class).
# --------------------------------------------------------------------------- #
class RunItem(Base):
    """
    Polymorphic parent representing any of the six SDK item types.
    Single-table inheritance → one table, discriminator column `type`.
    """

    __tablename__ = "run_item"

    # --- shared columns ----------------------------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)

    run_result_id: Mapped[int] = mapped_column(
        ForeignKey("run_result.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_result: Mapped["RunResult"] = relationship(back_populates="new_items")

    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent.id", ondelete="SET NULL"), nullable=True)
    agent: Mapped[Optional["Agent"]] = relationship(
        "Agent",
        # back_populates="generated_items",
        foreign_keys=[agent_id],
    )

    # Raw payload from the SDK item (always present)
    raw_item: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Discriminator
    type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)

    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "run_item"}


class MessageOutputItem(RunItem):
    # only this subclass sees the 'content' attribute
    content: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {"polymorphic_identity": "message_output_item"}


class HandoffCallItem(RunItem):
    function_name: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {"polymorphic_identity": "handoff_call_item"}


class HandoffOutputItem(RunItem):
    source_agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent.id", ondelete="SET NULL"))
    target_agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent.id", ondelete="SET NULL"))

    source_agent: Mapped[Optional["Agent"]] = relationship("Agent", foreign_keys=[source_agent_id])
    target_agent: Mapped[Optional["Agent"]] = relationship("Agent", foreign_keys=[target_agent_id])

    __mapper_args__ = {"polymorphic_identity": "handoff_output_item"}


class ToolCallItem(RunItem):
    # tool_name: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {"polymorphic_identity": "tool_call_item"}


class ToolCallOutputItem(RunItem):
    output: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {"polymorphic_identity": "tool_call_output_item"}


class ReasoningItem(RunItem):
    rationale: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {"polymorphic_identity": "reasoning_item"}


class RunItemBase(BaseModel):
    type: str
    agent_id: Optional[int] = None
    raw_item: dict[str, Any]


class MessageOutputItemCreate(RunItemBase):
    content: Optional[str]


class HandoffCallItemCreate(RunItemBase):
    function_name: Optional[str]


class HandoffOutputItemCreate(RunItemBase):
    source_agent_id: Optional[int]
    target_agent_id: Optional[int]


class ToolCallItemCreate(RunItemBase):
    pass


class ToolCallOutputItemCreate(RunItemBase):
    output: Optional[str]


class ReasoningItemCreate(RunItemBase):
    rationale: Optional[str]


RunItemCreate = RunItemBase  # fallback for generic use

