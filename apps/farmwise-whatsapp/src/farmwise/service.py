import tempfile
from typing import AsyncIterator

import google.generativeai as genai
import requests
from loguru import logger
from zep_cloud import Message

from farmwise.agent import DEFAULT_AGENT, ONBOARDING_AGENT, get_agents
from farmwise.audio import load_oga_as_audio_input
from farmwise.context import UserContext
from farmwise.memory.session import SessionState, clear_session_state, get_or_create_session, set_session_state
from farmwise.memory.zep import add_messages, get_memory
from farmwise.schema import ResponseEvent, TextResponse, UserInput
from farmwise.stream import _batch_stream_events
from farmwise.utils import to_adk_content


class FarmwiseService:
    @classmethod
    async def invoke(
        cls, context: UserContext, user_input: UserInput, agent_name: str = None
    ) -> AsyncIterator[ResponseEvent]:
        session_state = await get_or_create_session(context)
        
        # Retrieve agents from the factory/registry
        # In a real request-scoped scenario, we might want to create a fresh hierarchy here
        # But for now, we use the global singleton or factory return
        agents = get_agents()

        memories = await get_memory(thread_id=session_state.thread_id)
        if memories:
            context.memories = memories
            # Convert Zep messages to ADK/Gemini history format
            context.history = [
                genai.types.Content(role="user" if m.role == "user" else "model", parts=[genai.types.Part.from_text(m.content)])
                for m in memories
            ]
            context.thread_id = session_state.thread_id

        user = context.user

        if agent_name:
            agent = agents[agent_name]
        elif context.new_user:
            agent = agents[ONBOARDING_AGENT]
        else:
            agent = agents[session_state.current_agent]

        # Convert UserInput to ADK-compatible content
        adk_content_parts = to_adk_content(user_input)

        try:
            # Initialize the generative model with the selected agent's tools
            model = genai.GenerativeModel(
                model_name=agent.model,
                tools=agent.tools,
                system_instruction=agent.instruction,
            )

            # Start a chat session with the model
            # Pass existing history from memory
            chat_session = model.start_chat(history=context.history)

            # Send the message and get the streaming response
            # Note: ADK's `ToolContext` is usually managed implicitly when running agents
            # directly via `adk.agents.Agent.run()`. Here, we're using `generativeai.GenerativeModel`
            # directly for streaming, so `ToolContext` will need to be managed by the tools themselves
            # or populated before tool execution. For now, assuming tools access `UserContext`
            # directly or through global state if not passed explicitly here.
            stream_result = await chat_session.send_message_async(adk_content_parts, stream=True)

            async for event in _batch_stream_events(stream_result, tts=False): # tts is hardcoded to False for now
                yield event

            # After the stream, get the final accumulated content if needed for memory update
            final_response_content = ""
            # This part needs adjustment based on how _batch_stream_events accumulates final content
            # For now, let's assume the last event from _batch_stream_events contains the full response
            # A more robust solution would be to modify _batch_stream_events to return the final content
            # or iterate through the stream_result again to get the final text.
            # For simplicity, we'll extract it from chat_session.history[-1] after send_message completes
            if chat_session.history and chat_session.history[-1].role == "model":
                final_response_content = chat_session.history[-1].parts[0].text


            await set_session_state(
                context,
                SessionState(
                    current_agent=agent.name,
                    thread_id=session_state.thread_id,
                    previous_response_id=None,
                ),
            )

            # We only update the memory if we have a text input and a final response
            if user_input.text and final_response_content:
                await add_messages(
                    session_state.thread_id,
                    messages=[
                        Message(name=user.full_name, role="user", content=user_input.text),
                        Message(name=agent.name, role="assistant", content=final_response_content),
                    ],
                )

        except Exception as e:
            logger.exception("An error has occurred during agent invocation")
            yield ResponseEvent(
                response=TextResponse(
                    content=f"Sorry, there has been a problem. Please try again.\n\nDetail: {str(e)}"
                ),
                has_more=False,
            )
            await clear_session_state(context)

    # invoke_voice method removed as part of migration


farmwise = FarmwiseService()
