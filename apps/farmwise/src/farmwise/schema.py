import pathlib
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from pywa.types import Button, SectionList


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

