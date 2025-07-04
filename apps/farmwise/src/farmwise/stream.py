import json
from enum import Enum
from typing import AsyncIterator

from agents import RawResponsesStreamEvent, RunItemStreamEvent, AgentUpdatedStreamEvent, ItemHelpers
from loguru import logger
from openai.types.responses import ResponseTextDeltaEvent

from farmwise.schema import ResponseEvent, TextResponse, AudioResponse
from farmwise.service import text_to_speech


class RunItemStreamEventName(str, Enum):
    MESSAGE_OUTPUT_CREATED = "message_output_created"
    HANDOFF_REQUESTED = "handoff_requested"
    HANDOFF_OCCURED = "handoff_occured"  # noqa - typo in source
    TOOL_CALLED = "tool_called"
    TOOL_OUTPUT = "tool_output"
    REASONING_ITEM_CREATED = "reasoning_item_created"
    MCP_APPROVAL_REQUESTED = "mcp_approval_requested"
    MCP_LIST_TOOLS = "mcp_list_tools"


async def _batch_stream_events(event_stream: AsyncIterator[
    RawResponsesStreamEvent | RunItemStreamEvent | AgentUpdatedStreamEvent],
                               tts: bool
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
            yield ResponseEvent(response=response, has_more=tts)

            if tts:
                logger.debug(f"Running text to speech for content: {full_content}")
                speech = await text_to_speech(full_content)
                yield ResponseEvent(
                    response=AudioResponse(
                        audio=speech.audio_content,
                    ),
                    has_more=False,
                )
