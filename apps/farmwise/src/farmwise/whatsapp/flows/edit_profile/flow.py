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
    FormComponent,
    Layout,
    NavigateAction,
    Next,
    Screen,
    ScreenData,
    TextBody,
    TextHeading,
    TextInput,
)

FLOW_ENDPOINT = "/flows/edit-profile"
FLOW_NAME = "edit_profile"
EDIT_PROFILE_SCREEN_ID = "EDIT_PROFILE"
EDIT_CROPS_SCREEN_ID = "EDIT_CROPS"
EDIT_LIVESTOCK_SCREEN_ID = "EDIT_LIVESTOCK"
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
    return FlowJSON(
        version=Version.FLOW_JSON,
        data_api_version=Version.FLOW_DATA_API,
        routing_model={
            EDIT_PROFILE_SCREEN_ID: [EDIT_CROPS_SCREEN_ID],
            EDIT_CROPS_SCREEN_ID: [EDIT_LIVESTOCK_SCREEN_ID],
            EDIT_LIVESTOCK_SCREEN_ID: [],
        },
        screens=[
            Screen(
                id=EDIT_PROFILE_SCREEN_ID,
                title="Update your farmbetter profile",
                data=[
                    first_name_default := ScreenData(key="first_name_initial_value", example="Hudson"),
                    last_name_default := ScreenData(key="last_name_initial_value", example="Ndege"),
                    gender_default := ScreenData(key="gender_initial_value", example=_GENDER_OPTIONS[0].id),
                    dob_default := ScreenData(key="dob_initial_value", example="1979-03-06"),
                    language_default := ScreenData(key="language_initial_value", example=_LANGUAGE_OPTIONS[0].id),
                    cereal_options := ScreenData(
                        key="cereal_options",
                        example=[
                            DataSource(id="maize", title="Maize"),
                            DataSource(id="barley", title="Barley"),
                        ],
                    ),
                    vegetable_options := ScreenData(
                        key="vegetable_options",
                        example=[
                            DataSource(id="beans", title="Beans"),
                            DataSource(id="radishes", title="Radishes"),
                        ],
                    ),
                    fruit_options := ScreenData(
                        key="fruit_options",
                        example=[
                            DataSource(id="apples", title="Apples"),
                            DataSource(id="bananas", title="Bananas"),
                        ],
                    ),
                    livestock_options := ScreenData(
                        key="livestock_options",
                        example=[
                            DataSource(id="cattle", title="Cattle"),
                            DataSource(id="goat", title="Goat"),
                        ],
                    ),
                    poultry_options := ScreenData(
                        key="poultry_options",
                        example=[
                            DataSource(id="chickens", title="Chickens"),
                            DataSource(id="quails", title="Quails"),
                        ],
                    ),
                    cereal_initial_ids := ScreenData(key="cereal_ids", example=["maize"]),
                    vegetable_initial_ids := ScreenData(key="vegetable_ids", example=["radishes"]),
                    fruit_initial_ids := ScreenData(key="fruit_ids", example=["apples"]),
                    livestock_initial_ids := ScreenData(key="livestock_ids", example=["cattle"]),
                    poultry_initial_ids := ScreenData(key="poultry_ids", example=["chickens"]),
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
                            ],
                        ),
                        Footer(
                            label="Save profile",
                            on_click_action=NavigateAction(
                                next=Next(name=EDIT_CROPS_SCREEN_ID),
                            ),
                        ),
                    ]
                ),
            ),
            Screen(
                id=EDIT_CROPS_SCREEN_ID,
                title="Update your crop interests",
                # data=[],
                layout=Layout(
                    children=[
                        TextHeading(text="What crops do you grow?"),
                        crops_form := Form(
                            name=PROFILE_FORM_NAME,
                            children=[
                                ChipsSelector(
                                    name="cereals",
                                    label="🌾 Cereals",
                                    data_source=cereal_options.ref_in(EDIT_PROFILE_SCREEN_ID),
                                    init_value=cereal_initial_ids.ref_in(EDIT_PROFILE_SCREEN_ID),
                                ),
                                ChipsSelector(
                                    name="vegetables",
                                    label="🥕 Vegetables",
                                    data_source=vegetable_options.ref_in(EDIT_PROFILE_SCREEN_ID),
                                    init_value=vegetable_initial_ids.ref_in(EDIT_PROFILE_SCREEN_ID),
                                ),
                                ChipsSelector(
                                    name="fruits",
                                    label="🥝 Fruits",
                                    data_source=fruit_options.ref_in(EDIT_PROFILE_SCREEN_ID),
                                    init_value=fruit_initial_ids.ref_in(EDIT_PROFILE_SCREEN_ID),
                                ),
                            ],
                        ),
                        Footer(
                            label="Save crop interests",
                            on_click_action=NavigateAction(
                                next=Next(name=EDIT_LIVESTOCK_SCREEN_ID),
                            ),
                        ),
                    ]
                ),
            ),
            Screen(
                id=EDIT_LIVESTOCK_SCREEN_ID,
                title="Update your livestock interests",
                terminal=True,
                layout=Layout(
                    children=[
                        livestock_form := Form(
                            name=PROFILE_FORM_NAME,
                            children=[
                                TextHeading(text="What livestock do you keep?"),
                                ChipsSelector(
                                    name="livestock",
                                    label="🐄 Livestock",
                                    data_source=livestock_options.ref_in(EDIT_PROFILE_SCREEN_ID),
                                    init_value=livestock_initial_ids.ref_in(EDIT_PROFILE_SCREEN_ID),
                                ),
                                ChipsSelector(
                                    name="poultry",
                                    label="🐓 Poultry",
                                    data_source=poultry_options.ref_in(EDIT_PROFILE_SCREEN_ID),
                                    init_value=poultry_initial_ids.ref_in(EDIT_PROFILE_SCREEN_ID),
                                ),
                            ],
                        ),
                        Footer(
                            label="Save livestock interests",
                            on_click_action=CompleteAction(
                                payload={
                                    c.name: c.ref_in(EDIT_PROFILE_SCREEN_ID)
                                    for c in profile_form.children
                                    if isinstance(c, FormComponent)
                                }
                                | {
                                    c.name: c.ref_in(EDIT_CROPS_SCREEN_ID)
                                    for c in crops_form.children
                                    if isinstance(c, FormComponent)
                                }
                                | {c.name: c.ref for c in livestock_form.children if isinstance(c, FormComponent)},
                                # payload=profile_form.ref,
                            ),
                        ),
                    ]
                ),
            ),
        ],
    )
