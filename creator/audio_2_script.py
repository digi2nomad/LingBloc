from moviepy import *
from google import genai
from google.genai import types
import os,random,time

def test(client,model_name):
    response = client.models.generate_content(
        model=model_name,
        contents="Explain how Gemini makes youtube video",
    )
    print(response.text)

def list_files(client):
    files = client.files.list()
    for file in files:
        print(" ", file.name)

def get_file(client,filename): 
    file = client.files.get(name=filename)
    print(" ", file.name)

def delete_file(client,filename):
    client.files.delete(name=filename)

def transcribe(client,model_name,uploaded_file):
    max_retries = 3
    initial_delay = 1
    response = None
    last_exception = None # keep the last exception
    prompt = """
        Transcribe the audio, in the format of timestamp, speaker, caption.
        use speaker A, speaker B, etc. to identify speakers. the timestamp
        should be in the format of [MM:SS:ss]. Each caption sentence should 
        not be too long to fit into one line of a screen.
        """
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

    return response.text

def upload_file(audio_file):
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

def get_genai_client(api_key):
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        return None

if __name__ == "__main__":
    api_key = os.environ['GOOGLE_API_KEY']
    client = get_genai_client(api_key)
    #test(client,"gemini-2.5-flash")
    #list_files(client)

    #uploaded_file = upload_file("clips/small_audio.wav")
    #script = transcribe(client,"gemini-2.5-flash", uploaded_file)
    #print(script)
    #get_file(client, uploaded_file.name)
    #delete_file(client, uploaded_file.name)
