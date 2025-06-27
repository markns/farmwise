import json
import tempfile
from datetime import datetime, UTC
from typing import AsyncIterator

import requests
from agents import (
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
from google.cloud import texttospeech
from google.cloud.texttospeech_v1 import SynthesizeSpeechResponse
from loguru import logger
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputImageParam,
    ResponseInputTextParam,
    ResponseTextDeltaEvent, )

from farmbase_client.api.contacts import contacts_create_run_result
from farmbase_client.models import RunResultCreate, AgentCreate
from farmwise.agent import DEFAULT_AGENT, ONBOARDING_AGENT, agents
from farmwise.audio import load_oga_as_audio_input
from farmwise.context import user_context
from farmwise.memory.session import get_session_state, set_session_state
from farmwise.farmbase import FarmbaseClient
from farmwise.hooks import AgentHooks
from farmwise.openai.enums import RunItemStreamEventName
from farmwise.schema import AudioResponse, ResponseEvent, UserInput, TextResponse, SessionState


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
        # logger.debug(event)
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
                    yield ResponseEvent(response=TextResponse(content=json.loads(f'"{ready}"')))

            if end_token in accumulated:
                ready, accumulated = accumulated.split(end_token)
                in_content = False

        elif event.type == RunItemStreamEvent.type and event.name == RunItemStreamEventName.MESSAGE_OUTPUT_CREATED:
            content = ItemHelpers.extract_last_content(event.item.raw_item)
            # TODO: content might be a ResponseOutputRefusal
            response = TextResponse.model_validate(json.loads(content))

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

    @classmethod
    async def invoke(cls, user_input: UserInput) -> AsyncIterator[ResponseEvent]:
        context = await user_context(user_input)
        session_state = await get_session_state(context)

        if context.new_user:
            agent = agents[ONBOARDING_AGENT]
        elif session_state:
            agent = agents.get(session_state.last_agent, DEFAULT_AGENT)
        else:
            agent = agents[DEFAULT_AGENT]

        content = []
        if user_input.message:
            content.append(ResponseInputTextParam(text=user_input.message, type="input_text"))
        if user_input.image:
            content.extend(
                [
                    ResponseInputImageParam(detail="auto", image_url=user_input.image, type="input_image"),
                    ResponseInputTextParam(text=f"image_path={user_input.image}", type="input_text"),
                ]
            )

        input_items = [
            EasyInputMessageParam(
                content=content,
                role="user",
            )
        ]

        previous_response_id = session_state.previous_response_id if session_state else None
        hooks = AgentHooks()
        trace_id = gen_trace_id()

        with trace("FarmWise", trace_id=trace_id, group_id=user_input.user_id):
            result: RunResultStreaming = Runner.run_streamed(agent, input=input_items, context=context, hooks=hooks,
                                                             previous_response_id=previous_response_id)

            async for event in _batch_stream_events(result.stream_events()):
                yield event

        await set_session_state(context, SessionState(last_agent=result.last_agent.name,
                                                      previous_response_id=result.last_response_id))

        usage = result.context_wrapper.usage
        async with FarmbaseClient() as client:
            await contacts_create_run_result.asyncio(
                client=client.raw,
                organization=context.contact.organization.slug,
                contact_id=context.contact.id,
                body=RunResultCreate(
                    created_at=datetime.now(UTC),
                    contact_id=context.contact.id,
                    input=user_input.message,
                    final_output=result.final_output,
                    last_agent=AgentCreate(name=result.last_agent.name),
                    trace_id=trace_id,
                    requests=usage.requests,
                    input_tokens=usage.input_tokens,
                    input_tokens_cached=usage.input_tokens_details.cached_tokens,
                    output_tokens=usage.output_tokens,
                    output_tokens_reasoning=usage.output_tokens_details.reasoning_tokens,
                    total_tokens=usage.total_tokens,
                ),
            )


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
