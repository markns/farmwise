from datetime import datetime

from farmbetter_client.context import get_or_create_user
from google.adk.agents.callback_context import CallbackContext
from loguru import logger

from farmwise.shared_libraries import constants


async def before_agent(callback_context: CallbackContext) -> None:
    logger.debug(f"Callback context state: {callback_context.state.to_dict()}")

    if "user_context" not in callback_context.state:
        callback_context.state["user_context"] = await get_or_create_user(
            wa_id=callback_context.session.user_id,
        )

    if constants.SYSTEM_TIME not in callback_context.state:
        callback_context.state[constants.SYSTEM_TIME] = str(datetime.now())
