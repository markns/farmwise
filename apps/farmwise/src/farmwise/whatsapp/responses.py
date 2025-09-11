from farmbase_client.models import ContactRead
from loguru import logger
from pywa_async.types.base_update import BaseUserUpdateAsync

from farmwise.schema import Action, AudioResponse, Button, SectionList, TextResponse
from farmwise.whatsapp.activities import activities
from farmwise.whatsapp.store import record_outbound_message
from farmwise.whatsapp.utils import _convert_md_to_whatsapp


def ensure_valid_section_list(section_list: SectionList):
    print(section_list)
    return section_list


def ensure_valid_buttons(buttons: list[Button]):
    print(buttons)
    return buttons


async def send_text_reply(contact: ContactRead, response: TextResponse, msg: BaseUserUpdateAsync):
    """Send a WhatsApp response using the appropriate message type based on response content."""

    text = _convert_md_to_whatsapp(response.content)

    if Action.request_location in response.actions:
        sent_message = await msg.reply_location_request(response.content)
    elif response.section_list:
        section_list = ensure_valid_section_list(response.section_list)
        sent_message = await msg.reply_text(text=text, buttons=section_list)
    elif response.buttons:
        buttons = ensure_valid_buttons(response.buttons)
        sent_message = await msg.reply_text(text=text, buttons=buttons)
    else:
        if response.agent_complete:
            section_list = ensure_valid_section_list(activities)
        else:
            section_list = None
        sent_message = await msg.reply_text(text=text, buttons=section_list)

    await record_outbound_message(contact, sent_message, text)


async def send_audio_reply(response: AudioResponse, msg):
    await msg.reply_audio(audio=response.audio, mime_type="audio/ogg")

    # Priority 2: Media messages (can include buttons/section_lists)
    # if response.image_url:
    #     await msg.reply_image(
    #         image=response.image_url,
    #         caption=response.content,
    #         buttons=section_list or buttons,
    #     )
    #     return
    #
    # # Priority 3: Contact sharing
    # if response.contact:
    #     contact = _convert_to_pywa_contact(response.contact)
    #     await msg.reply_contact(contact=contact)
    #     # If there are buttons/section_lists, send them in a follow-up text message
    #     if section_list or buttons:
    #         await msg.reply_text(
    #             text=_convert_md_to_whatsapp(response.content) if response.content else "Choose an option:",
    #             buttons=section_list or buttons,
    #         )
    #     return
    #
    # # Priority 4: Product sharing
    # if response.product:
    #     await msg.reply_product(
    #         catalog_id=response.product.catalog_id,
    #         sku=response.product.sku,
    #         body=response.product.body,
    #         footer=response.product.footer,
    #     )
    #     # If there are buttons/section_lists, send them in a follow-up text message
    #     if section_list or buttons:
    #         await msg.reply_text(
    #             text=_convert_md_to_whatsapp(response.content) if response.content else "Choose an option:",
    #             buttons=section_list or buttons,
    #         )
    #     return


async def send_responses(contact, response_events, msg):
    async for event in response_events:
        match event.response:
            case TextResponse():
                await send_text_reply(contact, event.response, msg)
            case AudioResponse():
                await send_audio_reply(event.response, msg)
            case _:
                logger.error(f"Unknown response type: {event.response}")

        if event.has_more:
            await msg.indicate_typing()
