import numpy as np
from agents.voice import (
    AudioInput,
)
from pydub import AudioSegment


def _total_hack_for_filename(path):
    # DOWNLOAD_DIR=/Users/markns/Documents/farmwise_media
    # MEDIA_SERVER=

    return path.replace("http://localhost:8002", "/Users/markns/Documents/farmwise_media")


def load_oga_as_audio_input(input_path: str) -> AudioInput:
    # Load OGA/Opus file with pydub -
    # TODO: requires brew install ffmpeg
    input_path = _total_hack_for_filename(input_path)

    audio = AudioSegment.from_file(input_path, format="ogg")

    # Convert to 24000 Hz mono
    audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2)  # int16 = 2 bytes

    # Get raw audio data as numpy array
    samples = np.frombuffer(audio.raw_data, dtype=np.int16)

    return AudioInput(buffer=samples, frame_rate=24000, sample_width=2, channels=1)


async def write_stream_to_ogg(stream, output_path: str, sample_rate: int = 24000):
    """
    Write VoiceStreamEvent stream to an .ogg file.

    Args:
        stream: Async generator or iterator yielding VoiceStreamEvent with `chunk` or `buffer` of raw PCM data.
        output_path: Where to write the .ogg file.
        sample_rate: Sample rate of the audio (defaults to 24kHz).
    """
    pcm_data = bytearray()
    output_path = _total_hack_for_filename(output_path)
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
