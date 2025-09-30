from __future__ import annotations

import uuid
from collections import defaultdict
from copy import copy
from textwrap import dedent

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

    user_crops = {c.id for c in user.crops}
    user_livestock = {c.id for c in user.livestock}

    def _to_datasources(items: list[GqConceptDto]) -> list[DataSource]:
        return [DataSource(id=item.id, title=item.name) for item in items]

    return req.respond(
        screen=EDIT_PROFILE_SCREEN_ID,
        data={
            "first_name_initial_value": user.firstName,
            "last_name_initial_value": user.lastName,
            "gender_initial_value": user.gender,
            "dob_initial_value": user.dateOfBirth,
            "language_initial_value": user.preferredLanguage,
            "cereal_options": _to_datasources(concepts.get("cereals", [])),
            "cereal_ids": user_crops.intersection({c.id for c in concepts["cereals"]}),
            "fruit_options": _to_datasources(concepts.get("fruits", [])),
            "fruit_ids": user_crops.intersection({c.id for c in concepts["fruits"]}),
            "vegetable_options": _to_datasources(concepts.get("vegetables", [])),
            "vegetable_ids": user_crops.intersection({c.id for c in concepts["vegetables"]}),
            "livestock_options": _to_datasources(concepts.get("livestock", [])),
            "livestock_ids": user_livestock.intersection({c.id for c in concepts["livestock"]}),
            "poultry_options": _to_datasources(concepts.get("poultry", [])),
            "poultry_ids": user_livestock.intersection({c.id for c in concepts["poultry"]}),
        },
    )


@edit_profile_flow.on_completion()
async def on_edit_profile_completion(client: WhatsApp, flow: FlowCompletion) -> None:
    logger.info(f"Flow completion: {flow}")

    wa_id = flow.from_user.wa_id
    number = phonenumbers.parse(f"+{wa_id}")
    user = await get_user(country_code=number.country_code, national_number=number.national_number)

    poultry = flow.response.pop("poultry")
    livestock = flow.response.pop("livestock")
    vegetables = flow.response.pop("vegetables")
    fruits = flow.response.pop("fruits")
    cereals = flow.response.pop("cereals")

    livestock = [{"id": pl, "name": pl} for pl in poultry + livestock]
    crops = [{"id": vfc, "name": vfc} for vfc in vegetables + fruits + cereals]

    update_args = {snake_to_camel(k, upper=False): v for k, v in flow.response.items()}
    update_args["crops"] = crops
    # update_args["livestock"] = livestock
    update_args["livestock"] = []

    logger.info(f"Updating farmbetter profile for {wa_id} with {update_args}")
    update_payload = OmittedUpdateUserRequest(id=user.id, **update_args)

    try:
        await update_user(update_payload)
    except FarmBetterAPIError as exc:
        logger.exception("Failed to update FarmBetter profile for %s: %s", wa_id, exc)
        await client.send_message(
            to=wa_id,
            text="⚠️ We couldn't save your profile changes right now. Please try again later.",
        )
        return

    await client.send_message(
        to=wa_id,
        text=dedent("✅ Profile updated successfully!"),
    )

    if flow.token:
        await clear_flow_session(flow.token)


button = FlowButton(
    title="Edit profile",
    # flow_id=flow_id,
    # flow_token=flow_token,
    flow_action_type=FlowActionType.DATA_EXCHANGE,
    flow_action_screen=EDIT_PROFILE_SCREEN_ID,
    mode=FlowStatus.PUBLISHED,
    flow_name=FLOW_NAME,
)


async def launch_edit_profile_flow(
    client: WhatsApp,
    *,
    to: str,
    wa_user_name: str | None = None,
) -> None:
    flow_token = uuid.uuid4().hex
    await store_flow_session(flow_token, FlowSession(wa_id=to, name=wa_user_name))

    _button = copy(button)
    _button.flow_token = flow_token
    await client.send_message(to=to, text="Tap below to review and update your farmbetter profile.", buttons=_button)


async def fetch_concepts() -> dict[str, list[GqConceptDto]]:
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
    #
    # options = {}
    # for concept, values in concepts.items():
    #     options[concept] = values

    return concepts
