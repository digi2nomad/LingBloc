from google import genai
from google.genai import types
import os,random,time,audio_file_split

def test(client,model_name):
    response = client.models.generate_content(
        model=model_name,
        contents="Explain how Gemini makes youtube video",
    )
    print(response.text)

def list_uploaded_files(client):
    files = client.files.list()
    for file in files:
        print(" ", file.name)

def get_uploaded_file(client, filename):
    file = client.files.get(name=filename)
    print(" ", file.name)

def delete_uploaded_file(client, filename):
    client.files.delete(name=filename)
    print(" ", filename, "deleted")

def transcribe(client,
               model_name,
               uploaded_file):
    max_retries = 3
    initial_delay = 1
    response = None
    prompt = f"""
        You are a transcription service for video caption, please transcribe 
        the audio file into  SRT (SubRip) file format, with accurate timestamps. 
        Each sentence should be concise and clear and each sentence should not 
        be too long in order to fit into one line of a screen.
        """
    print(f"  transcribing {uploaded_file.name} with prompt:\n {prompt.strip()}")
    for attempt in range(max_retries): # try max_retries times
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    uploaded_file
                ],
                # Required to enable timestamp understanding for audio-only files
                config=types.GenerateContentConfig(
                    temperature=0,
                    top_p=1,
                    top_k=32,
                    max_output_tokens=None),
            )
            last_exception = None # success
            break 
        except Exception as e:
            last_exception = e
            print(f"  transcribe failed (try {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                delay = (initial_delay * (2 ** attempt)) + random.uniform(0, 1)
                print(f"  will {delay:.2f} seconds, then try again..")
                time.sleep(delay)
            else:
                print(f"  have tried maximum times，give up: {uploaded_file.name}")
    print(f"  transcribed: {uploaded_file.name}")
    return response.text+"\n\n"

def upload_file(client, audio_file):
    max_retries = 3
    initial_delay = 1
    uploaded_file = None
    last_exception = None # keep the last exception
    for attempt in range(max_retries): # try max_tries times
        try:
            print(f"  uploading (try {attempt + 1}/{max_retries}): {audio_file}")
            uploaded_file = client.files.upload(file=audio_file)
            print(f"  uploaded: {audio_file} -> {uploaded_file.name}")
            last_exception = None # success
            break 
        except Exception as e:
            last_exception = e
            print(f"  uploading failed (try {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                delay = (initial_delay * (2 ** attempt)) + random.uniform(0, 1)
                print(f"  will {delay:.2f} seconds, then try again..")
                time.sleep(delay)
            else:
                print(f"  have tried maximum times，give up: {audio_file}")
    if uploaded_file:
        while uploaded_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(10) # Wait for 10 seconds before checking again
            uploaded_file = client.files.get(audio_file) # Refresh the file object

    if uploaded_file.state.name == "FAILED":
        raise ValueError(f"File upload failed: {uploaded_file.state.name}")
    elif uploaded_file.state.name == "ACTIVE":
        print(f"  File is now active and ready for use.")
    return uploaded_file

def process_script(script, start_time, end_time):
    return script #modify the timestamp with start_time and end_time

def append_to_script(file_path, text):
    with open(file_path, "a") as file:
        file.write(text)

def delete_audio_chunk(file_path):
    os.remove(file_path)
    print(f"  deleted audio chunk: {file_path}")

def get_genai_client(api_key):
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        return None

def transcribe_audio_to_script(client,
                               model_name,
                               audio_file_path,
                               script_file_path,
                               work_dir):
    audio_file_clip = audio_file_split.AudioFileClip(audio_file_path)
    audio_chunk_list  = audio_file_split.split_audio(audio_file_clip, work_dir)
    for audio_chunk in audio_chunk_list:
        uploaded_file = upload_file(client, audio_chunk.filename)
        script = transcribe(client, model_name, uploaded_file)
        processed_script = process_script(script, audio_chunk.start_time, audio_chunk.end_time)
        append_to_script(script_file_path, processed_script)
        get_uploaded_file(client, uploaded_file.name)
        delete_uploaded_file(client, uploaded_file.name)
        delete_audio_chunk(audio_chunk.filename)

if __name__ == "__main__":
    api_key = os.environ['GOOGLE_API_KEY']
    client = get_genai_client(api_key)
    #test(client,"gemini-2.5-flash")
    #list_uploaded_files(client)
    transcribe_audio_to_script(client,
                               model_name="gemini-2.5-flash",
                               audio_file_path="clips/audio.mp4",
                               script_file_path="clips/script.txt",
                               work_dir="clips/audio_chunks")
