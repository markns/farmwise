import tempfile
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
from zep_cloud import Message

from farmwise.agent import DEFAULT_AGENT, agents
from farmwise.audio import load_oga_as_audio_input
from farmwise.context import UserContext
from farmwise.hooks import AgentHooks
from farmwise.memory.session import SessionState, clear_session_state, get_or_create_session, set_session_state
from farmwise.memory.zep import add_messages, get_memory
from farmwise.schema import ResponseEvent, TextResponse, UserInput
from farmwise.stream import _batch_stream_events


class FarmwiseService:
    @classmethod
    async def invoke(
        cls, context: UserContext, user_input: UserInput, agent_name: str = None
    ) -> AsyncIterator[ResponseEvent]:
        session_state = await get_or_create_session(context)

        memories = await get_memory(thread_id=session_state.thread_id)
        if memories:
            context.memories = memories

        user = context.user

        if agent_name:
            agent = agents[agent_name]
        # TODO: how to handle onboarding with FarmBetter?
        # elif context.new_user:
        #     agent = agents[ONBOARDING_AGENT]
        else:
            agent = agents[session_state.current_agent]

        content = []
        if user_input.text:
            content.append(ResponseInputTextParam(text=user_input.text, type="input_text"))
        if user_input.image:
            content.append(
                ResponseInputImageParam(detail="auto", image_url=user_input.image, type="input_image"),
            )

        input_items = [EasyInputMessageParam(content=content, role="user")]

        hooks = AgentHooks()
        trace_id = gen_trace_id()

        logger.info(f"Agent starting https://platform.openai.com/traces/trace?trace_id={trace_id}")
        try:
            with trace(
                "FarmWise",
                trace_id=trace_id,
                group_id=user.wa_id,
                metadata={"full_name": user.full_name},
            ):
                result: RunResultStreaming = Runner.run_streamed(
                    agent,
                    input=input_items,
                    context=context,
                    hooks=hooks,
                    previous_response_id=session_state.previous_response_id,
                )

                # TODO: tts = user.config.text_to_speech
                tts = False
                async for event in _batch_stream_events(result.stream_events(), tts=tts):
                    yield event

            await set_session_state(
                context,
                SessionState(
                    current_agent=result.last_agent.name,
                    thread_id=session_state.thread_id,
                    previous_response_id=result.last_response_id,
                ),
            )

            if user_input.text:
                text_response: TextResponse = result.final_output_as(TextResponse)

                await add_messages(
                    session_state.thread_id,
                    messages=[
                        Message(name=user.full_name, role="user", content=user_input.text),
                        Message(name=result.last_agent.name, role="assistant", content=text_response.content),
                    ],
                )

        except openai.APIError as e:
            logger.exception("An OpenAI error has occurred")
            yield ResponseEvent(
                response=TextResponse(
                    content=f"Sorry, there has been a problem. Please try again.\n\nDetail: {e.message}"
                ),
                has_more=False,
            )
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
