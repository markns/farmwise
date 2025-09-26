from __future__ import annotations

import uuid

import phonenumbers
from loguru import logger
from pywa_async import WhatsApp
from pywa_async.types import FlowButton
from pywa_async.types.flows import (
    FlowActionType,
    FlowCompletion,
    FlowRequest,
    FlowResponse,
    FlowStatus,
)

from farmwise.farmbetter.models import (
    OmittedUpdateUserRequest,
)
from farmwise.farmbetter.users import FarmBetterAPIError, get_user, update_user
from farmwise.whatsapp.flows.edit_profile.flow import (
    EDIT_PROFILE_SCREEN_ID,
    FLOW_ENDPOINT,
    FLOW_NAME,
)
from farmwise.whatsapp.flows.flow_tokens import FlowSession, clear_flow_session, get_flow_session, store_flow_session

_CONFIRMATION_TEMPLATE = (
    "✅ Profile updated successfully!\n• Name: {name}\n• Gender: {gender}\n• Age: {age}\n"
    # "• Language: {language}\n"
    # "• Crops: {crops}\n"
    # "• Livestock: {livestock}"
)


@WhatsApp.on_flow_request(endpoint=FLOW_ENDPOINT)
async def edit_profile_flow(_: WhatsApp, req: FlowRequest) -> FlowResponse:
    raise NotImplementedError(req)


@edit_profile_flow.on_init()
async def on_edit_profile_init(_: WhatsApp, req: FlowRequest) -> FlowResponse:
    logger.info(f"Flow init request: {req}")
    session = await get_flow_session(req.flow_token) if req.flow_token else None
    if session is None:
        req.token_no_longer_valid("Session expired. Please open the profile flow again.")

    number = phonenumbers.parse(f"+{session.wa_id}")
    user = await get_user(country_code=number.country_code, national_number=number.national_number)

    return req.respond(
        screen=EDIT_PROFILE_SCREEN_ID,
        data={
            "first_name_initial_value": user.firstName,
            "last_name_initial_value": user.lastName,
            "gender_initial_value": user.gender,
        },
    )


@edit_profile_flow.on_data_exchange()
async def on_edit_profile_data_exchange(_: WhatsApp, req: FlowRequest):
    logger.info(f"Flow data exchange: {req}")


@edit_profile_flow.on_completion()
async def on_edit_profile_completion(client: WhatsApp, flow: FlowCompletion) -> None:
    logger.info(f"Flow completion: {flow}")

    wa_id = flow.from_user.wa_id
    number = phonenumbers.parse(f"+{wa_id}")
    user = await get_user(country_code=number.country_code, national_number=number.national_number)

    first_name = flow.response.get("first_name")
    last_name = flow.response.get("last_name")
    gender = flow.response.get("gender")

    update_payload = OmittedUpdateUserRequest(id=user.id, firstName=first_name, lastName=last_name, gender=gender)

    try:
        updated_user = await update_user(update_payload)
    except FarmBetterAPIError as exc:
        logger.exception("Failed to update FarmBetter profile for %s: %s", wa_id, exc)
        await client.send_message(
            to=wa_id,
            text="⚠️ We couldn't save your profile changes right now. Please try again later.",
        )
        return

    await client.send_message(
        to=wa_id,
        text=_CONFIRMATION_TEMPLATE.format(
            name=f"{updated_user.firstName} {updated_user.lastName}".strip(),
        ),
    )

    if flow.token:
        await clear_flow_session(flow.token)


async def launch_edit_profile_flow(
    client: WhatsApp,
    *,
    to: str,
    wa_user_name: str | None = None,
) -> None:
    flow_token = uuid.uuid4().hex
    await store_flow_session(flow_token, FlowSession(wa_id=to, name=wa_user_name))

    await client.send_message(
        to=to,
        text="Tap below to review and update your farmbetter profile.",
        buttons=FlowButton(
            title="Edit profile",
            # flow_id=flow_id,
            flow_token=flow_token,
            flow_action_type=FlowActionType.DATA_EXCHANGE,
            flow_action_screen=EDIT_PROFILE_SCREEN_ID,
            mode=FlowStatus.PUBLISHED,
            flow_name=FLOW_NAME,
        ),
    )
