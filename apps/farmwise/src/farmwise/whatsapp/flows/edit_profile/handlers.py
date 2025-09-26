from __future__ import annotations

import uuid
from collections import defaultdict

import phonenumbers
from graphql.pyutils import snake_to_camel
from loguru import logger
from pywa.types.flows import (
    DataSource,
)
from pywa_async import WhatsApp
from pywa_async.types import FlowButton
from pywa_async.types.flows import (
    FlowActionType,
    FlowCompletion,
    FlowRequest,
    FlowResponse,
    FlowStatus,
)

from farmwise.farmbetter.concepts import get_concepts
from farmwise.farmbetter.models import (
    GqConceptDto,
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

    concepts = await fetch_concepts()

    return req.respond(
        screen=EDIT_PROFILE_SCREEN_ID,
        data={
            "first_name_initial_value": user.firstName,
            "last_name_initial_value": user.lastName,
            "gender_initial_value": user.gender,
            "fruit_options": concepts.get("fruits", []),
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

    update_args = {snake_to_camel(k): v for k, v in flow.response.items()}
    logger.info(f"Updating farmbetter profile for {wa_id} with {update_args}")
    update_payload = OmittedUpdateUserRequest(id=user.id, **update_args)

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


async def fetch_concepts() -> dict[str, list[DataSource]]:
    concepts = await get_concepts()

    def _group_and_sort(items: list[GqConceptDto]):
        grouped = defaultdict(list)
        # group items by parentId
        for item in items:
            grouped[item.parentId].append(item)
        # sort each group by the 'name' field
        for key in grouped:
            grouped[key] = sorted(grouped[key], key=lambda x: x.name.lower())
        return dict(grouped)

    concepts = _group_and_sort(concepts)

    options = {}
    for concept, values in concepts.items():
        options[concept] = [DataSource(id=v.id, title=v.name) for v in values]
        print(f"{concept}: {[v.name for v in values]}")

    return options
