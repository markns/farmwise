import tempfile
from datetime import UTC, datetime
from typing import AsyncIterator

import openai
import requests
from agents import (
    Runner,
    RunResultStreaming,
    gen_trace_id,
    trace,
)
from agents.voice import SingleAgentVoiceWorkflow, TTSModelSettings, VoicePipeline, VoicePipelineConfig
from loguru import logger
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputImageParam,
    ResponseInputTextParam,
)

from farmbase_client.api.contacts import contacts_create_run_result
from farmbase_client.models import AgentCreate, Message, RunResultCreate
from farmwise.agent import DEFAULT_AGENT, ONBOARDING_AGENT, agents
from farmwise.audio import load_oga_as_audio_input
from farmwise.context import UserContext
from farmwise.farmbase import farmbase_api_client
from farmwise.hooks import AgentHooks
from farmwise.memory.memory import add_memory
from farmwise.memory.session import get_session_state, set_session_state, clear_session_state
from farmwise.schema import ResponseEvent, SessionState, TextResponse, UserInput
from farmwise.stream import _batch_stream_events


class FarmwiseService:
    @classmethod
    async def invoke(cls,
                     context: UserContext,
                     user_input: UserInput,
                     agent_name: str = None) -> AsyncIterator[ResponseEvent]:

        session_state = await get_session_state(context)

        if agent_name:
            agent = agents[agent_name]
        elif context.new_user:
            agent = agents[ONBOARDING_AGENT]
        elif session_state:
            agent = agents.get(session_state.last_agent, DEFAULT_AGENT)
        else:
            agent = agents[DEFAULT_AGENT]

        content = []
        if user_input.text:
            content.append(ResponseInputTextParam(text=user_input.text, type="input_text"))
        if user_input.image:
            content.extend(
                [
                    ResponseInputImageParam(detail="auto", image_url=user_input.image, type="input_image"),
                    # TODO: is this still necessary?
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
        contact = context.contact

        logger.debug(f"Agent starting https://platform.openai.com/traces/trace?trace_id={trace_id}")
        try:
            with trace(
                    "FarmWise",
                    trace_id=trace_id,
                    group_id=contact.phone_number,
                    metadata={"username": contact.name, "organization": contact.organization.slug},
            ):
                result: RunResultStreaming = Runner.run_streamed(
                    agent, input=input_items, context=context, hooks=hooks, previous_response_id=previous_response_id
                )

                # TODO: tts = contact.config.text_to_speech
                tts = False
                async for event in _batch_stream_events(result.stream_events(), tts=tts):
                    yield event

            await set_session_state(
                context, SessionState(last_agent=result.last_agent.name, previous_response_id=result.last_response_id)
            )

            if user_input.text:
                text_response: TextResponse = result.final_output_as(TextResponse)
                await add_memory(
                    contact,
                    messages=[
                        Message(role="user", content=user_input.text),
                        Message(role="assistant", content=text_response.content),
                    ],
                )

            usage = result.context_wrapper.usage
            await contacts_create_run_result.asyncio(
                client=farmbase_api_client,
                organization=contact.organization.slug,
                contact_id=contact.id,
                body=RunResultCreate(
                    created_at=datetime.now(UTC),
                    contact_id=contact.id,
                    input=user_input.text,
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

        except openai.APIError as e:
            logger.exception("An OpenAI error has occurred")
            yield ResponseEvent(response=TextResponse(
                content=f"Sorry, there has been a problem. Please try again.\n\nDetail: {e.message}"),
                                has_more=False)
            await clear_session_state(context)

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
