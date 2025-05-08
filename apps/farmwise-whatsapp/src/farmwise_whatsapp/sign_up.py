import os

from pywa import utils
from pywa.types.flows import (
    Action,
    EmbeddedLink,
    FlowActionType,
    FlowJSON,
    Footer,
    Form,
    InputType,
    Layout,
    Next,
    NextType,
    OptIn,
    Screen,
    ScreenData,
    TextHeading,
    TextInput,
    TextSubheading,
)

SIGN_UP_FLOW_JSON = FlowJSON(
    version=utils.Version.FLOW_JSON,
    data_api_version=utils.Version.FLOW_DATA_API,
    routing_model={
        "START": ["SIGN_UP", "LOGIN"],
        "SIGN_UP": ["LOGIN"],
        "LOGIN": ["LOGIN_SUCCESS"],
        "LOGIN_SUCCESS": [],
    },
    screens=[
        Screen(
            id="START",
            title="Home",
            layout=Layout(
                children=[
                    TextHeading(
                        text="Welcome to our app",
                    ),
                    EmbeddedLink(
                        text="Click here to sign up",
                        on_click_action=Action(
                            name=FlowActionType.NAVIGATE,
                            next=Next(
                                type=NextType.SCREEN,
                                name="SIGN_UP",
                            ),
                            payload={
                                "first_name_initial_value": "",
                                "last_name_initial_value": "",
                                "email_initial_value": "",
                                "password_initial_value": "",
                                "confirm_password_initial_value": "",
                            },
                        ),
                    ),
                    EmbeddedLink(
                        text="Click here to login",
                        on_click_action=Action(
                            name=FlowActionType.NAVIGATE,
                            next=Next(
                                type=NextType.SCREEN,
                                name="LOGIN",
                            ),
                            payload={
                                "email_initial_value": "",
                                "password_initial_value": "",
                            },
                        ),
                    ),
                ]
            ),
        ),
        Screen(
            id="SIGN_UP",
            title="Sign Up",
            data=[
                first_name_initial_value := ScreenData(key="first_name_initial_value", example="John"),
                last_name_initial_value := ScreenData(key="last_name_initial_value", example="Doe"),
                email_initial_value := ScreenData(key="email_initial_value", example="john.doe@gmail.com"),
                password_initial_value := ScreenData(key="password_initial_value", example="abc123"),
                confirm_password_initial_value := ScreenData(key="confirm_password_initial_value", example="abc123"),
            ],
            layout=Layout(
                children=[
                    TextHeading(
                        text="Please enter your details",
                    ),
                    EmbeddedLink(
                        text="Already have an account?",
                        on_click_action=Action(
                            name=FlowActionType.NAVIGATE,
                            next=Next(
                                type=NextType.SCREEN,
                                name="LOGIN",
                            ),
                            payload={
                                "email_initial_value": "",
                                "password_initial_value": "",
                            },
                        ),
                    ),
                    Form(
                        name="form",
                        children=[
                            first_name := TextInput(
                                name="first_name",
                                label="First Name",
                                input_type=InputType.TEXT,
                                required=True,
                                init_value=first_name_initial_value.ref,
                            ),
                            last_name := TextInput(
                                name="last_name",
                                label="Last Name",
                                input_type=InputType.TEXT,
                                required=True,
                                init_value=last_name_initial_value.ref,
                            ),
                            email := TextInput(
                                name="email",
                                label="Email Address",
                                input_type=InputType.EMAIL,
                                required=True,
                                init_value=email_initial_value.ref,
                            ),
                            password := TextInput(
                                name="password",
                                label="Password",
                                input_type=InputType.PASSWORD,
                                min_chars=8,
                                max_chars=16,
                                helper_text="Password must contain at least one number",
                                required=True,
                                init_value=password_initial_value.ref,
                            ),
                            confirm_password := TextInput(
                                name="confirm_password",
                                label="Confirm Password",
                                input_type=InputType.PASSWORD,
                                min_chars=8,
                                max_chars=16,
                                required=True,
                                init_value=confirm_password_initial_value.ref,
                            ),
                            Footer(
                                label="Done",
                                on_click_action=Action(
                                    name=FlowActionType.DATA_EXCHANGE,
                                    payload={
                                        "first_name": first_name.ref,
                                        "last_name": last_name.ref,
                                        "email": email.ref,
                                        "password": password.ref,
                                        "confirm_password": confirm_password.ref,
                                    },
                                ),
                            ),
                        ],
                    ),
                ]
            ),
        ),
        Screen(
            id="LOGIN",
            title="Login",
            terminal=True,
            data=[
                email_initial_value := ScreenData(key="email_initial_value", example="john.doe@gmail.com"),
                password_initial_value := ScreenData(key="password_initial_value", example="abc123"),
            ],
            layout=Layout(
                children=[
                    TextHeading(text="Please enter your details"),
                    EmbeddedLink(
                        text="Don't have an account?",
                        on_click_action=Action(
                            name=FlowActionType.NAVIGATE,
                            next=Next(
                                type=NextType.SCREEN,
                                name="SIGN_UP",
                            ),
                            payload={
                                "email_initial_value": "",
                                "password_initial_value": "",
                                "confirm_password_initial_value": "",
                                "first_name_initial_value": "",
                                "last_name_initial_value": "",
                            },
                        ),
                    ),
                    Form(
                        name="form",
                        children=[
                            email := TextInput(
                                name="email",
                                label="Email Address",
                                input_type=InputType.EMAIL,
                                required=True,
                                init_value=email_initial_value.ref,
                            ),
                            password := TextInput(
                                name="password",
                                label="Password",
                                input_type=InputType.PASSWORD,
                                required=True,
                                init_value=password_initial_value.ref,
                            ),
                            Footer(
                                label="Done",
                                on_click_action=Action(
                                    name=FlowActionType.DATA_EXCHANGE,
                                    payload={
                                        "email": email.ref,
                                        "password": password.ref,
                                    },
                                ),
                            ),
                        ],
                    ),
                ]
            ),
        ),
        Screen(
            id="LOGIN_SUCCESS",
            title="Success",
            terminal=True,
            layout=Layout(
                children=[
                    TextHeading(
                        text="Welcome to our store",
                    ),
                    TextSubheading(
                        text="You are now logged in",
                    ),
                    Form(
                        name="form",
                        children=[
                            stay_logged_in := OptIn(
                                name="stay_logged_in",
                                label="Stay logged in",
                            ),
                            Footer(
                                label="Done",
                                on_click_action=Action(
                                    name=FlowActionType.COMPLETE,
                                    payload={
                                        "stay_logged_in": stay_logged_in.ref,
                                    },
                                ),
                            ),
                        ],
                    ),
                ]
            ),
        ),
    ],
)


from pywa import WhatsApp
from pywa.types.flows import FlowCategory

wa = WhatsApp(
    phone_id=os.environ.get("WHATSAPP_PHONE_ID"),  # The phone id you got from the API Setup
    token=os.environ.get("WHATSAPP_TOKEN"),  # The token you got from the API Setup
    verify_token="xyz123",
    app_id=1392339421934377,
    app_secret="b8a5543a9bf425a0e87676641569b2b4",
    business_account_id="1220686245817945",  # the ID of the WhatsApp Business Account
)

flow_id = wa.create_flow(
    name="Sign Up Flow",
    categories=[FlowCategory.SIGN_IN, FlowCategory.SIGN_UP],
)

wa.update_flow_metadata(
    flow_id=flow_id,
    endpoint_uri="https://my-server.com/sign-up-flow",
)

from pywa.errors import FlowUpdatingError

try:
    wa.update_flow_json(
        flow_id=flow_id,
        flow_json=SIGN_UP_FLOW_JSON,
    )
    print("Flow updated successfully")
except FlowUpdatingError as e:
    print("Flow updating failed")
    print(wa.get_flow(flow_id=flow_id).validation_errors)
