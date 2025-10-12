from moviepy import AudioFileClip, concatenate_audioclips

def merge_audio(audio_files, output_file):
    """
    Merge multiple audio files into a single output file.

    Args:
        audio_files (list): List of audio file paths to merge
        output_file (str): Path where the merged audio file will be saved

    Returns:
        None
    """
    try:
        # Load all audio clips
        audio_clips = [AudioFileClip(file) for file in audio_files]

        # Concatenate the audio clips
        final_audio = concatenate_audioclips(audio_clips)

        # Write the combined audio to the output file
        final_audio.write_audiofile(output_file)

        # Close all clips to free resources
        for clip in audio_clips:
            clip.close()
        final_audio.close()

    except Exception as e:
        print(f"Error merging audio files: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    audio_fs = ["audio_clip1.mp3", "audio_clip2.mp3", "audio_clip3.mp3"]
    merge_audio(audio_fs, "combined_audio.mp3")
