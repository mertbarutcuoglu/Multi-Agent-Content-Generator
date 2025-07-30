from openai import AzureOpenAI
from openai._types import FileTypes
import os

client = AzureOpenAI(
    azure_deployment="whisper",
    api_version="2024-06-01",
    azure_endpoint=os.environ["AZURE_OPENAI_WHISPER_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_WHISPER_API_KEY"],
)


def transcribe_with_api(audio_file: FileTypes, prompt: str | None = None):
    """
    Transcribe an audio file using the OpenAI Whisper API
    """

    transcript = client.audio.transcriptions.create(
        model="whisper",
        file=open(audio_file, "rb"),
        response_format="verbose_json",
        timestamp_granularities=["segment", "word"],
        prompt=prompt,
    )

    # Add space to beginning of words
    # to match local Whisper format
    for transcription_word in transcript.words:
        transcription_word.word = " " + transcription_word.word

    # Return response in same format
    # as local Whisper format
    return [
        {
            "start": transcript.segments[0].start,
            "end": transcript.segments[-1].end,
            "words": transcript.words,
        }
    ]
