import sys

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

from util.srt_utils import extract_subtitles

def get_image_prompts(input_text):
    text_splitter = SemanticChunker(OpenAIEmbeddings())
    return text_splitter.split_text(input_text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: <input_srt_file>")
        sys.exit(1)
    input_srt_file = sys.argv[1]
    prompts = get_image_prompts(extract_subtitles(input_srt_file))
    for prompt in prompts:
        print(prompt)

