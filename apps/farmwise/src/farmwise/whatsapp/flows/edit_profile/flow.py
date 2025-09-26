from __future__ import annotations

import time
from typing import Iterable, Sequence

from gql import gql
from loguru import logger
from pywa import Version
from pywa.types.flows import (
    CompleteAction,
    DataSource,
    DatePicker,
    Dropdown,
    FlowJSON,
    Footer,
    Form,
    Layout,
    Screen,
    ScreenData,
    TextBody,
    TextHeading,
    TextInput,
)

from farmwise.farmbetter import farmbetter_client

FLOW_ENDPOINT = "/flows/edit-profile"
FLOW_NAME = "edit_profile"
EDIT_PROFILE_SCREEN_ID = "EDIT_PROFILE"
PROFILE_FORM_NAME = "profile_form"

_GENDER_OPTIONS: tuple[DataSource, ...] = (
    DataSource(id="male", title="Male"),
    DataSource(id="female", title="Female"),
    DataSource(id="other", title="Keep private"),
)

_LANGUAGE_OPTIONS: tuple[DataSource, ...] = (
    DataSource(id="en", title="English"),
    DataSource(id="fr", title="French"),
    DataSource(id="pt", title="Portuguese"),
    DataSource(id="sw", title="Swahili"),
    DataSource(id="es", title="Spanish"),
)

# Cached catalog lookups so we avoid round-tripping to FarmBetter on every flow request.
_CROP_CACHE: tuple[list[DataSource], float] | None = None
_LIVESTOCK_CACHE: tuple[list[DataSource], float] | None = None
_CATALOG_TTL_SECONDS = 60 * 60  # 1 hour cache window


def build_edit_profile_flow_json() -> FlowJSON:
    """Construct the Flow JSON definition for the edit profile experience."""

    language_default = ScreenData(key="language_initial_value", example=_LANGUAGE_OPTIONS[0].id)
    crop_options = ScreenData(key="crop_options", example=[DataSource(id="crop-example", title="Maize")])
    livestock_options = ScreenData(key="livestock_options", example=[DataSource(id="livestock-example", title="Goat")])
    crop_initial_ids = ScreenData(key="initial_crop_ids", example=["crop-example"])
    livestock_initial_ids = ScreenData(key="initial_livestock_ids", example=["livestock-example"])

    #         # TextInput(
    #         #     name="age",
    #         #     label="Age",
    #         #     required=True,
    #         #     helper_text="Whole number between 13 and 120",
    #         #     input_type=InputType.NUMBER,
    #         #     init_value=age_default.ref,
    #         # ),
    #         # RadioButtonsGroup(
    #         #     name="preferred_language",
    #         #     label="Preferred language",
    #         #     required=True,
    #         #     data_source=list(_LANGUAGE_OPTIONS),
    #         #     init_value=language_default.ref,
    #         # ),
    #         # ChipsSelector(
    #         #     name="crop_ids",
    #         #     label="Crop interests",
    #         #     description="Select up to 5 crops you grow or plan to grow",
    #         #     data_source=crop_options.ref,
    #         #     max_selected_items=5,
    #         #     init_value=crop_initial_ids.ref,
    #         # ),
    #         # ChipsSelector(
    #         #     name="livestock_ids",
    #         #     label="Livestock interests",
    #         #     description="Select up to 5 livestock types you keep",
    #         #     data_source=livestock_options.ref,
    #         #     max_selected_items=5,
    #         #     init_value=livestock_initial_ids.ref,
    #         # ),
    #     ],
    # )

    return FlowJSON(
        version=Version.FLOW_JSON,
        data_api_version=Version.FLOW_DATA_API,
        routing_model={
            EDIT_PROFILE_SCREEN_ID: [],
        },
        screens=[
            Screen(
                id=EDIT_PROFILE_SCREEN_ID,
                title="Update your farmbetter profile",
                terminal=True,
                success=True,
                data=[
                    first_name_default := ScreenData(key="first_name_initial_value", example="Hudson"),
                    last_name_default := ScreenData(key="last_name_initial_value", example="Ndege"),
                    gender_default := ScreenData(key="gender_initial_value", example=_GENDER_OPTIONS[0].id),
                    dob_default := ScreenData(key="dob_initial_value", example="1979-03-06"),
                    # gender_default,
                    # age_default,
                    # language_default,
                    # crop_options,
                    # livestock_options,
                    # crop_initial_ids,
                    # livestock_initial_ids,
                ],
                layout=Layout(
                    children=[
                        TextHeading(text="Keep your details current"),
                        TextBody(
                            text="We use this information to personalise advice and connect you to the right services.",
                        ),
                        profile_form := Form(
                            name=PROFILE_FORM_NAME,
                            children=[
                                TextInput(
                                    name="first_name",
                                    label="First name",
                                    required=True,
                                    min_chars=2,
                                    max_chars=80,
                                    helper_text="Enter your first name",
                                    init_value=first_name_default.ref,
                                ),
                                TextInput(
                                    name="last_name",
                                    label="Last name",
                                    required=True,
                                    min_chars=2,
                                    max_chars=80,
                                    helper_text="Enter your last name",
                                    init_value=last_name_default.ref,
                                ),
                                Dropdown(
                                    name="gender",
                                    label="Gender",
                                    required=True,
                                    data_source=list(_GENDER_OPTIONS),
                                    init_value=gender_default.ref,
                                ),
                                DatePicker(
                                    name="dob",
                                    label="Date of birth",
                                    required=False,
                                    # max_date="today",
                                    helper_text="Enter your date of birth (optional)",
                                    init_value=dob_default.ref,
                                ),
                            ],
                        ),
                        Footer(
                            label="Save profile",
                            on_click_action=CompleteAction(
                                # TODO: is there a better way to do this using the Form?
                                payload={component.name: component.ref for component in profile_form.children},
                                # payload=profile_form.ref,
                            ),
                        ),
                    ]
                ),
            )
        ],
    )


def ensure_gender_option(value: str | None) -> str:
    if value and value in {option.id for option in _GENDER_OPTIONS}:
        return value
    return _GENDER_OPTIONS[-1].id  # default to "Prefer not to say"


def ensure_language_option(value: str | None) -> str:
    if value and value in {option.id for option in _LANGUAGE_OPTIONS}:
        return value
    return _LANGUAGE_OPTIONS[0].id


async def fetch_crop_options(*, size: int = 100) -> list[DataSource]:
    global _CROP_CACHE
    if _CROP_CACHE and (time.time() - _CROP_CACHE[1]) < _CATALOG_TTL_SECONDS:
        return _CROP_CACHE[0]

    query = gql(
        """
        query GetCrops($size: Int!) {
            getCrops(size: $size) {
                status
                message
                payload {
                    id
                    name
                }
            }
        }
        """
    )

    async with farmbetter_client as session:
        result = await session.execute(query, variable_values={"size": size})

    response = result["getCrops"]
    if response["status"] != 200:
        logger.warning("FarmBetter returned %s when fetching crops: %s", response["status"], response.get("message"))
        return _CROP_CACHE[0] if _CROP_CACHE else []

    options = [DataSource(id=item["id"], title=item["name"]) for item in response["payload"]]
    _CROP_CACHE = (options, time.time())
    return options


async def fetch_livestock_options(*, size: int = 100) -> list[DataSource]:
    global _LIVESTOCK_CACHE
    if _LIVESTOCK_CACHE and (time.time() - _LIVESTOCK_CACHE[1]) < _CATALOG_TTL_SECONDS:
        return _LIVESTOCK_CACHE[0]

    query = gql(
        """
        query GetLivestock($size: Int!) {
            getLivestock(size: $size) {
                status
                message
                payload {
                    id
                    name
                }
            }
        }
        """
    )

    async with farmbetter_client as session:
        result = await session.execute(query, variable_values={"size": size})

    response = result["getLivestock"]
    if response["status"] != 200:
        logger.warning(
            "FarmBetter returned %s when fetching livestock: %s", response["status"], response.get("message")
        )
        return _LIVESTOCK_CACHE[0] if _LIVESTOCK_CACHE else []

    options = [DataSource(id=item["id"], title=item["name"]) for item in response["payload"]]
    _LIVESTOCK_CACHE = (options, time.time())
    return options


def select_data_sources(
    *,
    all_options: Sequence[DataSource],
    required_ids: Iterable[str],
) -> list[DataSource]:
    """Ensure that options include every required id even if the catalog response omits them."""

    lookup = {option.id: option for option in all_options}
    selected = list(all_options)
    existing_ids = set(lookup)

    for item_id in required_ids:
        if not item_id or item_id in existing_ids:
            continue
        option = lookup.get(item_id) or DataSource(
            id=item_id,
            title=item_id.replace("_", " ").title(),
        )
        selected.append(option)
        existing_ids.add(item_id)

    return selected
