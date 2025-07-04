from google.cloud import texttospeech
from google.cloud.texttospeech_v1 import SynthesizeSpeechResponse


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
