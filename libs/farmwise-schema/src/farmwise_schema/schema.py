from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal, NotRequired

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class AgentInfo(BaseModel):
    """Info about an available agent."""

    key: str = Field(
        description="Agent key.",
        examples=["research-assistant"],
    )
    description: str = Field(
        description="Description of the agent.",
        examples=["A research assistant for generating research papers."],
    )


class ServiceMetadata(BaseModel):
    """Metadata about the service including available agents and models."""

    ...
    agents: list[AgentInfo] = Field(
        description="List of available agents.",
    )
    # models: list[AllModelEnum] = Field(
    #     description="List of available LLMs.",
    # )
    default_agent: str = Field(
        description="Default agent used when none is specified.",
        examples=["research-assistant"],
    )
    # default_model: AllModelEnum = Field(
    #     description="Default model used when none is specified.",
    # )


class UserInput(BaseModel):
    """Basic user input for the agent."""

    message: str = Field(
        description="User input to the agent.",
        examples=["What is the weather in Tokyo?"],
    )
    # TODO: Use eg. Image object from pywa, rather than `str`
    image: str | None = Field(
        description="Image to send to the agent.",
        default=None,
        # examples=["https://example.com/image.jpg"],
    )
    user_id: str | None = Field(
        description="User ID to persist and continue a multi-turn conversation.",
        # default=None,
        examples=["+254748256530", "847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    timestamp: datetime = Field(
        description="Timestamp of the user input.",
        default_factory=lambda: datetime.now(UTC),
        examples=[datetime.now(UTC).isoformat()],
    )
    user_name: str | None = Field(
        description="User ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["Mark Nuttall-Smith"],
    )
    agent_config: dict[str, Any] = Field(
        description="Additional configuration to pass through to the agent",
        default={},
        examples=[{"spicy_level": 0.8}],
    )


class StreamInput(UserInput):
    """User input for streaming the agent's response."""

    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )


class ToolCall(TypedDict):
    """Represents a request to call a tool."""

    name: str
    """The name of the tool to be called."""
    args: dict[str, Any]
    """The arguments to the tool call."""
    id: str | None
    """An identifier associated with the tool call."""
    type: NotRequired[Literal["tool_call"]]


class Action(Enum):
    request_location = "request_location"


class Button(BaseModel):
    title: str
    callback_data: str


class SectionRow(BaseModel):
    title: str
    callback_data: str


class Section(BaseModel):
    title: str
    rows: list[SectionRow]


class SectionList(BaseModel):
    button_title: str
    sections: list[Section]


class WhatsappResponse(BaseModel):
    content: str | None = Field(description="Content of the response.")
    actions: list[Action] = Field(
        description="Actions that can be requested from the client. Should be left empty unless specified.",
    )
    buttons: list[Button] = Field(
        description="Buttons that can be added to the response. Should be left empty unless specified.",
    )
    section_list: SectionList | None = Field(
        description="Section list with multiple choice options. Should be left null unless specified."
    )


# class ChatMessage(BaseModel):
#     """Message in a chat."""
#

#     content: str = Field(
#         description="Content of the message.",
#         examples=["Hello, world!"],
#     )
#     actions: list[Action] = Field(description="Actions requested of user", default=[], examples=["request_location"])
#
#     def pretty_repr(self) -> str:
#         """Get a pretty representation of the message."""
#         base_title = self.type.title() + " Message"
#         padded = " " + base_title + " "
#         sep_len = (80 - len(padded)) // 2
#         sep = "=" * sep_len
#         second_sep = sep + "=" if len(padded) % 2 else sep
#         title = f"{sep}{padded}{second_sep}"
#         return f"{title}\n\n{self.content}"
#
#     def pretty_print(self) -> None:
#         print(self.pretty_repr())  # noqa: T201


class Feedback(BaseModel):
    """Feedback for a run, to record to LangSmith."""

    run_id: str = Field(
        description="Run ID to record feedback for.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    key: str = Field(
        description="Feedback key.",
        examples=["human-feedback-stars"],
    )
    score: float = Field(
        description="Feedback score.",
        examples=[0.8],
    )
    kwargs: dict[str, Any] = Field(
        description="Additional feedback kwargs, passed to LangSmith.",
        default={},
        examples=[{"comment": "In-line human feedback"}],
    )


class FeedbackResponse(BaseModel):
    status: Literal["success"] = "success"


class ChatHistoryInput(BaseModel):
    """Input for retrieving chat history."""

    user_id: str | None = Field(
        description="User ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["+254748256530", "847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    thread_id: str = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )


class ChatHistory(BaseModel):
    ...
    # messages: list[ChatMessage]
