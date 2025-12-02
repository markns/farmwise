from datetime import datetime

from google.adk.agents.callback_context import CallbackContext
from loguru import logger

from farmwise.assistant.shared_libraries import constants
from farmwise.context import get_or_create_user


# checking that the customer profile is loaded as state.
async def before_agent(callback_context: CallbackContext) -> None:
    logger.debug(f"Callback context state: {callback_context.state.to_dict()}")

    if "user_profile" not in callback_context.state:
        callback_context.state["user_profile"] = await get_or_create_user(
            wa_id=callback_context.user_id,
        )

    if constants.SYSTEM_TIME not in callback_context.state:
        callback_context.state[constants.SYSTEM_TIME] = str(datetime.now())
