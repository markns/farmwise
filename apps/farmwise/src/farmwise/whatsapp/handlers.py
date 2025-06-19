import logging
import os
from enum import Enum

from loguru import logger
from loguru_logging_intercept import InterceptHandler
from pywa.types import Button, Command, Section, SectionList, SectionRow
from pywa_async import WhatsApp, filters, types
from pywa_async.types.base_update import BaseUserUpdateAsync
from pywa_async.types.others import Contact as PywaContact

from farmwise.schema import Action, AudioResponse, Contact, UserInput, WhatsAppResponse
from farmwise.schema import SectionList as FarmwiseSectionList
from farmwise.service import farmwise
from farmwise.settings import settings
from farmwise.whatsapp.utils import _convert_md_to_whatsapp

# Intercept standard logging and route to loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)


# TODO: load these commands from the FarmWise service
class Commands(Enum):
    REGISTER_FIELD = Command(name="Register a field", description="Register a new field")
    SELECT_MAIZE_VARIETY = Command(name="Select a maize seed variety", description="Select a maize seed variety")
    SHOW_SUITABLE_CROPS = Command(name="Show suitable crops", description="Show suitable crops for a location")


async def _send_response(response: WhatsAppResponse, msg: BaseUserUpdateAsync):
    """Send a WhatsApp response using the appropriate message type based on response content."""

    # Priority 1: Location request (highest priority)
    if Action.request_location in response.actions:
        await msg.reply_location_request(response.content)
        return

    # Prepare interactive elements that can be used with various message types
    buttons = None
    section_list = None

    if response.section_list:
        section_list = _convert_to_pywa_section_list(response.section_list)
    elif response.buttons:
        if len(response.buttons) > 3:
            logger.warning(f"Max allowed buttons: 3. {response}")
        buttons = [Button(b.title[:20], b.callback_data) for b in response.buttons[:3]]

    # Priority 2: Media messages (can include buttons/section_lists)
    if response.image_url:
        await msg.reply_image(
            image=response.image_url,
            caption=response.content,
            buttons=section_list or buttons,
        )
        return

    # Priority 3: Contact sharing
    if response.contact:
        contact = _convert_to_pywa_contact(response.contact)
        await msg.reply_contact(contact=contact)
        # If there are buttons/section_lists, send them in a follow-up text message
        if section_list or buttons:
            await msg.reply_text(
                text=_convert_md_to_whatsapp(response.content) if response.content else "Choose an option:",
                buttons=section_list or buttons,
            )
        return

    # Priority 4: Product sharing
    if response.product:
        await msg.reply_product(
            catalog_id=response.product.catalog_id,
            sku=response.product.sku,
            body=response.product.body,
            footer=response.product.footer,
        )
        # If there are buttons/section_lists, send them in a follow-up text message
        if section_list or buttons:
            await msg.reply_text(
                text=_convert_md_to_whatsapp(response.content) if response.content else "Choose an option:",
                buttons=section_list or buttons,
            )
        return

    # Priority 5: Interactive text messages with section lists or buttons
    if section_list or buttons:
        await msg.reply_text(
            text=_convert_md_to_whatsapp(response.content),
            buttons=section_list or buttons,
        )
        return

    # Priority 6: Plain text message (default)
    await msg.reply_text(_convert_md_to_whatsapp(response.content))


def _convert_to_pywa_contact(contact: Contact) -> PywaContact:
    """Convert our Contact model to pywa Contact type."""

    # Create name object
    name = PywaContact.Name(formatted_name=contact.name)

    # Create phone list if phone is provided
    phones = []
    if contact.phone:
        phones.append(PywaContact.Phone(phone=contact.phone, wa_id=contact.phone, type="MOBILE"))

    # Create email list if email is provided
    emails = []
    if contact.email:
        emails.append(PywaContact.Email(email=contact.email, type="WORK"))

    # Create organization list if organization is provided
    orgs = []
    if contact.organization:
        orgs.append(PywaContact.Org(company=contact.organization))

    return PywaContact(
        name=name,
        phones=phones,
        emails=emails,
        orgs=orgs,
    )


def _convert_to_pywa_section_list(section_list: FarmwiseSectionList) -> SectionList:
    """Convert our SectionList model to pywa SectionList type."""
    return SectionList(
        # TODO: Should have a better way of meeting the char and list size limits
        section_list.button_title[:20],
        sections=[
            Section(
                title=section.title[:24],
                rows=[SectionRow(title=row.title[:24], callback_data=row.callback_data) for row in section.rows[:10]],
            )
            for section in section_list.sections[:10]
        ],
    )


# TODO: Chat opened is not being triggered...
#  https://developers.facebook.com/docs/whatsapp/cloud-api/phone-numbers/conversational-components#welcome-messages
#  Welcome messages are currently not functioning as intended.
#  https://developers.facebook.com/community/threads/1842836979827258/?post_id=1842836983160591
@WhatsApp.on_chat_opened
async def chat_opened(client: WhatsApp, chat_opened: types.ChatOpened):
    logger.info(f"CHAT OPENED USER: {chat_opened}")
    # TODO: Do we already want to register a user here?
    await chat_opened.reply_text(f"""
Hi {chat_opened.from_user.name}! 👋 You're now connected to FarmWise – your trusted partner for smart farming advice.

Here's what you can do:
✅ Get tailored recommendations for your crops
✅ Ask about pests, diseases, and weather risks
✅ Record planting and input data
✅ Get reminders for key farm activities

Just type your question or send a photo, and we'll help you grow better!

Reply with "menu" to see all services.
    """)


@WhatsApp.on_message(filters.location)
async def location_handler(_: WhatsApp, msg: types.Message):
    logger.info(f"LOCATION USER: {msg}")
    await msg.indicate_typing()

    user_input = UserInput(
        message=f"My location is {msg.location}",
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )

    response = await farmwise.invoke(user_input)
    async for event in response:
        match event.response:
            case WhatsAppResponse():
                await _send_response(event.response, msg)
            case AudioResponse():
                await _send_audio_response(event.response, msg)
            case _:
                print("Unknown response type")

        if event.has_more:
            await msg.indicate_typing()



async def _send_audio_response(response: AudioResponse, msg):
    await msg.reply_audio(audio=response.audio, mime_type="audio/ogg")


@WhatsApp.on_message(filters.text)
async def message_handler(_: WhatsApp, msg: types.Message):
    logger.info(f"MESSAGE USER: {msg}")
    await msg.indicate_typing()

    user_input = UserInput(
        message=msg.text,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )

    response_events = await farmwise.invoke(user_input)
    async for event in response_events:
        match event.response:
            case WhatsAppResponse():
                await _send_response(event.response, msg)
            case AudioResponse():
                await _send_audio_response(event.response, msg)
            case _:
                print("Unknown response type")

        if event.has_more:
            await msg.indicate_typing()


@WhatsApp.on_callback_selection
async def on_callback_selection(_: WhatsApp, sel: types.CallbackSelection):
    logger.info(f"CALLBACK SELECTION USER: {sel}")
    await sel.indicate_typing()

    user_input = UserInput(
        message=sel.data,
        user_id=sel.from_user.wa_id,
        user_name=sel.from_user.name,
    )

    response_events = await farmwise.invoke(user_input)
    async for event in response_events:
        match event.response:
            case WhatsAppResponse():
                await _send_response(event.response, sel)
            case AudioResponse():
                await _send_audio_response(event.response, sel)
            case _:
                print("Unknown response type")

        if event.has_more:
            await sel.indicate_typing()


@WhatsApp.on_callback_button
async def on_callback_button(_: WhatsApp, btn: types.CallbackButton):
    logger.info(f"CALLBACK BUTTON USER: {btn}")
    await btn.indicate_typing()

    user_input = UserInput(
        message=btn.data,
        user_id=btn.from_user.wa_id,
        user_name=btn.from_user.name,
    )

    response_events = await farmwise.invoke(user_input)
    async for event in response_events:
        match event.response:
            case WhatsAppResponse():
                await _send_response(event.response, btn)
            case AudioResponse():
                await _send_audio_response(event.response, btn)
            case _:
                print("Unknown response type")

        if event.has_more:
            await btn.indicate_typing()


@WhatsApp.on_message(filters.image)
async def image_handler(_: WhatsApp, msg: types.Message):
    await msg.indicate_typing()
    # download image to disk (saves file and returns the file path)
    file_path = await msg.image.download(os.path.join(settings.DOWNLOAD_DIR, "images"))
    logger.info(f"Image downloaded to {file_path}")
    url = file_path.replace(settings.DOWNLOAD_DIR, f"{settings.MEDIA_SERVER}")

    await msg.mark_as_read()

    user_input = UserInput(
        message=msg.caption,
        image=url,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )

    response_events = await farmwise.invoke(user_input)
    async for event in response_events:
        match event.response:
            case WhatsAppResponse():
                await _send_response(event.response, msg)
            case AudioResponse():
                await _send_audio_response(event.response, msg)
            case _:
                print("Unknown response type")

        if event.has_more:
            await msg.indicate_typing()


@WhatsApp.on_message(filters.voice)
async def voice_handler(_: WhatsApp, msg: types.Message):
    await msg.indicate_typing()
    # download voice note to disk (saves file and returns the file path)
    file_path = await msg.audio.download(os.path.join(settings.DOWNLOAD_DIR, "voice"))
    logger.info(f"Voice note downloaded to {file_path}")
    url = file_path.replace(settings.DOWNLOAD_DIR, f"{settings.MEDIA_SERVER}")

    await msg.mark_as_read()

    user_input = UserInput(
        voice=url,
        user_id=msg.from_user.wa_id,
        user_name=msg.from_user.name,
    )

    response = await farmwise.invoke_voice(user_input)
    logger.info(f"AGENT: {response}")

    await msg.reply_audio(audio=response.replace(settings.MEDIA_SERVER, f"{settings.DOWNLOAD_DIR}").strip('"'))


@WhatsApp.on_raw_update
async def raw_update_handler(_: WhatsApp, update: dict):
    logger.warning(f"RAW UPDATE: {update}")
