
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