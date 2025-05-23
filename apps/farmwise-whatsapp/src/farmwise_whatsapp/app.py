import base64
import logging
from contextlib import asynccontextmanager
from enum import Enum

from farmwise_client import AgentClient
from farmwise_schema.schema import Action, WhatsappResponse
from fastapi import FastAPI
from loguru import logger
from loguru_logging_intercept import InterceptHandler
from pywa.types import Command, Section, SectionList, SectionRow
from pywa_async import WhatsApp, filters, types
from pywa_async.types.base_update import BaseUserUpdateAsync

from .core.config import settings
from .utils import _convert_md_to_whatsapp

# Intercept standard logging and route to loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)


# TODO: load these commands from the FarmWise service
class Commands(Enum):
    REGISTER_FIELD = Command(name="Register a field", description="Register a new field")
    SELECT_MAIZE_VARIETY = Command(name="Select a maize seed variety", description="Select a maize seed variety")
    SHOW_SUITABLE_CROPS = Command(name="Show suitable crops", description="Show suitable crops for a location")


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Startup: Initializing resources...")

    # Ice breakers don't allow emojis when set via API, so set these in the WhatsApp Manager
    ice_breakers = [
        "🌻 What crops are suitable for my area",
        "🌤️ Give me a weather forecast",
        "🌱 Calculate fertilizer for my field",
    ]
    # TODO: It's all or nothing with conversational automation, so we can't set commands and not ice breakers
    # await wa.update_conversational_automation(
    #     enable_chat_opened=True,
    #     # ice_breakers=ice_breakers,
    #     commands=[command.value for command in Commands],
    # )

    yield  # Run the application
    print("Shutdown: Cleaning up resources...")


app = FastAPI(lifespan=lifespan)

wa = WhatsApp(
    phone_id=settings.WHATSAPP_PHONE_ID,  # The phone id you got from the API Setup
    token=settings.WHATSAPP_TOKEN,  # The token you got from the API Setup
    server=app,
    callback_url="https://3df7-105-163-156-68.ngrok-free.app",
    verify_token="xyz123fdsfds",
    app_id=1392339421934377,
    app_secret="b8a5543a9bf425a0e87676641569b2b4",
)

# TODO: move to dependencies
agent_client = AgentClient(base_url=settings.AGENT_URL)


async def _send_response(response: WhatsappResponse, msg: BaseUserUpdateAsync):
    if Action.request_location in response.actions:
        await msg.reply_location_request(response.content)
    elif response.section_list:
        await msg.reply_text(
            text=_convert_md_to_whatsapp(response.content),
            # todo: use pywa types directly in WhatsappResponse to prevent this reconstruction?
            buttons=SectionList(
                # TODO: Should have a better way of meeting the char and list size limits
                response.section_list.button_title[:20],
                sections=[
                    Section(
                        title=section.title[:24],
                        rows=[
                            SectionRow(title=row.title[:24], callback_data=row.callback_data)
                            for row in section.rows[:10]
                        ],
                    )
                    for section in response.section_list.sections
                ],
            ),
        )
    else:
        await msg.reply_text(_convert_md_to_whatsapp(response.content))


# TODO: Chat opened is not being triggered...
#  https://developers.facebook.com/docs/whatsapp/cloud-api/phone-numbers/conversational-components#welcome-messages
#  Welcome messages are currently not functioning as intended.
#  https://developers.facebook.com/community/threads/1842836979827258/?post_id=1842836983160591
@wa.on_chat_opened
async def chat_opened(client: WhatsApp, chat_opened: types.ChatOpened):
    logger.info(f"CHAT OPENED USER: {chat_opened}")
    # TODO: Do we already want to register a user here?
    await chat_opened.reply_text(f"""
Hi {chat_opened.from_user.name}! 👋 You’re now connected to FarmWise – your trusted partner for smart farming advice.

Here’s what you can do:
✅ Get tailored recommendations for your crops
✅ Ask about pests, diseases, and weather risks
✅ Record planting and input data
✅ Get reminders for key farm activities

Just type your question or send a photo, and we’ll help you grow better!

Reply with “menu” to see all services.
    """)


@wa.on_message(filters.location)
async def location_handler(_: WhatsApp, msg: types.Message):
    logger.info(f"LOCATION USER: {msg}")
    await msg.indicate_typing()
    response = await agent_client.ainvoke(
        message=f"My location is {msg.location}",
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, msg)


@wa.on_message(filters.text)
async def message_handler(_: WhatsApp, msg: types.Message):
    logger.info(f"MESSAGE USER: {msg}")
    await msg.indicate_typing()
    response = await agent_client.ainvoke(
        message=msg.text,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )
    # TODO: Add error handling here.
    logger.info(f"AGENT: {response}")
    await _send_response(response, msg)


@wa.on_callback_selection
async def callback_handler(_: WhatsApp, sel: types.CallbackSelection):
    logger.info(f"CALLBACK SELECTION USER: {sel}")
    await sel.indicate_typing()
    response = await agent_client.ainvoke(
        message=sel.data,
        user_id=sel.from_user.wa_id,
        user_name=sel.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, sel)


@wa.on_message(filters.image)
async def image_handler(_: WhatsApp, msg: types.Message):
    await msg.indicate_typing()
    img_bytes = await msg.image.download(in_memory=True)
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    await msg.mark_as_read()
    response = await agent_client.ainvoke(
        # FIXME: This borks when no caption is provided.
        message=msg.caption,
        image=img_b64,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, msg)


@wa.on_raw_update
async def raw_update_handler(_: WhatsApp, update: dict):
    logger.warning(f"RAW UPDATE: {update}")
