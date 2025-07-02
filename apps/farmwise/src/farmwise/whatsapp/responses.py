from farmbase_client.models import ContactRead
from loguru import logger
from pywa.types import Button, Section, SectionList, SectionRow
from pywa_async.types.base_update import BaseUserUpdateAsync

from farmwise.schema import Action, AudioResponse, TextResponse
from farmwise.schema import SectionList as FarmwiseSectionList
from farmwise.whatsapp.store import record_outbound_message
from farmwise.whatsapp.utils import _convert_md_to_whatsapp


async def _send_text_response(contact: ContactRead, response: TextResponse, msg: BaseUserUpdateAsync):
    """Send a WhatsApp response using the appropriate message type based on response content."""

    # Prepare interactive elements that can be used with various message types
    buttons = None
    section_list = None

    if response.section_list:
        section_list = _convert_to_pywa_section_list(response.section_list)
    elif response.buttons:
        if len(response.buttons) > 3:
            logger.warning(f"Max allowed buttons: 3. {response}")
        buttons = [Button(b.title[:20], b.callback_data) for b in response.buttons[:3]]

    text = _convert_md_to_whatsapp(response.content)

    if Action.request_location in response.actions:
        sent_message = await msg.reply_location_request(response.content)
    elif section_list or buttons:
        sent_message = await msg.reply_text(text=text, buttons=section_list or buttons)
    else:
        sent_message = await msg.reply_text(text)

    await record_outbound_message(contact, sent_message, text)


async def _send_audio_response(response: AudioResponse, msg):
    await msg.reply_audio(audio=response.audio, mime_type="audio/ogg")


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
