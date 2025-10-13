import os,sys
import wave

from google import genai
from google.genai import types

from util import srt_utils, audio_file_merge


def gen_audio(genai_client,
              text_content,
              output_audio_file,
              speaker1,
              speaker2,
              speed=1.0):
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
                        voice_name=speaker1,
                     )
                  )
               ),
               types.SpeakerVoiceConfig(
                  speaker='B',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=speaker2,
                        )
                        )
                     ),
                  ]
               )
            )
         )
    )
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    if not audio_data:
        raise Exception("Failed to generate audio")

    wave_file(output_audio_file, audio_data, speed)

def wave_file(filename, pcm, speed=1.0, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(int(rate*speed))
      wf.writeframes(pcm)

def get_genai_client(genai_api_key):
    try:
        return genai.Client(api_key=genai_api_key)
    except Exception as e:
        return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: <input_script_file> <output_audio_file> <workfolder> <speaker1> <speaker2> <speed>")
        print(f"Example: python script_2_audio.py clips/script.txt clips/audio.wav clips speaker1 speaker2 1.0")
        print(f"Note: The order of the voices in the list should match the order of the speakers: ")
        print(f"Zephyr -- Bright 	Puck -- Upbeat 	Charon -- Informative")
        print(f"Kore -- Firm 	Fenrir -- Excitable 	Leda -- Youthful")
        print(f"Orus -- Firm 	Aoede -- Breezy 	Callirrhoe -- Easy-going")
        print(f"Autonoe -- Bright 	Enceladus -- Breathy 	Iapetus -- Clear")
        print(f"Umbriel -- Easy-going 	Algieba -- Smooth 	Despina -- Smooth")
        print(f"Erinome -- Clear 	Algenib -- Gravelly 	Rasalgethi -- Informative")
        print(f"Laomedeia -- Upbeat 	Achernar -- Soft 	Alnilam -- Firm")
        print(f"Schedar -- Even 	Gacrux -- Mature 	Pulcherrima -- Forward")
        print(f"Achird -- Friendly 	Zubenelgenubi -- Casual 	Vindemiatrix -- Gentle")
        print(f"Sadachbia -- Lively 	Sadaltager -- Knowledgeable 	Sulafat -- Warm")
        sys.exit(1)

    api_key = os.environ['GOOGLE_API_KEY']
    client = get_genai_client(api_key)
    spk1 = "Charon"
    spk2 = "Despina"
    spd = 1.0

    srt_file = sys.argv[1]
    output_audio_file = sys.argv[2]
    work_folder = sys.argv[3]
    if len(sys.argv) > 6:
        spk1 = sys.argv[4] #speaker1
        spk2 = sys.argv[5] #speaker2
    if len(sys.argv) > 7:
        spd = float(sys.argv[6]) #speed

    subtitles_chunks = srt_utils.divide_subtitles(srt_file)
    audio_chunk_files = []
    for i, chunk in enumerate(subtitles_chunks):
        audio_chunk_file = work_folder + "/audio_chunk_" + str(i) + ".wav"
        audio_chunk_files.append(audio_chunk_file)
        gen_audio(client, chunk, audio_chunk_file, spk1, spk2, spd)
    audio_file_merge.merge_audio(audio_chunk_files, output_audio_file)
