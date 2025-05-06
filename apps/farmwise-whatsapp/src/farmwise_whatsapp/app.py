import base64
import logging
from contextlib import asynccontextmanager
from enum import Enum

from farmwise_client import AgentClient
from farmwise_schema.schema import Action, WhatsappResponse
from fastapi import FastAPI
from pywa.types import Command, Section, SectionList, SectionRow
from pywa_async import WhatsApp, filters, types
from pywa_async.types.base_update import BaseUserUpdateAsync

from farmwise_whatsapp.core.config import settings  # Import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: load these commands from the FarmWise service
class Commands(Enum):
    REGISTER_FIELD = Command(name="Register a field", description="Register a new field")
    SELECT_MAIZE_VARIETY = Command(name="Select a maize seed variety", description="Select a maize seed variety")
    SHOW_SUITABLE_CROPS = Command(name="Show suitable crops", description="Show suitable crops for a location")


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Startup: Initializing resources...")

    # TODO: Ice breakers is only showing the last command - why?
    # ice_breakers = [c.value.name for c in Commands]
    ice_breakers = []
    print(ice_breakers)
    await wa.update_conversational_automation(
        enable_chat_opened=True,
        ice_breakers=ice_breakers,
        commands=[command.value for command in Commands],
    )

    yield  # Run the application
    print("Shutdown: Cleaning up resources...")


app = FastAPI(lifespan=lifespan)

wa = WhatsApp(
    phone_id=settings.WHATSAPP_PHONE_ID,  # The phone id you got from the API Setup
    token=settings.WHATSAPP_TOKEN,  # The token you got from the API Setup
    server=app,
    callback_url="https://84a7-105-163-2-144.ngrok-free.app",
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
            response.content,
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
        await msg.reply_text(response.content)


# TODO: Chat opened is not being triggered...
@wa.on_chat_opened
async def chat_opened_handler(client: WhatsApp, chat_opened: types.ChatOpened):
    logger.info(f"CHAT OPENED USER: {chat_opened}")
    # TODO: Do we already want to register a user here?
    await chat_opened.reply_text(f"""Hi {chat_opened.from_user.name}! 👋 You’re now connected to FarmWise – your trusted partner for smart farming advice.

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
    await msg.mark_as_read()
    response = await agent_client.ainvoke(
        message=f"My location is {msg.location}",
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, msg)


@wa.on_raw_update
async def raw_update_handler(_: WhatsApp, update: dict):
    logger.warning(f"RAW UPDATE: {update}")


@wa.on_message(filters.text)
async def message_handler(_: WhatsApp, msg: types.Message):
    logger.info(f"MESSAGE USER: {msg}")
    await msg.mark_as_read()
    response = await agent_client.ainvoke(
        message=msg.text,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, msg)


@wa.on_callback_selection
async def callback_handler(_: WhatsApp, sel: types.CallbackSelection):
    logger.info(f"CALLBACK SELECTION USER: {sel}")
    await sel.mark_as_read()
    response = await agent_client.ainvoke(
        message=sel.data,
        user_id=sel.from_user.wa_id,
        user_name=sel.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, sel)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@wa.on_message(filters.image)
async def on_image(_: WhatsApp, msg: types.Message):
    logger.info(f"IMAGE USER: {msg}")
    img_bytes = await msg.image.download(in_memory=True)
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    await msg.mark_as_read()
    response = await agent_client.ainvoke(
        message=msg.caption,
        image=img_b64,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )
    logger.info(f"AGENT: {response}")
    await _send_response(response, msg)


#
#
# MESSAGE_ID_TO_TEXT: dict[str, str] = {}  # msg_id -> text
# POPULAR_LANGUAGES = {"en": ("English", "🇺🇸"), "es": ("Español", "🇪🇸"), "fr": ("Français", "🇫🇷")}
# OTHER_LANGUAGES = {
#     "iw": ("עברית", "🇮🇱"),
#     "ar": ("العربية", "🇸🇦"),
#     "ru": ("Русский", "🇷🇺"),
#     "de": ("Deutsch", "🇩🇪"),
#     "it": ("Italiano", "🇮🇹"),
#     "pt": ("Português", "🇵🇹"),
#     "ja": ("日本語", "🇯🇵"),
# }
#
#
# # @wa.on_message(filters.text)
# @wa.on_message(filters=filters.contains("translate"))
# async def offer_translation(_: WhatsApp, msg: types.Message):
#     msg_id = await msg.reply_text(
#         text="Choose language to translate to:",
#         buttons=types.SectionList(
#             button_title="🌐 Choose Language",
#             sections=[
#                 types.Section(
#                     title="🌟 Popular languages",
#                     rows=[
#                         types.SectionRow(
#                             title=f"{flag} {name}",
#                             callback_data=f"translate:{code}",
#                         )
#                         for code, (name, flag) in POPULAR_LANGUAGES.items()
#                     ],
#                 ),
#                 types.Section(
#                     title="🌐 Other languages",
#                     rows=[
#                         types.SectionRow(
#                             title=f"{flag} {name}",
#                             callback_data=f"translate:{code}",
#                         )
#                         for code, (name, flag) in OTHER_LANGUAGES.items()
#                     ],
#                 ),
#             ],
#         ),
#     )
#     # Save the message ID so we can use it later to get the original text.
#     MESSAGE_ID_TO_TEXT[msg_id.id] = msg.text
#
#
# @wa.on_callback_selection(filters.startswith("translate:"))
# async def translate(_: WhatsApp, sel: types.CallbackSelection):
#     logger.warn(MESSAGE_ID_TO_TEXT)
#     logger.warn(sel.reply_to_message.message_id)
#     lang_code = sel.data.split(":")[-1]
#     try:
#         # every CallbackSelection has a reference to the original message (the selection's message)
#         original_text = MESSAGE_ID_TO_TEXT[sel.reply_to_message.message_id]
#     except KeyError:  # If the bot was restarted, the message ID is no longer valid.
#         await sel.react("❌")
#         await sel.reply_text(text="Original message not found. Please send a new message.")
#         return
#     try:
#         translated = await translator.translate(original_text, dest=lang_code)
#     except Exception as e:
#         await sel.react("❌")
#         await sel.reply_text(text="An error occurred. Please try again.")
#         logger.exception(e)
#         return
#
#     await sel.reply_text(text=f"Translated to {translated.dest}:\n{translated.text}")
#
#
# @wa.on_message(filters.command(Commands.SELECT_COLOUR.value.name))
# async def select_colour(_: WhatsApp, msg: types.Message):
#     print("In select colour handler")
#     await msg.reply_text(
#         header="Select your favorite color",
#         text="Tap a button to select your favorite color:",
#         # footer='⚡ Powered by PyWa',
#         buttons=SectionList(
#             button_title="Colors",
#             sections=[
#                 Section(
#                     title="Popular Colors",
#                     rows=[
#                         SectionRow(
#                             title="🟥 Red",
#                             callback_data="color:red",
#                             description="The color of blood",
#                         ),
#                         SectionRow(
#                             title="🟩 Green",
#                             callback_data="color:green",
#                             description="The color of grass",
#                         ),
#                         SectionRow(
#                             title="🟦 Blue",
#                             callback_data="color:blue",
#                             description="The color of the sky",
#                         ),
#                     ],
#                 ),
#                 Section(
#                     title="Other Colors",
#                     rows=[
#                         SectionRow(
#                             title="🟧 Orange",
#                             callback_data="color:orange",
#                             description="The color of an orange",
#                         ),
#                         SectionRow(
#                             title="🟪 Purple",
#                             callback_data="color:purple",
#                             description="The color of a grape",
#                         ),
#                         SectionRow(
#                             title="🟨 Yellow",
#                             callback_data="color:yellow",
#                             description="The color of the sun",
#                         ),
#                     ],
#                 ),
#             ],
#         ),
#     )
