from moviepy import *
import numpy as np

def find_silent_intervals(audio_clip, window_size=0.1, volume_threshold=0.01):
    """
    Finds silent intervals in an audio clip.

    Args:
        audio_clip (AudioFileClip): The audio clip to analyze.
        window_size (float): The size of the analysis window in seconds.
        volume_threshold (float): The volume level below which a window is considered silent.

    Returns:
        list: A list of (start, end) tuples representing silent intervals.
    """
    silent_intervals = []
    is_silent = False
    silent_start = 0

    for t in np.arange(0, audio_clip.duration, window_size):
        # Get audio data for the current window
        sub_clip = audio_clip.subclipped(t, min(t + window_size, audio_clip.duration))

        # Calculate average volume (or RMS)
        # This is a simplified example; a more robust calculation might be needed
        if sub_clip.duration > 0:
            volume = np.mean(np.abs(sub_clip.to_soundarray()))
        else:
            volume = 0

        if volume < volume_threshold and not is_silent:
            is_silent = True
            silent_start = t
        elif volume >= volume_threshold and is_silent:
            is_silent = False
            silent_intervals.append((silent_start, t))

    if is_silent:  # Handle trailing silence
        silent_intervals.append((silent_start, audio_clip.duration))

    return silent_intervals


if __name__ == "__main__":
    try:
        audio = AudioFileClip("clips/small_audio.wav")
        silent_parts = find_silent_intervals(audio)
        print(f"Found {len(silent_parts)} silent intervals:")
        for i, (start, end) in enumerate(silent_parts, 1):
            print(f"Interval {i}: {start:.2f}s - {end:.2f}s (duration: {end - start:.2f}s)")
        audio.close()
    except Exception as e:
        print(f"Error processing video: {str(e)}")
