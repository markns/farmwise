from __future__ import annotations

import uuid
from datetime import date
from typing import Any

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
from farmwise.whatsapp.flows.flow_tokens import FlowSession, get_flow_session, store_flow_session

_CONFIRMATION_TEMPLATE = (
    "✅ Profile updated successfully!\n• Name: {name}\n"
    # "• Gender: {gender}\n"
    # "• Age: {age}\n"
    # "• Language: {language}\n"
    # "• Crops: {crops}\n"
    # "• Livestock: {livestock}"
)


def _safe_age_from_dob(dob_iso: str | None) -> str:
    if not dob_iso:
        return ""
    try:
        dob = date.fromisoformat(dob_iso)
    except ValueError:
        logger.debug("Invalid stored date_of_birth: %s", dob_iso)
        return ""
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return str(age) if age >= 0 else ""


def _dob_from_age(age: int | None) -> str | None:
    if age is None:
        return None
    today = date.today()
    birth_year = today.year - age
    # Mid-year anchor avoids issues with leap days and ensures deterministic value.
    return date(birth_year, 7, 1).isoformat()


def _parse_age(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        candidate = int(value)
    elif isinstance(value, str):
        value = value.strip()
        if not value.isdigit():
            return None
        candidate = int(value)
    else:
        return None

    return candidate if 13 <= candidate <= 120 else None


def _split_first_name(first_name: str | None, fallback_first: str, fallback_last: str) -> tuple[str, str]:
    if not first_name:
        return fallback_first, fallback_last

    parts = [piece for piece in first_name.split(" ") if piece]
    if not parts:
        return fallback_first, fallback_last
    if len(parts) == 1:
        return parts[0], fallback_last
    return parts[0], " ".join(parts[1:])


async def _handle_flow_completion(client: WhatsApp, flow: FlowCompletion) -> None:
    # flow.response = flow.response.get(PROFILE_FORM_NAME)
    # if not isinstance(flow.response, dict):
    #     logger.warning("Missing %s in flow completion payload: %s", PROFILE_FORM_NAME, flow.response)
    #     return

    # session = await get_flow_session(flow.token) if flow.token else None

    wa_id = flow.from_user.wa_id
    # display_name = session.name if session and session.name else flow.from_user.name
    number = phonenumbers.parse(f"+{wa_id}")
    user = await get_user(country_code=number.country_code, national_number=number.national_number)
    # user_before = context.user

    first_name = flow.response.get("first_name")
    # gender = ensure_gender_option(flow.response.get("gender"))
    # language = ensure_language_option(flow.response.get("preferred_language"))
    # age = _parse_age(flow.response.get("age"))
    # date_of_birth = _dob_from_age(age)

    # crop_ids = [item for item in flow.response.get("crop_ids", []) if isinstance(item, str) and item]
    # livestock_ids = [item for item in flow.response.get("livestock_ids", []) if isinstance(item, str) and item]

    # crop_catalog = await fetch_crop_options()
    # livestock_catalog = await fetch_livestock_options()
    # crop_lookup = {item.id: item.title for item in select_data_sources(all_options=crop_catalog, required_ids=crop_ids)}
    # livestock_lookup = {
    #     item.id: item.title for item in select_data_sources(all_options=livestock_catalog, required_ids=livestock_ids)
    # }

    # first_name, last_name = _split_first_name(first_name, user_before.firstName, user_before.lastName)

    update_payload = OmittedUpdateUserRequest(
        id=user.id,
        firstName=first_name,
        # lastName=last_name,
        # gender=gender,
        # preferredLanguage=language,
        # dateOfBirth=date_of_birth,
        # crops=[
        #     GqCropInput(id=crop_id, name=crop_lookup.get(crop_id, crop_id.replace("_", " ").title()))
        #     for crop_id in crop_ids
        # ],
        # livestock=[
        #     GqLivestockInput(id=animal_id, name=livestock_lookup.get(animal_id, animal_id.replace("_", " ").title()))
        #     for animal_id in livestock_ids
        # ],
    )

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
            # gender=gender.replace("_", " ").title(),
            # age=str(age) if age is not None else "Not shared",
            # language=language.upper(),
            # crops=", ".join(crop.name for crop in updated_user.crops) or "None",
            # livestock=", ".join(animal.name for animal in updated_user.livestock) or "None",
        ),
    )

    # if flow.token:
    #     await clear_flow_session(flow.token)


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

    # user_first_name =
    # gender = ensure_gender_option(user.gender)
    # language = ensure_language_option(user.preferredLanguage)
    # age_str = _safe_age_from_dob(user.dateOfBirth)

    # crop_ids = [crop.id for crop in user.crops]
    # livestock_ids = [animal.id for animal in user.livestock]

    # crop_catalog = await fetch_crop_options()
    # livestock_catalog = await fetch_livestock_options()

    # crop_options = select_data_sources(all_options=crop_catalog, required_ids=crop_ids)
    # livestock_options = select_data_sources(all_options=livestock_catalog, required_ids=livestock_ids)

    return req.respond(
        screen=EDIT_PROFILE_SCREEN_ID,
        data={
            "first_name_initial_value": user.firstName,
            "last_name_initial_value": user.lastName,
            # "gender_initial_value": gender,
            # "age_initial_value": age_str,
            # "language_initial_value": language,
            # "crop_options": crop_options,
            # "livestock_options": livestock_options,
            # "initial_crop_ids": crop_ids,
            # "initial_livestock_ids": livestock_ids,
        },
    )


@edit_profile_flow.on_data_exchange()
async def on_edit_profile_data_exchange(_: WhatsApp, req: FlowRequest):
    logger.info(f"Flow data exchange: {req}")


@edit_profile_flow.on_completion()
async def on_edit_profile_completion(client: WhatsApp, flow: FlowCompletion) -> None:
    logger.info(f"Flow completion: {flow}")
    await _handle_flow_completion(client, flow)


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


__all__ = [
    "launch_edit_profile_flow",
]
