from __future__ import annotations

from pywa import Version
from pywa.types.flows import (
    ChipsSelector,
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
    DataSource(id="es", title="Español (Spanish)"),
    DataSource(id="hi", title="हिन्दी (Hindi)"),
    DataSource(id="fr", title="Français (French)"),
    DataSource(id="sw", title="Kiswahili (Swahili)"),
    DataSource(id="vi", title="Tiếng Việt (Vietnamese)"),
    DataSource(id="lg", title="Luganda"),
    DataSource(id="ne", title="नेपाली (Nepali)"),
)


async def build_edit_profile_flow_json() -> FlowJSON:
    """Construct the Flow JSON definition for the edit profile experience."""

    fruit_options = ScreenData(key="fruit_options", example=[DataSource(id="fruit-example", title="Maize")])
    livestock_options = ScreenData(key="livestock_options", example=[DataSource(id="livestock-example", title="Goat")])
    fruit_initial_ids = ScreenData(key="initial_fruit_ids", example=["fruit-example"])
    livestock_initial_ids = ScreenData(key="initial_livestock_ids", example=["livestock-example"])

    #         # ChipsSelector(
    #         #     name="fruit_ids",
    #         #     label="fruit interests",
    #         #     description="Select up to 5 fruits you grow or plan to grow",
    #         #     data_source=fruit_options.ref,
    #         #     max_selected_items=5,
    #         #     init_value=fruit_initial_ids.ref,
    #         # ),

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
                    language_default := ScreenData(key="language_initial_value", example=_LANGUAGE_OPTIONS[0].id),
                    fruit_options := ScreenData(
                        key="fruit_options",
                        example=[
                            DataSource(id="apples", title="Apples"),
                            DataSource(id="bananas", title="Bananas"),
                        ],
                    ),
                    # vegetable_options := ScreenData(
                    #     key="vegetable_options", example=[DataSource(id="vegetable-example", title="Maize")]
                    # ),
                    # livestock_options := ScreenData(
                    #     key="livestock_options", example=[DataSource(id="livestock-example", title="Goat")]
                    # ),
                    fruit_initial_ids := ScreenData(key="initial_fruit_ids", example=["apples"]),
                    # livestock_initial_ids := ScreenData(key="initial_livestock_ids", example=["livestock-example"]),
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
                                    name="date_of_birth",
                                    label="Date of birth",
                                    required=False,
                                    # max_date="today",
                                    helper_text="Enter your date of birth (optional)",
                                    init_value=dob_default.ref,
                                ),
                                Dropdown(
                                    name="preferred_language",
                                    label="Preferred language",
                                    required=True,
                                    data_source=list(_LANGUAGE_OPTIONS),
                                    init_value=language_default.ref,
                                ),
                                ChipsSelector(
                                    name="fruits",
                                    label="🥝 Fruits",
                                    data_source=fruit_options.ref,
                                    init_value=fruit_initial_ids.ref,
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
