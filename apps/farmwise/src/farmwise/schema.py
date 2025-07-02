import pathlib
from enum import Enum
from typing import Annotated, Any, Literal, NotRequired

from annotated_types import Len
from pydantic import BaseModel, Field, StringConstraints
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


class SessionState(BaseModel):
    last_agent: str
    previous_response_id: str


class UserInput(BaseModel):
    """Basic user input for the agent."""

    text: str | None = Field(
        description="User input to the agent.",
        default=None,
        examples=["What is the weather in Tokyo?"],
    )
    image: str | None = Field(
        description="Image path to send to the agent.",
        default=None,
    )
    voice: str | None = Field(
        description="Voice path to send to the agent.",
        default=None,
    )
    # user_id: str = Field(
    #     description="User ID to persist and continue a multi-turn conversation.",
    #     examples=["+254748256530", "847c6285-8fc9-4560-a83f-4e6285809254"],
    # )
    # timestamp: datetime = Field(
    #     description="Timestamp of the user input.",
    #     default_factory=lambda: datetime.now(UTC),
    #     examples=[datetime.now(UTC).isoformat()],
    # )
    # user_name: str | None = Field(
    #     description="User ID to persist and continue a multi-turn conversation.",
    #     default=None,
    #     examples=["Mark Nuttall-Smith"],
    # )
    # agent_config: dict[str, Any] = Field(
    #     description="Additional configuration to pass through to the agent",
    #     default={},
    #     examples=[{"spicy_level": 0.8}],
    # )


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
    title: Annotated[str, StringConstraints(max_length=24)]
    callback_data: str


class Section(BaseModel):
    title: Annotated[str, StringConstraints(max_length=24)]
    rows: Annotated[list[SectionRow], Len(min_length=1, max_length=10)]


class SectionList(BaseModel):
    button_title: str
    sections: list[Section]


class Contact(BaseModel):
    """Contact information for WhatsApp contact sharing."""

    name: str = Field(description="Full name of the contact")
    phone: str | None = Field(default=None, description="Phone number of the contact")
    email: str | None = Field(default=None, description="Email address of the contact")
    organization: str | None = Field(default=None, description="Organization name")


class Product(BaseModel):
    """Product information for WhatsApp product sharing."""

    catalog_id: str = Field(description="The catalog ID containing the product")
    sku: str = Field(description="The product SKU")
    body: str | None = Field(default=None, description="Body text for the product message")
    footer: str | None = Field(default=None, description="Footer text for the product message")


class TextResponse(BaseModel):
    content: str | None = Field(description="Content of the response.")
    actions: list[Action] = Field(
        default=[],
        description="Actions that can be requested from the client. Should be left empty unless specified.",
    )
    # TODO: use a oneOf here to make sure not everything is set -
    #  https://docs.pydantic.dev/latest/concepts/fields/#discriminator
    # image_url: str | None = Field(default=None, description="An image url that should be sent to the user.")
    # contact: Contact | None = Field(default=None, description="Contact information to share with the user.")
    # product: Product | None = Field(default=None, description="Product information to share with the user.")
    buttons: list[Button] = Field(
        default=[],
        description="Buttons that can be added to the response. Should be left empty unless specified.",
    )
    section_list: SectionList | None = Field(
        default=None, description="Section list with multiple choice options. Should be left null unless specified."
    )
    # TODO: debug_info: str | None = Field(
    #     description="This field can be used by the LLM to tell the user that it's not clear how to respond, "
    #     "and how the user can improve subsequent requests"
    # )


class AudioResponse(BaseModel):
    audio: str | pathlib.Path | bytes


class ResponseEvent(BaseModel):
    response: TextResponse | AudioResponse
    has_more: bool = True


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
