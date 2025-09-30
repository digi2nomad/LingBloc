from google import genai
import os,sys

from util.srt_utils import extract_subtitles

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
