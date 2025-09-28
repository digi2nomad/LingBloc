from moviepy import *
import numpy as np
import math, os, sys, pathlib

class AudioChunk:
    def __init__(self, filename, start_time, end_time):
        self.filename = filename
        self.start_time = start_time
        self.end_time = end_time

MAX_CHUNK_LENGTH = 5 * 60  # max chunk length (in seconds), default is 5 minutes
MIN_SILENCE_LENGTH = 0.5 # min silence length (in seconds)
SILENCE_THRESH = -40  # silence threshold (dB)

def get_audio_duration(audio_file):
    return audio_file.duration

def find_silent_points(audio_file,
                       window_size=0.1,
                       silence_threshold=0.01):
    """
    Finds silent points in an audio clip.

    Args:
        audio_file (AudioFileClip): The audio file clip to analyze.
        window_size (float): The size of the analysis window in seconds.
        silence_threshold (float): The volume level below which a window is considered silent.

    Returns:
        list: A list of (start, end) tuples representing silent intervals.
    """
    silence_points = []
    is_silent = False
    silent_start = 0

    for t in np.arange(0, audio_file.duration, window_size):
        # Get audio data for the current window
        sub_clip = audio_file.subclipped(t, min(t + window_size, audio_file.duration))

        # Calculate average volume (or RMS)
        # This is a simplified example; a more robust calculation might be needed
        if sub_clip.duration > 0:
            volume = np.mean(np.abs(sub_clip.to_soundarray()))
        else:
            volume = 0

        if volume < silence_threshold and not is_silent:
            is_silent = True
            silent_start = t
        elif volume >= silence_threshold and is_silent:
            is_silent = False
            silence_points.append((silent_start, t))

    if is_silent:  # Handle trailing silence
        silence_points.append((silent_start, audio_file.duration))

    return silence_points #[(start1, end1), (start2, end2), ...]

def find_split_points(audio_length,
                      silence_points,
                      max_chunk_length):

    split_points = []
    current_chunk_start = 0.0
    last_silence_midpoint = -1.0 # Track the last suitable silence midpoint

    # Iterate through silence periods to find good split points
    for start, end in silence_points:
        silence_midpoint = (start + end) / 2.0
        potential_chunk_len = silence_midpoint - current_chunk_start

        # If adding this silence midpoint doesn't exceed max length, consider it
        if potential_chunk_len <= max_chunk_length:
            last_silence_midpoint = silence_midpoint
        else:
            # The current chunk is too long if we go to this silence.
            # Did we have a previous suitable silence point?
            if last_silence_midpoint > current_chunk_start:
                split_points.append(last_silence_midpoint)
                current_chunk_start = last_silence_midpoint
                # Re-evaluate the current silence period from the new start
                if (silence_midpoint - current_chunk_start) <= max_chunk_length:
                     last_silence_midpoint = silence_midpoint
                else: # Even starting from the last split, this silence is too far
                     # Force a split before this silence if the segment is too long
                     if (start - current_chunk_start) > max_chunk_length:
                          # Force split at max length if no silence available
                          forced_split = current_chunk_start + max_chunk_length
                          split_points.append(forced_split)
                          current_chunk_start = forced_split
                          last_silence_midpoint = -1 # Reset last silence point
                     else:
                          # Split right before the current silence starts
                          split_points.append(start)
                          current_chunk_start = start
                          last_silence_midpoint = silence_midpoint # This silence is now the potential next split

            else:
                # No suitable silence point found, and the chunk is too long.
                # Force split at max_chunk_length_sec.
                forced_split = current_chunk_start + max_chunk_length
                split_points.append(forced_split)
                current_chunk_start = forced_split
                # Re-evaluate the current silence period from the new start
                if (silence_midpoint - current_chunk_start) <= max_chunk_length:
                     last_silence_midpoint = silence_midpoint
                else:
                     last_silence_midpoint = -1 # Reset

    # After checking all silences, handle the remaining audio segment
    remaining_length = audio_length - current_chunk_start
    if remaining_length > 0:
        if remaining_length > max_chunk_length:
             # If the remainder is too long, split it further
             num_additional_splits = math.ceil(remaining_length / max_chunk_length)
             split_interval = remaining_length / num_additional_splits
             for i in range(1, num_additional_splits):
                 split_points.append(current_chunk_start + i * split_interval)

    # Add the final end point
    split_points.append(audio_length)

    # Sort and remove duplicates, ensure points are within bounds
    split_points = sorted(list(set(p for p in split_points if 0 < p <= audio_length)))

    print(f"get {len(split_points)} split points (second)")
    return split_points

def split_audio(audio_file,
                work_dir,
                max_chunk_length=MAX_CHUNK_LENGTH,
                min_silence_len=MIN_SILENCE_LENGTH,
                silence_thresh=SILENCE_THRESH):
    """
    Split an audio file into smaller chunks using silence points
    and maximum chunk length constraints.
    """
    pathlib.Path(work_dir).mkdir(parents=True, exist_ok=True)

    print(f"audio file: {audio_file.filename}")
    total_length = get_audio_duration(audio_file)
    if total_length is None:
        print(f"error：cannot get audio length，cannot split {audio_file}")
        return []
    print(f"audio length: {total_length:.2f} second ({total_length/60:.2f} minutes)")

    # find silent points
    silence_points = find_silent_points(audio_file, min_silence_len, silence_thresh)

    # calculate split points
    split_points = find_split_points(total_length, silence_points, max_chunk_length)

    # execute split
    audio_chunk_list = []
    start_time = 0.0
    for i, end_time in enumerate(split_points):
        # Make sure the slice has a valid length
        if end_time <= start_time + 0.01: # Add a small threshold to avoid zero-length or very short fragments
            print(f"  Skip invalid split points: {start_time:.2f}s -> {end_time:.2f}s")
            continue

        chunk_filename = os.path.join(work_dir, f"chunk_{i + 1:03d}.mp3")
        audio_chunk_list.append(AudioChunk(chunk_filename, start_time, end_time))
        duration = end_time - start_time
        print(f"export chunk {i+1}/{len(split_points)}: {start_time:.2f}s - {end_time:.2f}s ({duration:.2f}s) -> {chunk_filename}")
        (audio_file.subclipped(start_time, end_time).write_audiofile(chunk_filename,
                                                                     codec='mp3',
                                                                     bitrate='192k',
                                                                     logger=None))
        start_time = end_time # Update the start time of the next segment

    if not audio_chunk_list:
         print("error, failed to split audio")
         return []
    print(f"finish splitting. generated {len(audio_chunk_list)} chunks，Keep in {work_dir} folder")
    return audio_chunk_list

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: <input_audio_file> <work_folder>")
        sys.exit(1)
    try:
        audioFileClip = AudioFileClip(sys.argv[1]) #"clips/audio.mp4"
        split_audio(audioFileClip, sys.argv[2]) #"clips/audio_chunks"
        audioFileClip.close()
    except Exception as e:
        print(f"Error processing video: {str(e)}")
