from moviepy import *
import os,sys

def gen_video (clips_folder, audio_file, output_video):
    video_folder = clips_folder
    image_folder = clips_folder 
    image_files = [os.path.join(image_folder, f) 
        for f in sorted(os.listdir(image_folder)) 
            if f.endswith(('.png', '.jpg', '.jpeg'))]

    fps = 1  # Adjust frames per second (fps)

    clips = [ImageClip(m).with_duration(10)
        for m in image_files]

    audio_clip = AudioFileClip(audio_file)

    video_clip = concatenate_videoclips(clips, method="compose")
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_video, fps=fps)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: <clips_folder> <audio_file> <output_video>")
        sys.exit(1)

    clips_folder = sys.argv[1]
    audio_file = sys.argv[2]
    output_video = sys.argv[3]

    gen_video(clips_folder, audio_file, output_video)
