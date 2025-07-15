import pathlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from pydantic import BaseModel, Field, ConfigDict
from pywa_async import types


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


class Action(Enum):
    request_location = "request_location"


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


@dataclass
class Button(types.Button):
    title: str = field(metadata={"description": "The title of the button (up to 20 characters)"})
    callback_data: str = field(
        metadata={"description": "The data to send when the user clicks on the button (up to 256 characters"})


@dataclass(frozen=True, slots=True)
class ActivityData(types.CallbackData):  # Subclass CallbackData
    agent: str
    text: str


@dataclass
class SectionRow(types.SectionRow):
    title: str = field(metadata={"description": "The title of the row (up to 24 characters)"})
    callback_data: str | ActivityData = field(
        metadata={"description": "The payload to send when the user clicks on the row up to 200 characters"})
    description: str | None = field(default=None,
                                    metadata={
                                        "description": "The description of the row (optional, up to 72 characters)"})


@dataclass
class Section(types.Section):
    title: str = field(metadata={"description": "The title of the section (up to 24 characters)"})
    rows: Iterable[SectionRow] = field(
        metadata={"description": "The rows in the section (at least 1, no more than 10)"})


@dataclass
class SectionList(types.SectionList):
    button_title: str = field(
        metadata={"description": "The title of the button that opens the section list (up to 20 characters)"})
    sections: Iterable[Section] = field(
        metadata={"description": "The sections in the section list (at least 1, no more than 10)"})


class TextResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
