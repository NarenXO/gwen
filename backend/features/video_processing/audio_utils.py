# audio_utils.py
# Everything related to audio analysis

import librosa
import numpy as np
import os
from moviepy.editor import VideoFileClip
from typing import List


# ─────────────────────────────────────────────
# FUNCTION 1 — EXTRACT AUDIO FROM VIDEO
# ─────────────────────────────────────────────

def extract_audio_from_video(video_path: str, output_audio_path: str) -> str:
    """
    Extract audio track from video file.
    Save as WAV file.
    Returns path to audio file.
    
    Uses local temp path to avoid OneDrive/network drive issues with FFmpeg.
    """

    import tempfile

    # Normalize input video path
    video_path = os.path.abspath(video_path)

    # Use system temp directory instead of project folder
    # This avoids OneDrive path issues with FFmpeg on Windows
    system_temp = tempfile.gettempdir()
    
    # Get just the filename from the requested output path
    audio_filename = os.path.basename(output_audio_path)
    
    # Build a safe local path in system temp
    safe_output_path = os.path.join(system_temp, audio_filename)

    # Ensure directory exists
    if not os.path.exists(system_temp):
        os.makedirs(system_temp)

    video = VideoFileClip(video_path)

    if video.audio is None:
        video.close()
        raise ValueError("Video has no audio track")

    video.audio.write_audiofile(
        safe_output_path,
        verbose=False,
        logger=None
    )

    video.close()

    # If caller wants it in a different location, move it there
    if safe_output_path != output_audio_path:
        import shutil
        try:
            shutil.move(safe_output_path, output_audio_path)
            return output_audio_path
        except Exception:
            # If move fails, return the temp location
            # File still exists and is usable
            return safe_output_path

    return safe_output_path


# ─────────────────────────────────────────────
# FUNCTION 2 — DETECT SILENCE SEGMENTS
# ─────────────────────────────────────────────

def detect_silence_segments(
    audio_path: str,
    silence_threshold: float = 0.02,
    min_silence_duration: float = 1.5
) -> List[dict]:
    """
    Load audio and find silent sections.
    
    silence_threshold: amplitude below this = silence (0.0 to 1.0)
    min_silence_duration: only record silences longer than this (seconds)
    
    Returns list of silence segments:
        [{"start_time": 45.0, "end_time": 48.5, "duration": 3.5}]
    """
    
    # Load audio with librosa
    # y = audio samples, sr = sample rate
    y, sr = librosa.load(audio_path, sr=None)
    
    # Calculate amplitude over time (root mean square energy)
    # hop_length=512 means we check every 512 samples
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    
    # Convert frame indices to timestamps
    times = librosa.frames_to_time(
        np.arange(len(rms)),
        sr=sr,
        hop_length=512
    )
    
    # Find silent frames
    silence_segments = []
    silence_start = None
    
    for i, (time, amplitude) in enumerate(zip(times, rms)):
        
        if amplitude < silence_threshold:
            # This moment is silent
            if silence_start is None:
                silence_start = time
        else:
            # Not silent
            if silence_start is not None:
                duration = time - silence_start
                
                if duration >= min_silence_duration:
                    silence_segments.append({
                        "start_time": round(float(silence_start), 2),
                        "end_time": round(float(time), 2),
                        "duration": round(float(duration), 2)
                    })
                
                silence_start = None
    
    return silence_segments


# ─────────────────────────────────────────────
# FUNCTION 3 — GENERATE BASIC SUBTITLE FILE
# ─────────────────────────────────────────────

def generate_basic_srt(
    audio_path: str,
    output_srt_path: str,
    clip_duration: float
) -> str:
    """
    Generate a basic SRT subtitle file.
    
    Note: Real speech recognition needs Whisper.
    This creates a placeholder SRT structure.
    You can plug in Whisper later easily.
    
    Returns path to SRT file.
    """
    
    # Basic SRT without speech recognition
    # Shows simple subtitle markers
    # You will plug Whisper in here later
    
    srt_content = ""
    
    # Create subtitle entry every 5 seconds
    subtitle_index = 1
    current_time = 0.0
    segment_length = 5.0
    
    while current_time < clip_duration:
        end_time = min(current_time + segment_length, clip_duration)
        
        start_str = _seconds_to_srt_time(current_time)
        end_str = _seconds_to_srt_time(end_time)
        
        srt_content += f"{subtitle_index}\n"
        srt_content += f"{start_str} --> {end_str}\n"
        srt_content += f"[Subtitle {subtitle_index}]\n\n"
        
        subtitle_index += 1
        current_time += segment_length
    
    # Write to file
    with open(output_srt_path, "w") as f:
        f.write(srt_content)
    
    return output_srt_path


def _seconds_to_srt_time(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format.
    Example: 65.5 → "00:01:05,500"
    """
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"