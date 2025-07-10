import logging

from pywa_async import WhatsApp, filters
from pywa_async.types import FlowRequest, FlowCompletion
from pywa_async.types import FlowResponse, FlowRequestActionType

from farmwise.whatsapp.flows.sign_up.db import user_repository


@WhatsApp.on_flow_request("/sign-up-flow")
async def on_sign_up_request(_: WhatsApp, flow: FlowRequest) -> FlowResponse | None:
    if flow.has_error:
        logging.error("Flow request has error: %s", flow.data)
        return


@WhatsApp.on_flow_completion()
async def handle_flow_completion(_: WhatsApp, flow: FlowCompletion):
    print("Flow completed successfully")
    print(flow.token)
    print(flow.response)


@on_sign_up_request.on(
    action=FlowRequestActionType.DATA_EXCHANGE,
    screen="SIGN_UP",
    filters=filters.new(lambda _, request: user_repository.exists(request.data["email"])),
)
async def if_already_registered(_: WhatsApp, request: FlowRequest) -> FlowResponse | None:
    return FlowResponse(
        version=request.version,
        screen="LOGIN",
        error_message="You are already registered. Please login",
        data={
            "email_initial_value": request.data["email"],
            "password_initial_value": request.data["password"],
        },
    )


@on_sign_up_request.on(
    action=FlowRequestActionType.DATA_EXCHANGE,
    screen="SIGN_UP",
    filters=filters.new(lambda _, request: request.data["password"] != request.data["confirm_password"]),
)
async def if_passwords_dont_match(_: WhatsApp, request: FlowRequest) -> FlowResponse | None:
    return FlowResponse(
        version=request.version,
        screen=request.screen,
        error_message="Passwords do not match",
        data={
            "first_name_initial_value": request.data["first_name"],
            "last_name_initial_value": request.data["last_name"],
            "email_initial_value": request.data["email"],
            "password_initial_value": "",
            "confirm_password_initial_value": "",
        },
    )


@on_sign_up_request.on(
    action=FlowRequestActionType.DATA_EXCHANGE,
    screen="SIGN_UP",
    filters=filters.new(lambda _, request: not any(char.isdigit() for char in request.data["password"])),
)
async def if_password_does_not_contain_number(
        _: WhatsApp, request: FlowRequest
) -> FlowResponse | None:
    return FlowResponse(
        version=request.version,
        screen=request.screen,
        error_message="Password must contain at least one number",
        data={
            "first_name_initial_value": request.data["first_name"],
            "last_name_initial_value": request.data["last_name"],
            "email_initial_value": request.data["email"],
            "password_initial_value": "",
            "confirm_password_initial_value": "",
        },
    )


@on_sign_up_request.on(action=FlowRequestActionType.DATA_EXCHANGE, screen="SIGN_UP")
async def submit_signup(_: WhatsApp, request: FlowRequest) -> FlowResponse | None:
    user_repository.create(request.data["email"], request.data)
    return FlowResponse(
        version=request.version,
        screen="LOGIN",
        data={
            "email_initial_value": request.data["email"],
            "password_initial_value": "",
        },
    )


@on_sign_up_request.on(
    action=FlowRequestActionType.DATA_EXCHANGE,
    screen="LOGIN",
    filters=filters.new(lambda _, request: not user_repository.exists(request.data["email"])),
)
async def if_not_registered(_: WhatsApp, request: FlowRequest) -> FlowResponse | None:
    return FlowResponse(
        version=request.version,
        screen="SIGN_UP",
        error_message="You are not registered. Please sign up",
        data={
            "first_name_initial_value": "",
            "last_name_initial_value": "",
            "email_initial_value": request.data["email"],
            "password_initial_value": "",
            "confirm_password_initial_value": "",
        },
    )


@on_sign_up_request.on(
    action=FlowRequestActionType.DATA_EXCHANGE,
    screen="LOGIN",
    filters=filters.new(
        lambda _, request: not user_repository.is_password_valid(request.data["email"], request.data["password"])),
)
async def if_incorrect_password(_: WhatsApp, request: FlowRequest) -> FlowResponse | None:
    return FlowResponse(
        version=request.version,
        screen=request.screen,
        error_message="Incorrect password",
        data={
            "email_initial_value": request.data["email"],
            "password_initial_value": "",
        },
    )


@on_sign_up_request.on(action=FlowRequestActionType.DATA_EXCHANGE, screen="LOGIN")
async def login_success(_: WhatsApp, request: FlowRequest) -> FlowResponse | None:
    return FlowResponse(
        version=request.version,
        screen="LOGIN_SUCCESS",
        data={},
    )
