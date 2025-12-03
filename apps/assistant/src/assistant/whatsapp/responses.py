import uuid

from loguru import logger
from pywa_async.types import Button
from pywa_async.types.base_update import BaseUserUpdateAsync

from assistant.schema import Action, AudioResponse, SectionList, TextResponse
from assistant.whatsapp.activities import activities_section_list
from assistant.whatsapp.flows.flow_tokens import FlowSession, store_flow_session
from assistant.whatsapp.utils import _convert_md_to_whatsapp


def ensure_valid_section_list(section_list: SectionList):
    return section_list


def ensure_valid_buttons(buttons: list[Button]):
    if len(buttons) > 3:
        logger.warning(f"Invalid buttons count. Min allowed buttons: 1, Max allowed buttons: 3': {buttons}")
        return buttons[:3]
    return buttons


async def send_text_reply(response: TextResponse, msg: BaseUserUpdateAsync):
    """Send a WhatsApp response using the appropriate message type based on response content."""

    text = _convert_md_to_whatsapp(response.content)

    if Action.request_location in response.actions:
        await msg.reply_location_request(response.content)
    elif response.section_list:
        section_list = ensure_valid_section_list(response.section_list)
        await msg.reply_text(text=text, buttons=section_list)
    elif response.flow_button:
        flow_button = response.flow_button
        flow_token = uuid.uuid4().hex
        await store_flow_session(flow_token, FlowSession(wa_id=msg.from_user.wa_id, name=msg.from_user.name))
        flow_button.flow_token = flow_token

        await msg.reply_text(text=text, buttons=flow_button)
    elif response.buttons:
        buttons = ensure_valid_buttons(response.buttons)
        await msg.reply_text(text=text, buttons=buttons)
    else:
        if response.agent_complete:
            section_list = ensure_valid_section_list(activities_section_list)
        else:
            section_list = None
        await msg.reply_text(text=text, buttons=section_list)

    # TODO: await record_outbound_message(user, sent_message, text)


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
    # # Priority 3: user sharing
    # if response.user:
    #     user = _convert_to_pywa_user(response.user)
    #     await msg.reply_user(user=user)
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


async def send_responses(response_events, msg):
    async for event in response_events:
        match event.response:
            case TextResponse():
                await send_text_reply(event.response, msg)
            case AudioResponse():
                await send_audio_reply(event.response, msg)
            case _:
                logger.error(f"Unknown response type: {event.response}")

        if event.has_more:
            await msg.indicate_typing()
