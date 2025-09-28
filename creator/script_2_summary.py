from google import genai
import os,sys

def extract_subtitles(srt_file):
    subtitles_text = []
    with open(srt_file, 'r', encoding='utf-8') as file:
        current_text = ""
        for line in file:
            line = line.strip()
            if line.isdigit() or '-->' in line or not line:
                if current_text:
                    subtitles_text.append(current_text.strip())
                    current_text = ""
            else:
                current_text += " " + line
        if current_text:
            subtitles_text.append(current_text.strip())
    return " ".join(subtitles_text)

def save_summary(summary_txt,
                 output_filename):
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(summary)
    print(f"Summary saved to {output_filename}")

def summarize(genai_client,
              model_name,
              srt_file):
    text = extract_subtitles(srt_file)
    response = genai_client.models.generate_content(
        model=model_name,
        contents=f"Summarize the following text:\n{text}"
    )
    return response.text

def get_genai_client(genai_api_key):
    try:
        return genai.Client(api_key=genai_api_key)
    except Exception as e:
        return None

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(f"Usage: <input_srt_file> <output_summary_file>")
        sys.exit(1)

    api_key = os.environ['GOOGLE_API_KEY']
    client = get_genai_client(api_key)

    input_srt_file= sys.argv[1]
    output_summary_file = sys.argv[2]

    summary = summarize(client, "gemini-2.5-flash", input_srt_file)
    save_summary(summary,output_summary_file)
