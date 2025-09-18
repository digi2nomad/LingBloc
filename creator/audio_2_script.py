import google.generativeai as genai
from google.generativeai.genai.types import GenerateContentConfig, HttpOptions, Part

client = genai.Client(http_options=HttpOptions(api_version="v1"))
prompt = """
Transcribe the interview, in the format of timecode, speaker, caption.
Use speaker A, speaker B, etc. to identify speakers.
"""
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        prompt,
        Part.from_uri(
            file_uri="gs://cloud-samples-data/generative-ai/audio/pixel.mp3",
            mime_type="audio/mpeg",
        ),
    ],
    # Required to enable timestamp understanding for audio-only files
    config=GenerateContentConfig(audio_timestamp=True),
)
print(response.text)
# Example response:
# [00:00:00] **Speaker A:** your devices are getting better over time. And so ...
# [00:00:14] **Speaker B:** Welcome to the Made by Google podcast where we meet ...
# [00:00:20] **Speaker B:** Here's your host, Rasheed Finch.
# [00:00:23] **Speaker C:** Today we're talking to Aisha Sharif and DeCarlos Love. ...
# ...
