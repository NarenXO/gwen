# audio_utils.py
# Everything related to audio analysis

import librosa
import numpy as np
import os
import tempfile
from moviepy.editor import VideoFileClip
from typing import List


# ─────────────────────────────────────────────
# FUNCTION 1 — EXTRACT AUDIO FROM VIDEO
# ─────────────────────────────────────────────

def extract_audio_from_video(video_path: str, output_audio_path: str) -> str:
    """
    Extract audio track from video file.
    Save as WAV file.
    Uses system temp to avoid OneDrive/FFmpeg path issues on Windows.
    Returns path to audio file.
    """

    video_path = os.path.abspath(video_path)

    # Use system temp to avoid OneDrive FFmpeg issues
    audio_filename = os.path.basename(output_audio_path)
    safe_output_path = os.path.join(tempfile.gettempdir(), audio_filename)

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

    # Move to requested location if different
    if safe_output_path != output_audio_path:
        import shutil
        try:
            shutil.move(safe_output_path, output_audio_path)
            return output_audio_path
        except Exception:
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
    Returns list of silence segments with timestamps.
    """

    y, sr = librosa.load(audio_path, sr=None)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]

    times = librosa.frames_to_time(
        np.arange(len(rms)),
        sr=sr,
        hop_length=512
    )

    silence_segments = []
    silence_start = None

    for i, (time, amplitude) in enumerate(zip(times, rms)):

        if amplitude < silence_threshold:
            if silence_start is None:
                silence_start = time
        else:
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
# FUNCTION 3 — GENERATE WHISPER SUBTITLES
# ─────────────────────────────────────────────

def generate_whisper_subtitles(
    audio_path: str,
    output_srt_path: str
) -> str:
    """
    Use OpenAI Whisper for real speech-to-text subtitles.
    Falls back to basic subtitles if Whisper not installed.
    Returns path to SRT file.
    """

    try:
        import whisper

        print("   [Subtitles] Loading Whisper model...")
        model = whisper.load_model("small")

        print("   [Subtitles] Transcribing audio...")
        result = model.transcribe(audio_path)

        srt_content = ""

        for i, segment in enumerate(result["segments"], 1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()

            start_str = _seconds_to_srt_time(start)
            end_str = _seconds_to_srt_time(end)

            srt_content += f"{i}\n"
            srt_content += f"{start_str} --> {end_str}\n"
            srt_content += f"{text}\n\n"

        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        print("   [Subtitles] Whisper transcription complete")
        return output_srt_path

    except ImportError:
        # Whisper not installed — fall back to basic subtitles
        print("   [Subtitles] Whisper not installed — using basic subtitles")
        print("   [Subtitles] Run: pip install openai-whisper to enable speech-to-text")
        return generate_basic_srt(output_srt_path, clip_duration=30.0)


# ─────────────────────────────────────────────
# FUNCTION 4 — GENERATE BASIC SUBTITLE FILE
# ─────────────────────────────────────────────

def generate_basic_srt(
    output_srt_path: str,
    clip_duration: float
) -> str:
    """
    Generate a basic placeholder SRT subtitle file.
    Used as fallback when Whisper is not available.
    Returns path to SRT file.
    """

    srt_content = ""
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

    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return output_srt_path


# ─────────────────────────────────────────────
# HELPER — SECONDS TO SRT TIME FORMAT
# ─────────────────────────────────────────────

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