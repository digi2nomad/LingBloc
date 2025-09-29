import os,sys

from google import genai
from google.genai import types

def gen_audio(genai_client, text_content, output_audio_file):
    response = genai_client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=text_content,
    config=types.GenerateContentConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
         multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
               types.SpeakerVoiceConfig(
                  speaker='A',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                     )
                  )
               ),
               types.SpeakerVoiceConfig(
                  speaker='B',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Puck',
                        )
                        )
                     ),
                  ]
               )
            )
         )
    )
    if not response.audio:
        raise Exception("Failed to generate audio")

    with open(output_audio_file, 'wb') as f:
        f.write(response.audio)

def get_genai_client(genai_api_key):
    try:
        return genai.Client(api_key=genai_api_key)
    except Exception as e:
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: <input_text_file> <output_audio_file>")
        sys.exit(1)
    api_key = os.environ['GOOGLE_API_KEY']
    client = get_genai_client(api_key)
    gen_audio(open(sys.argv[1], 'r').read(), sys.argv[2])
