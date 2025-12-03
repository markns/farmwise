from typing import AsyncIterator

from loguru import logger
from google.genai.types import GenerateContentResponse

from farmwise.schema import ResponseEvent, TextResponse, AudioResponse
from farmwise.voice import text_to_speech


async def _batch_stream_events(event_stream: AsyncIterator[GenerateContentResponse],
                               tts: bool = False
                               ) -> AsyncIterator[ResponseEvent]:
    accumulated_content = ""
    # Assuming text-only responses from GenerateContentResponse for simplicity for now
    # More complex multimodal responses or tool calls would require additional parsing

    async for chunk in event_stream:
        if chunk.candidates:
            for part in chunk.candidates[0].content.parts:
                if part.text:
                    accumulated_content += part.text
                    yield ResponseEvent(response=TextResponse(content=accumulated_content), has_more=True)

    # After the stream is complete, if TTS is enabled, process the full accumulated content
    if tts and accumulated_content:
        logger.debug(f"Running text to speech for content: {accumulated_content}")
        speech = await text_to_speech(accumulated_content)
        yield ResponseEvent(
            response=AudioResponse(
                audio=speech.audio_content,
            ),
            has_more=False,
        )
    else:
        yield ResponseEvent(response=TextResponse(content=accumulated_content), has_more=False)
