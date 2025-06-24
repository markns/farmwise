import io
import json
import tempfile
from datetime import UTC, datetime
from typing import AsyncIterator

import requests
from agents import (
    Agent,
    AgentUpdatedStreamEvent,
    ItemHelpers,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    Runner,
    RunResultStreaming,
    gen_trace_id,
    trace,
)
from agents.voice import SingleAgentVoiceWorkflow, TTSModelSettings, VoicePipeline, VoicePipelineConfig
from farmbase_client.api.runresult import runresult_create_run_result as create_run_result
from farmbase_client.models import AgentBase, ChatState, RunResultCreate
from google.cloud import texttospeech
from google.cloud.texttospeech_v1 import SynthesizeSpeechResponse
from loguru import logger
from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputImageParam,
    ResponseInputTextParam,
    ResponseTextDeltaEvent,
)

from farmwise.agent import DEFAULT_AGENT, ONBOARDING_AGENT, agents
from farmwise.audio import load_oga_as_audio_input
from farmwise.dependencies import UserContext, chat_state, user_context
from farmwise.farmbase import FarmbaseClient
from farmwise.hooks import LoggingHooks
from farmwise.schema import AudioResponse, ResponseEvent, UserInput, WhatsAppResponse
from farmwise.settings import settings


async def text_to_speech(text) -> SynthesizeSpeechResponse:
    """
    Synthesizes speech from the input string of text with a
    South African English accent and saves it to a file.

    Args:
        text (str): The text to synthesize.
        output_filename (str): The name of the output audio file.
    """
    # Instantiates a client
    client = texttospeech.TextToSpeechAsyncClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-ZA" for
    # South African English) and the ssml voice gender ("NEUTRAL")
    # You can also specify a specific voice name. To get a list of available
    # voices, you can use client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-ZA",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        # Example of specifying a specific voice name:
        # name="en-ZA-Standard-A",
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        # Set the audio encoding to MP3
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = await client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    return response


async def _batch_stream_events(
    event_stream: AsyncIterator[RawResponsesStreamEvent | RunItemStreamEvent | AgentUpdatedStreamEvent],
) -> AsyncIterator[ResponseEvent]:
    accumulated = ""
    ready = ""
    start_token = '"content":"'
    end_token = '","actions":'
    message_ready_token = "\\n\\n"
    in_content = False

    async for event in event_stream:
        if event.type == RawResponsesStreamEvent.type and isinstance(event.data, ResponseTextDeltaEvent):
            delta = event.data.delta
            accumulated += delta

            if start_token in accumulated:
                in_content = True
                _, accumulated = accumulated.split(start_token)

            if in_content:
                if message_ready_token in accumulated:
                    ready, accumulated = accumulated.split(message_ready_token)
                    # use json.loads to unescape newlines etc.
                    yield ResponseEvent(response=WhatsAppResponse(content=json.loads(f'"{ready}"')))

            if end_token in accumulated:
                ready, accumulated = accumulated.split(end_token)
                in_content = False

        elif event.type == RunItemStreamEvent.type and event.name == "message_output_created":
            content = ItemHelpers.extract_last_content(event.item.raw_item)
            # TODO: content might be a ResponseOutputRefusal
            response = WhatsAppResponse.model_validate(json.loads(content))

            full_content = response.content
            response.content = ready
            yield ResponseEvent(response=response, has_more=True)

            logger.debug(f"Running text to speech for content: {full_content}")
            speech = await text_to_speech(full_content)
            yield ResponseEvent(
                response=AudioResponse(
                    audio=speech.audio_content,
                ),
                has_more=False,
            )


class FarmwiseService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

    def create_openai_file(self, file_url):
        # This is more useful than sending base64, as it means the base64 does not get
        # sent back and forth repeatedly

        response = requests.get(file_url)
        response.raise_for_status()

        # Determine a filename from the URL (or default to something)
        filename = file_url.split("/")[-1] or "upload.jpg"

        # Make sure the filename has a supported extension
        # if not any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
        #     raise ValueError(f"Unsupported file extension in: {filename}")

        file_like = io.BytesIO(response.content)
        file_like.name = filename  # This is critical — OpenAI expects a `.name` attribute

        logger.debug(f"Sending file {filename} from {file_url} to OpenAI")
        logger.debug(f"Sending file from {file_url} to OpenAI")
        result = self.openai_client.files.create(
            file=file_like,
            purpose="vision",
        )
        logger.debug(f"Created file {result}")
        return result.id

    async def run_agent(
        self,
        agent: Agent[UserContext],
        context: UserContext,
        user_input: UserInput,
        chat_state: ChatState,
    ) -> AsyncIterator[ResponseEvent]:
        input_items = chat_state.messages or []

        content = []
        if user_input.message:
            content.append(ResponseInputTextParam(text=user_input.message, type="input_text"))
        if user_input.image:
            # file_id = self.create_openai_file(user_input.image)
            content.extend(
                [
                    ResponseInputImageParam(detail="auto", image_url=user_input.image, type="input_image"),
                    ResponseInputTextParam(text=f"image_path={user_input.image}", type="input_text"),
                ]
            )

        input_items.append(
            EasyInputMessageParam(
                content=content,
                role="user",
            )
        )

        trace_id = gen_trace_id()
        hooks = LoggingHooks()
        with trace("FarmWise", trace_id=trace_id, group_id=user_input.user_id):
            result: RunResultStreaming = Runner.run_streamed(agent, input=input_items, context=context, hooks=hooks)
            async for event in _batch_stream_events(result.stream_events()):
                yield event

        async with FarmbaseClient() as client:
            await create_run_result.asyncio(
                client=client.raw,
                organization=context.contact.organization.slug,
                body=RunResultCreate(
                    contact_id=context.contact.id,
                    created_at=datetime.now(UTC),
                    input=result.input,
                    final_output=result.final_output,
                    input_guardrails=None,
                    output_guardrails=None,
                    last_agent=AgentBase(name=result.last_agent.name),
                    new_items=[],  # TODO: do we want to persist new_items and raw_responses?
                    raw_responses=[],
                    input_list=result.to_input_list(),
                    trace_id=trace_id,
                    # todo:
                    #  add tokens
                ),
            )

        logger.info(f"ASSISTANT: {result.final_output}")

    async def invoke(self, user_input: UserInput) -> AsyncIterator[ResponseEvent]:
        context = await user_context(user_input)
        chat_state_obj = await chat_state(context)

        if context.new_user:
            logger.info(f"NEW USER: {user_input.user_id}")
            agent = agents[ONBOARDING_AGENT]
        elif chat_state_obj.last_agent:
            agent = agents[chat_state_obj.last_agent.name]
        else:
            agent = agents[DEFAULT_AGENT]

        logger.info(f"USER: {user_input.message} AGENT: {agent.name} CONTEXT: {context}")
        return self.run_agent(agent, context, user_input, chat_state_obj)

    async def invoke_voice(self, user_input: UserInput) -> str:
        agent = agents[DEFAULT_AGENT]

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_f:
            temp_file_path = temp_f.name
            print(f"Created temporary file: {temp_file_path}")

            # Make a request to the URL, streaming the response
            print(f"Downloading from {user_input.voice}...")
            with requests.get(user_input.voice, stream=True) as r:
                # Check if the request was successful
                r.raise_for_status()

                # Write the content to the temporary file in chunks
                for chunk in r.iter_content(chunk_size=8192):
                    temp_f.write(chunk)

            audio_input = load_oga_as_audio_input(temp_file_path)

            pipeline = VoicePipeline(
                workflow=SingleAgentVoiceWorkflow(agent),
                config=VoicePipelineConfig(workflow_name="FarmWise", tts_settings=TTSModelSettings(voice="onyx")),
            )

            result = await pipeline.run(audio_input)

            # output_path = user_input.voice.replace(".oga", "_response.oga")
            # await write_stream_to_ogg(result.stream(), output_path)
            #
            # return output_path


farmwise = FarmwiseService()
