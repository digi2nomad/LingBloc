from google import genai
from google.genai import types
from datetime import datetime
import os,sys,random,time,io,re,audio_file_split

def test(genai_client, model_name):
    response = genai_client.models.generate_content(
        model=model_name,
        contents="Explain how Gemini makes youtube video",
    )
    print(response.text)

def list_uploaded_files(genai_client):
    files = genai_client.files.list()
    for file in files:
        print(" ", file.name)

def get_uploaded_file(genai_client, filename):
    file = genai_client.files.get(name=filename)
    print(" ", file.name)

def delete_uploaded_file(genai_client, filename):
    genai_client.files.delete(name=filename)
    print(" ", filename, "deleted")

def transcribe(genai_client,
               model_name,
               uploaded_file):
    max_retries = 3
    initial_delay = 1
    response = None
    prompt = f"""
        You are a transcription service for video caption, please transcribe the audio file into  SRT (SubRip) 
        file format, all timestamps must always in the format: 
             HH:MM:SS,mmm --> HH:MM:SS,mmm
             Where HH, MM, and SS are hours, minutes, and seconds, respectively, and mmm is milliseconds.
             Correct format: 00:00:00,500 --> 00:00:07,000 
             Incorrect format: 00:00,500 --> 00:07,000 
        Each subtitle should be concise and clear and each subtitle should not be too long in order to fit into 
        one line of a screen. After every subtitle, you need to enter a new line to separate subtitle blocks 
        from each other, so they won't appear together. 
        """
    print(f"  transcribing {uploaded_file.name} with prompt:\n {prompt.strip()}")
    for attempt in range(max_retries): # try max_retries times
        try:
            response = genai_client.models.generate_content(
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

def upload_file(genai_client, audio_file):
    max_retries = 3
    initial_delay = 1
    uploaded_file = None
    last_exception = None # keep the last exception
    for attempt in range(max_retries): # try max_tries times
        try:
            print(f"  uploading (try {attempt + 1}/{max_retries}): {audio_file}")
            uploaded_file = genai_client.files.upload(file=audio_file)
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
            uploaded_file = genai_client.files.get(audio_file) # Refresh the file object

    if uploaded_file.state.name == "FAILED":
        raise ValueError(f"File upload failed: {uploaded_file.state.name}")
    elif uploaded_file.state.name == "ACTIVE":
        print(f"  File is now active and ready for use.")
    return uploaded_file

def calculate_time (hours,
                    minutes,
                    seconds,
                    milliseconds,
                    adjust_time):
    dtime = datetime(year=1983,
                     month=12,
                     day=12,
                     hour=int(hours),
                     minute=int(minutes),
                     second=int(seconds),
                     microsecond=int(milliseconds)).timestamp()
    result = dtime + adjust_time
    return result

def parse_timestamp_fields(timestamp):
    milliseconds = "0"
    c = timestamp.count(':') # could be 2 or 1
    if c == 2:
        hours, minutes, seconds = timestamp.split(":")
    elif c == 1:
        hours = "0"
        minutes, seconds = timestamp.split(":")
    else:
        raise ValueError("invalid timestamp format: {timestamp}")
    c = seconds.count(',') # could be 0 or 1
    if c == 0:
        pass
    elif c == 1:
        seconds, milliseconds = seconds.split(",")
    else:
        raise ValueError("invalid timestamp format: {timestamp}")
    if int(seconds) > 59:
        quotient, remainder = divmod(int(seconds), 60)
        seconds = quotient
        milliseconds = int(milliseconds) + remainder
    milliseconds = int(milliseconds) * 1000 # convert to microseconds
    return hours, minutes, seconds, milliseconds

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def parse_start_end_timestamps(line):
    parts=line.split(" --> ")
    start_timestamp = parts[0].strip()
    end_timestamp = parts[1].strip()
    return start_timestamp, end_timestamp

def replace_timestamp(old_timestamp, new_time, line):
    new_timestamp = datetime.fromtimestamp(new_time).strftime('%H:%M:%S,%f')[:-3] #take only the first 3 digits of microseconds
    return re.sub(old_timestamp, new_timestamp, line)

def adjust_timestamps(srt_script, adjust_time, last_subtitle_number):
    processed_srt_script = ""
    string_buf = io.StringIO(srt_script)
    current_subtitle_number = 0
    while True:
        line = string_buf.readline()
        if not line:
            break
        elif line.strip() == "":
            processed_srt_script += line
        elif is_int(line.strip()):
            current_subtitle_number = last_subtitle_number + int(line.strip())
            processed_srt_script += str(current_subtitle_number)+"\n"
        elif re.match(".*-->.*", line):
            start_timestamp, end_timestamp = parse_start_end_timestamps(line)
            hours_start, minutes_start, seconds_start, milliseconds_start = parse_timestamp_fields(start_timestamp)
            new_start = calculate_time(hours_start, minutes_start, seconds_start, milliseconds_start, adjust_time)
            hours_end, minutes_end, seconds_end, milliseconds_end = parse_timestamp_fields(end_timestamp)
            new_end = calculate_time(hours_end, minutes_end, seconds_end, milliseconds_end, adjust_time)
            line = replace_timestamp(start_timestamp, new_start, line)
            line = replace_timestamp(end_timestamp, new_end, line)
            processed_srt_script += line
        else:
            processed_srt_script += line

    return processed_srt_script, current_subtitle_number

def append_to_script(script_file_path, text):
    with open(script_file_path, "a") as script_file:
        script_file.write(text)

def delete_audio_chunk(file_path):
    os.remove(file_path)
    print(f"  deleted audio chunk: {file_path}")

def get_genai_client(genai_api_key):
    try:
        return genai.Client(api_key=genai_api_key)
    except Exception as e:
        return None

def transcribe_audio_to_script(genai_client,
                               model_name,
                               audio_file_path,
                               script_file_path,
                               work_dir):
    audio_file_clip = audio_file_split.AudioFileClip(audio_file_path)
    audio_chunk_list  = audio_file_split.split_audio(audio_file_clip, work_dir)
    last_subtitle_number = 0
    for audio_chunk in audio_chunk_list:
        uploaded_file = upload_file(genai_client, audio_chunk.filename)
        srt_script = transcribe(genai_client, model_name, uploaded_file)
        processed_script, last_subtitle_number = adjust_timestamps(srt_script, audio_chunk.start_time, last_subtitle_number)
        append_to_script(script_file_path, processed_script)
        get_uploaded_file(genai_client, uploaded_file.name)
        delete_uploaded_file(genai_client, uploaded_file.name)
        delete_audio_chunk(audio_chunk.filename)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage:<input_audio_file> <output_script_file> <work_folder>")
        sys.exit(1)

    try:
        api_key = os.environ['GOOGLE_API_KEY']
        client = get_genai_client(api_key)
        transcribe_audio_to_script(client,
                                   model_name="gemini-2.5-flash",
                                   audio_file_path=sys.argv[1], # "clips/audio.mp4",
                                   script_file_path=sys.argv[2], #"clips/script.txt",
                                   work_dir=sys.argv[3] #"clips/audio_chunks"
                                   )
        client.close()
    except:
        pass
