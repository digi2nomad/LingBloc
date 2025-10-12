## srt_utils.py: utility functions for srt files
import sys

def extract_subtitles(srt_file) -> str:
    """
    Extracts subtitle text from an SRT file by removing timing and index information.
    Combines subtitle text entries into a single string.

    :param srt_file: Path to the SRT file to process
    :return: Combined subtitle text as a single string with entries separated by spaces
    """
    subtitles_text = []
    with open(srt_file, 'r', encoding='utf-8') as f:
        current_text = ""
        for line in f:
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

def divide_subtitles(srt_file, max_length=100) -> list:
    """
    Splits an SRT file into multiple chunks based on the number of subtitle entries.

    Args:
        srt_file: Path to the input SRT file.
        max_length (int): Number of subtitle entries per chunk.
    """
    return_chunks = []
    with open(srt_file, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()

    current_subtitle_count = 0
    current_chunk_lines = []
    last_number = None

    for line in lines:
        if line.strip().isdigit():  # this a number, it indicates a start of a new subtitle entry
            current_subtitle_count += 1

        if current_subtitle_count >= max_length:
            # Add the current chunk (i.e.: current_chunk_lines) to the return list
            return_chunks.append("".join(current_chunk_lines))

            # Reset for the next chunk
            last_number = line.strip()
            current_subtitle_count = 0
            current_chunk_lines = []
        else:
            if last_number:
                current_chunk_lines.append(last_number+"\n")
            current_chunk_lines.append(line)
            last_number = None

    # Add the last chunk if any remaining lines to the return list
    if current_chunk_lines:
        if last_number:
            current_chunk_lines.append(last_number+"\n")
        return_chunks.append("".join(current_chunk_lines))
    return return_chunks

if __name__ == "__main__":
    sub_chunks = divide_subtitles("clips/script.txt", 100)
    for i, chunk in enumerate(sub_chunks):
        save_file = "clips/script_chunk_" + str(i) + ".txt"
        with open(save_file, "w", encoding="utf-8") as file:
            file.write(chunk)