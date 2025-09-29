from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
import sys

def add_subtitles(input_video_file, srt_file, output_video_file):
    generator = lambda text: TextClip(text,
                                      font='font/font.ttf',
                                      font_size=24,
                                      color='white')
    subtitles_clip = SubtitlesClip(srt_file, make_textclip=generator, encoding='utf-8')
    input_video_clip = VideoFileClip(input_video_file)
    output_video_clip = CompositeVideoClip([input_video_clip, subtitles_clip])
    output_video_clip.write_videofile(output_video_file, fps=input_video_clip.fps)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: <video_file> <srt_file> <output_file>")
        sys.exit(1)

    add_subtitles(sys.argv[1], sys.argv[2], sys.argv[3])
