from pywa import utils
from pywa.types.flows import (
    FlowJSON,
    Screen,
    ScreenData,
    Form,
    Footer,
    Layout,
    Action,
    FlowActionType,
    InputType,
    TextHeading,
    TextInput,
    Dropdown,
    # DataSource,
    DatePicker,
    CompleteAction, DataSource,
)

PROFILE_EDIT_FLOW_JSON = FlowJSON(
    version=utils.Version.FLOW_JSON,
    data_api_version=utils.Version.FLOW_DATA_API,
    routing_model={
        "PROFILE_EDIT": [],
    },
    screens=[
        Screen(
            id="PROFILE_EDIT",
            title="Edit Profile",
            terminal=True,
            data=[
                current_name := ScreenData(key="current_name", example="John Doe"),
                current_preferred_address := ScreenData(key="current_preferred_address", example="Mr."),
                current_gender := ScreenData(key="current_gender", example="male"),
                current_date_of_birth := ScreenData(key="current_date_of_birth", example="1990-01-01"),
                # current_estimated_age := ScreenData(key="current_estimated_age", example=30),
            current_role := ScreenData(key="current_role", example="farmer"),
                current_experience := ScreenData(key="current_experience", example=5),
                current_email := ScreenData(key="current_email", example="john@example.com"),
            ],
            layout=Layout(
                children=[
                    TextHeading(
                        text="Update Your Profile",
                    ),
                    Form(
                        name="form",
                        children=[
                            name := TextInput(
                                name="name",
                                label="Name",
                                input_type=InputType.TEXT,
                                required=True,
                                init_value=current_name.ref,
                            ),
                            preferred_address := TextInput(
                                name="preferred_form_of_address",
                                label="Preferred Form of Address",
                                input_type=InputType.TEXT,
                                required=False,
                                init_value=current_preferred_address.ref,
                            ),
                            gender := Dropdown(
                                name="gender",
                                label="Gender",
                                data_source=[
                                    DataSource(id="male", title="Male"),
                                    DataSource(id="female", title="Female"),
                                    DataSource(id="other", title="Other"),
                                ],
                                init_value=current_gender.ref,
                            ),
                            date_of_birth := DatePicker(
                                name="date_of_birth",
                                label="Date of Birth",
                                init_value=current_date_of_birth.ref,
                            ),
                            # estimated_age := TextInput(
                            #     name="estimated_age",
                            #     label="Estimated Age",
                            #     input_type=InputType.NUMBER,
                            #     init_value=current_estimated_age.ref,
                            # ),
                            role := Dropdown(
                                name="role",
                                label="Role",
                                data_source=[
                                    DataSource(id="farmer", title="Farmer"),
                                    DataSource(id="extension_officer", title="Extension Officer"),
                                    DataSource(id="researcher", title="Researcher"),
                                    DataSource(id="other", title="Other"),
                                ],
                                init_value=current_role.ref,
                            ),
                            experience := TextInput(
                                name="experience",
                                label="Experience (years)",
                                input_type=InputType.NUMBER,
                                init_value=current_experience.ref,
                            ),
                            email := TextInput(
                                name="email",
                                label="Email Address",
                                input_type=InputType.EMAIL,
                                init_value=current_email.ref,
                            ),
                            Footer(
                                label="Update Profile",
                                on_click_action=Action(
                                    name=FlowActionType.COMPLETE,
                                    payload={
                                        "name": name.ref,
                                        "preferred_form_of_address": preferred_address.ref,
                                        "gender": gender.ref,
                                        "date_of_birth": date_of_birth.ref,
                                        # "estimated_age": estimated_age.ref,
                                        "role": role.ref,
                                        "experience": experience.ref,
                                        "email": email.ref,
                                    },
                                ),
                            ),
                        ]
                    )
                ]
            )
        )
    ]
)