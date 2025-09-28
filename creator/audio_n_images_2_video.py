from moviepy import *
import os,sys

def gen_video_with_thumbnail(thumbnail_image, audio_file, output_video):
    image_files = [thumbnail_image]

    fps = 1  # Adjust frames per second (fps) as needed
    clips = [ImageClip(m).with_duration(10)
        for m in image_files]

    audio_clip = AudioFileClip(audio_file)
    video_clip = concatenate_videoclips(clips, method="compose")
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_video, fps=fps)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: <thumbnail_image> <audio_file> <output_video>")
        sys.exit(1)

    thumbnail = sys.argv[1] #clips/thumbnail-english.jpg
    audio = sys.argv[2] #clips/audio-english.mp4
    output = sys.argv[3] #clips/english.mp4

    gen_video_with_thumbnail(thumbnail, audio, output)
