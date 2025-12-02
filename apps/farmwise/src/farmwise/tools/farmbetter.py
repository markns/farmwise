from datetime import datetime
from enum import Enum

from google.adk.tools import ToolContext
from loguru import logger
from pydantic import BaseModel, Field

from farmwise.context import UserContext
from farmwise.farmbetter.models import (
    FieldGqUserModel,
    GqTimelineEntryInput,
    GqUserModelDto,
    OmittedUpdateUserRequest,
)
from farmwise.farmbetter.problems import create_reported_problem
from farmwise.farmbetter.users import create_user, get_user_by_phone, update_user
from farmwise.settings import settings


async def get_farmbetter_user(
    tool_context: ToolContext,
    user_id: str | None = None,
    email: str | None = None,
    country_code: int | None = None,
    national_number: int | None = None,
) -> GqUserModelDto:
    user_context: UserContext = tool_context.state.get("user_context")
    if (
        user_id is None
        and email is None
        and (country_code is None or national_number is None)
        and user_context.user is not None
    ):
        return user_context.user

    user = await get_user_by_phone(
        user_id=user_id,
        email=email,
        country_code=country_code,
        national_number=national_number,
    )
    user_context.user = user
    user_context.new_user = False
    return user


async def create_farmbetter_user(tool_context: ToolContext, user: FieldGqUserModel) -> GqUserModelDto:
    created_user = await create_user(user=user)
    user_context: UserContext = tool_context.state.get("user_context")
    user_context.user = created_user
    user_context.new_user = True
    return created_user


async def update_farmbetter_user(
    tool_context: ToolContext, user: OmittedUpdateUserRequest
) -> GqUserModelDto:
    user_context: UserContext = tool_context.state.get("user_context")
    if user.id is None and user_context.user is not None and user_context.user.id is not None:
        user = user.model_copy(update={"id": user_context.user.id})

    updated_user = await update_user(user=user)
    user_context.user = updated_user
    user_context.new_user = False
    return updated_user


class ProblemStatus(Enum):
    """Represents the status of a reported problem."""

    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"


class TimelineEntry(BaseModel):
    """Represents a single step in a reported problem timeline."""

    message: str
    created: str = Field(default_factory=datetime.now().isoformat)
    image_url: list[str] = Field(default_factory=list)
    audio_url: list[str] = Field(default_factory=list)
    document_url: list[str] = Field(default_factory=list)
    video_url: list[str] = Field(default_factory=list)


async def record_problem(
    tool_context: ToolContext,
    status: ProblemStatus,
    user_summary: TimelineEntry,
    assistant_summary: TimelineEntry,
) -> str:
    """
    Records a farmer's problem in the farmbetter API.

    Args:
        tool_context: ToolContext containing the user context and other execution context details.
        status: Status of the problem. Use `in-progress` if the problem should be followed up by
            an extension agent, or `resolved` if the problem has been resolved by the assistant.
        user_summary: Summary of the user's input for the problem they reported. Any media
            uploaded by the user should be included in the timeline entry.
        assistant_summary: Summary of the assistant's response to the user's problem

    Returns:
        A string indicating successful recording of the problem and
        notifying the user that the assigned extension agent will follow up.

    Raises:
        ValueError: If the user context is not available in the execution
            wrapper.
    """
    user_context: UserContext = tool_context.state.get("user_context")
    if user_context.user is None:
        raise ValueError("No user context available")

    logger.info(f"Creating problem for {user_context.user.id} {user_summary} {assistant_summary}")

    user = user_context.user
    created_problem = await create_reported_problem(
        status=status.value,
        farmer_id=user.id,
        tenant_id=user.tenantIds[0],
        timeline=[
            GqTimelineEntryInput(
                from_=user.id, created=user_summary.created, media=user_summary.image_url, message=user_summary.message
            ),
            GqTimelineEntryInput(
                from_=settings.FARMBETTER_ASSISTANT_USER_ID,
                created=assistant_summary.created,
                message=assistant_summary.message,
            ),
        ],
    )

    if created_problem.extensionAgent is not None:
        return (
            f"Your problem is recorded, and your extension agent {created_problem.extensionAgent.firstName} "
            f"{created_problem.extensionAgent.lastName} should be in touch soon"
        )
    else:
        return "Your problem is recorded, and an extension agent will be in touch soon"
