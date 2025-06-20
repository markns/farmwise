import numpy as np
import tempfile
import uuid
from typing import Optional

from agents.voice import (
    AudioInput,
)
from loguru import logger
from pydub import AudioSegment

from farmwise.settings import settings
from farmwise.storage import generate_signed_url, upload_file_to_gcs


def _download_from_gcs_if_needed(path: str) -> str:
    """Download file from GCS if it's a signed URL, otherwise return the path as-is."""
    if path.startswith("http"):
        # It's a signed URL, we need to download it to a temporary file
        # For now, we'll assume it's already accessible and return the path
        # In a production system, you might want to download it to a temp file
        return path
    else:
        # It's already a local path
        return path


def load_oga_as_audio_input(input_path: str) -> AudioInput:
    """Load OGA/Opus file as AudioInput.
    
    Args:
        input_path: Path to the audio file or GCS signed URL
        
    Returns:
        AudioInput object with the audio data
    """
    # Handle both local paths and GCS URLs
    processed_path = _download_from_gcs_if_needed(input_path)
    
    try:
        # Load OGA/Opus file with pydub - requires ffmpeg
        audio = AudioSegment.from_file(processed_path, format="ogg")

        # Convert to 24000 Hz mono
        audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2)  # int16 = 2 bytes

        # Get raw audio data as numpy array
        samples = np.frombuffer(audio.raw_data, dtype=np.int16)

        return AudioInput(buffer=samples, frame_rate=24000, sample_width=2, channels=1)
    except Exception as e:
        logger.error(f"Error loading audio file {input_path}: {e}")
        raise


async def write_stream_to_ogg(stream, output_path: Optional[str] = None, sample_rate: int = 24000, upload_to_gcs: bool = True) -> str:
    """
    Write VoiceStreamEvent stream to an .ogg file and optionally upload to GCS.

    Args:
        stream: Async generator or iterator yielding VoiceStreamEvent with `chunk` or `buffer` of raw PCM data.
        output_path: Local path to write the .ogg file. If None, uses a temporary file.
        sample_rate: Sample rate of the audio (defaults to 24kHz).
        upload_to_gcs: Whether to upload the file to GCS and return a signed URL.
        
    Returns:
        str: Path to the local file, or GCS signed URL if upload_to_gcs is True.
    """
    pcm_data = bytearray()
    # output_path = _total_hack_for_filename(output_path)
    # Accumulate all raw audio chunks
    async for event in stream:
        if event.type == "voice_stream_event_audio":
            pcm_data += event.data.astype(np.int16).tobytes()

    # Convert to AudioSegment and export
    audio_segment = AudioSegment(
        data=bytes(pcm_data),
        sample_width=2,  # 16-bit PCM
        frame_rate=sample_rate,
        channels=1,  # Mono
    )
    audio_segment.export(output_path, format="ogg", codec="libopus")
