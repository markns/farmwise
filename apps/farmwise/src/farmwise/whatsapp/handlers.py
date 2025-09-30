import uuid

from loguru import logger
from pywa.types import FlowActionType, FlowButton
from pywa_async import WhatsApp, filters, types

from farmwise.context import get_or_create_user
from farmwise.schema import ActivityData, AudioResponse, CourseData, TextResponse, UserInput
from farmwise.service import farmwise
from farmwise.settings import settings
from farmwise.storage import make_blob_public, upload_bytes_to_gcs
from farmwise.whatsapp import commands
from farmwise.whatsapp.activities import activities_section_list
from farmwise.whatsapp.flows.courses.courses import get_courses_section_list
from farmwise.whatsapp.flows.edit_profile.handlers import launch_edit_profile_flow
from farmwise.whatsapp.responses import send_audio_reply, send_responses, send_text_reply
from farmwise.whatsapp.store import record_callback_selection


# TODO: Chat opened is not being triggered...
#  https://developers.facebook.com/docs/whatsapp/cloud-api/phone-numbers/conversational-components#welcome-messages
#  Welcome messages are currently not functioning as intended.
#  https://developers.facebook.com/community/threads/1842836979827258/?post_id=1842836983160591
@WhatsApp.on_chat_opened
async def chat_opened(client: WhatsApp, chat_opened: types.ChatOpened):
    logger.info(f"CHAT OPENED USER: {chat_opened}")
    # TODO: Do we already want to register a user here?
    await chat_opened.reply_text(f"""
Hi {chat_opened.from_user.name}! 👋 You're now connected to farmbetter – your trusted partner for smart farming advice.

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
    logger.info(f"{msg}")

    await msg.mark_as_read()
    context = await get_or_create_user(wa_id=msg.from_user.wa_id, name=msg.from_user.name)
    await msg.indicate_typing()

    user_input = UserInput(text=f"My location is {msg.location}")

    response_events = farmwise.invoke(context, user_input)
    await send_responses(response_events, msg)


@WhatsApp.on_message_status()
async def message_status_handler(_: WhatsApp, status: types.MessageStatus):
    logger.debug(f"Status: {status}")


cmds = [c.name for c in commands.commands]


@WhatsApp.on_message(filters.command(*cmds, prefixes="/", ignore_case=True), priority=1)
async def on_command(client: WhatsApp, msg: types.Message):
    logger.info(f"Command: {msg}")
    await msg.indicate_typing()

    match msg.text:
        case "/menu":
            await send_text_reply(
                TextResponse(content="Please choose an activity", section_list=activities_section_list), msg
            )
        case "/profile":
            await launch_edit_profile_flow(
                client,
                to=msg.from_user.wa_id,
                wa_user_name=msg.from_user.name,
            )
        case "/location":
            # TODO: add functionality to set location
            ...
        case "/courses":
            await send_text_reply(
                TextResponse(content="Please select a course", section_list=get_courses_section_list()), msg
            )


@WhatsApp.on_message(filters.text)
async def message_handler(_: WhatsApp, msg: types.Message):
    logger.info(f"Message: {msg}")

    await msg.mark_as_read()
    context = await get_or_create_user(wa_id=msg.from_user.wa_id, name=msg.from_user.name)

    # TODO: await record_inbound_message(user, msg)
    await msg.indicate_typing()

    user_input = UserInput(text=msg.text)

    response_events = farmwise.invoke(context, user_input)
    await send_responses(response_events, msg)


@WhatsApp.on_callback_selection(factory=ActivityData, priority=1)
async def on_activity_callback_selection(_: WhatsApp, sel: types.CallbackSelection[ActivityData]):
    logger.info(f"Activity: {sel.data}")
    await sel.indicate_typing()
    context = await get_or_create_user(wa_id=sel.from_user.wa_id, name=sel.from_user.name)
    await sel.indicate_typing()

    user_input = UserInput(text=sel.data.text)

    response_events = farmwise.invoke(context, user_input, agent_name=sel.data.agent)
    await send_responses(response_events, sel)


@WhatsApp.on_callback_selection(factory=CourseData, priority=1)
async def on_course_callback_selection(client: WhatsApp, sel: types.CallbackSelection[CourseData]):
    logger.info(f"Course: {sel.data}")

    course = sel.data
    await sel.reply_text(
        text=f"Tap the button to access the {course.title} course",
        buttons=FlowButton(
            title="Start course",
            flow_action_type=FlowActionType.NAVIGATE,
            flow_action_screen="LESSON_ONE",
            flow_name=course.name,
        ),
    )


@WhatsApp.on_callback_selection
async def on_callback_selection(_: WhatsApp, sel: types.CallbackSelection):
    logger.info(f"Callback: {sel}")
    await sel.mark_as_read()
    context = await get_or_create_user(wa_id=sel.from_user.wa_id, name=sel.from_user.name)
    user = context.user
    await record_callback_selection(user, sel)
    await sel.indicate_typing()

    user_input = UserInput(text=sel.data)

    response_events = farmwise.invoke(context, user_input)
    await send_responses(user, response_events, sel)


@WhatsApp.on_callback_button
async def on_callback_button(_: WhatsApp, btn: types.CallbackButton):
    logger.info(f"Button: {btn}")
    await btn.mark_as_read()
    context = await get_or_create_user(wa_id=btn.from_user.wa_id, name=btn.from_user.name)
    await btn.indicate_typing()

    user_input = UserInput(text=btn.data)

    response_events = farmwise.invoke(context, user_input)
    await send_responses(response_events, btn)


@WhatsApp.on_message(filters.image)
async def image_handler(_: WhatsApp, msg: types.Message):
    await msg.mark_as_read()
    context = await get_or_create_user(wa_id=msg.from_user.wa_id, name=msg.from_user.name)

    image_bytes = await msg.image.download(in_memory=True)
    await msg.indicate_typing()

    # Generate a unique blob name for GCS
    blob_name = f"images/{uuid.uuid4()}.jpg"
    bucket_name = settings.GCS_BUCKET.replace("gs://", "")

    # Upload to GCS
    upload_success = upload_bytes_to_gcs(
        data=image_bytes,
        bucket_name=bucket_name,
        blob_name=blob_name,
    )

    if upload_success:
        # TODO: Generate signed URL for the uploaded image
        # signed_url = generate_signed_url( bucket_name=bucket_name, blob_name=blob_name, )
        url = make_blob_public(bucket_name, blob_name)

    else:
        logger.error("Failed to upload image to GCS")
        await msg.reply_text("Sorry, there was an error processing your image.")
        return

    # await record_inbound_message(user, msg, storage={"blob": blob_name, "url": url})

    await msg.indicate_typing()
    user_input = UserInput(text=msg.caption, image=url)

    response_events = farmwise.invoke(context, user_input)
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


@WhatsApp.on_message(filters.voice)
async def voice_handler(_: WhatsApp, msg: types.Message):
    await msg.reply_text("Sorry voice notes are currently disabled")
    return
    #
    # await msg.indicate_typing()
    #
    # # Create a temporary local path for download
    # file_path = await msg.audio.download(in_memory=True)
    #
    # # Generate a unique blob name for GCS
    # blob_name = f"voice/{uuid.uuid4()}.ogg"
    # bucket_name = settings.GCS_BUCKET.replace("gs://", "")
    #
    # # Upload to GCS
    # upload_success = upload_bytes_to_gcs(
    #     data=file_path,
    #     bucket_name=bucket_name,
    #     blob_name=blob_name,
    # )
    #
    # if upload_success:
    #     # TODO: Generate signed URL for the uploaded voice note
    #     # signed_url = generate_signed_url( bucket_name=bucket_name, blob_name=blob_name, )
    #     url = make_blob_public(bucket_name, blob_name)
    #
    # else:
    #     logger.error("Failed to upload voice note to GCS")
    #     await msg.reply_text("Sorry, there was an error processing your voice message.")
    #     return
    #
    # await msg.mark_as_read()
    #
    # user_input = UserInput(
    #     voice=url,
    #     user_id=msg.from_user.wa_id,
    #     user_name=msg.from_user.name,
    # )
    #
    # response = await farmwise.invoke_voice(user_input)
    # logger.info(f"AGENT: {response}")
    #
    # # The response should now be a GCS signed URL or local file path
    # # For audio responses, we need to handle both cases
    # if response.startswith("http"):
    #     # It's already a URL, use it directly
    #     await msg.reply_audio(audio=response)
    # else:
    #     # It's a local file path, need to upload and get signed URL
    #     response_blob_name = f"responses/{uuid.uuid4()}.ogg"
    #     upload_success = upload_file_to_gcs(
    #         file_path=response.strip('"'),
    #         bucket_name=bucket_name,
    #         blob_name=response_blob_name,
    #         service_account_file=settings.GCS_SERVICE_ACCOUNT_FILE
    #     )
    #
    #     if upload_success:
    #         response_signed_url = generate_signed_url(
    #             bucket_name=bucket_name,
    #             blob_name=response_blob_name,
    #             service_account_file=settings.GCS_SERVICE_ACCOUNT_FILE
    #         )
    #         if response_signed_url:
    #             await msg.reply_audio(audio=response_signed_url)
    #         else:
    #             await msg.reply_text("Sorry, there was an error processing the audio response.")
    #     else:
    #         await msg.reply_text("Sorry, there was an error processing the audio response.")
    #
