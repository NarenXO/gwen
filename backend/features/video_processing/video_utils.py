# video_utils.py
# Everything related to video frames, scenes, clips

import cv2
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip
import os
from typing import List, Tuple


# ─────────────────────────────────────────────
# FUNCTION 1 — EXTRACT FRAMES
# ─────────────────────────────────────────────

def extract_frames(video_path: str, interval_seconds: float = 1.0) -> List[Tuple]:
    """
    Extract frames from video at regular intervals.
    Returns list of (timestamp, frame) tuples.
    """

    frames = []
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frames_per_interval = int(fps * interval_seconds)
    frame_index = 0

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = cap.read()

        if not success:
            break

        timestamp = frame_index / fps
        frames.append((timestamp, frame))
        frame_index += frames_per_interval

        if frame_index >= total_frames:
            break

    cap.release()
    return frames


# ─────────────────────────────────────────────
# FUNCTION 2 — GET VIDEO RESOLUTION
# ─────────────────────────────────────────────

def get_video_resolution(video_path: str) -> str:
    """
    Returns resolution as string like "1920x1080"
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return f"{width}x{height}"


# ─────────────────────────────────────────────
# FUNCTION 3 — GET VIDEO DURATION
# ─────────────────────────────────────────────

def get_video_duration(video_path: str) -> float:
    """
    Returns total duration in seconds.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    return round(total_frames / fps, 2)


# ─────────────────────────────────────────────
# FUNCTION 4 — DETECT STATIC SCENES
# ─────────────────────────────────────────────

def detect_static_scenes(frames: List[Tuple], threshold: float = 10.0) -> List[dict]:
    """
    Compare consecutive frames.
    If difference is very low → static scene.
    Returns list of static scene segments.
    """

    static_segments = []
    static_start = None

    for i in range(1, len(frames)):
        prev_timestamp, prev_frame = frames[i - 1]
        curr_timestamp, curr_frame = frames[i]

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)

        if mean_diff < threshold:
            if static_start is None:
                static_start = prev_timestamp
        else:
            if static_start is not None:
                duration = prev_timestamp - static_start
                if duration > 3.0:
                    static_segments.append({
                        "start_time": round(static_start, 2),
                        "end_time": round(prev_timestamp, 2),
                        "duration": round(duration, 2)
                    })
                static_start = None

    if static_start is not None and len(frames) > 0:
        last_timestamp = frames[-1][0]
        duration = last_timestamp - static_start
        if duration > 3.0:
            static_segments.append({
                "start_time": round(static_start, 2),
                "end_time": round(last_timestamp, 2),
                "duration": round(duration, 2)
            })

    return static_segments


# ─────────────────────────────────────────────
# FUNCTION 5 — DETECT HOOK DURATION
# ─────────────────────────────────────────────

def detect_hook_duration(frames: List[Tuple], check_first_n_seconds: float = 30.0) -> float:
    """
    Measure how dynamic the first 30 seconds are.
    Returns hook duration in seconds.
    """

    first_section_frames = [
        (t, f) for t, f in frames if t <= check_first_n_seconds
    ]

    if len(first_section_frames) < 2:
        return 0.0

    differences = []

    for i in range(1, len(first_section_frames)):
        prev_timestamp, prev_frame = first_section_frames[i - 1]
        curr_timestamp, curr_frame = first_section_frames[i]

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)

        differences.append((curr_timestamp, mean_diff))

    if not differences:
        return 0.0

    avg_activity = np.mean([d for _, d in differences])
    hook_end = 0.0

    for timestamp, activity in differences:
        if activity >= avg_activity * 0.5:
            hook_end = timestamp

    return round(hook_end, 2)


# ─────────────────────────────────────────────
# FUNCTION 6 — DETECT SCENE CHANGES
# ─────────────────────────────────────────────

def detect_scene_changes(frames: List[Tuple], threshold: float = 30.0) -> List[float]:
    """
    Detect timestamps where scene changes suddenly.
    Returns list of timestamps where scene changes happen.
    """

    scene_change_timestamps = []

    for i in range(1, len(frames)):
        prev_timestamp, prev_frame = frames[i - 1]
        curr_timestamp, curr_frame = frames[i]

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)

        if mean_diff > threshold:
            scene_change_timestamps.append(curr_timestamp)

    return scene_change_timestamps


# ─────────────────────────────────────────────
# FUNCTION 7 — DETECT ENGAGING SEGMENTS
# ─────────────────────────────────────────────

def detect_engaging_segments(
    frames: List[Tuple],
    silence_segments: List[dict],
    scene_changes: List[float],
    video_duration: float,
    clip_length: float = 30.0,
    max_clips: int = 3
) -> List[Tuple[float, float]]:
    """
    Score each segment based on engagement heuristics:
    - High scene change frequency (visual excitement)
    - No silence (audio presence)
    - High motion between frames

    Returns top segments sorted by engagement score
    as list of (start, end) tuples.
    """

    if not frames:
        return []

    # Build silence lookup set (seconds that are silent)
    silent_seconds = set()
    for seg in silence_segments:
        start = int(seg["start_time"])
        end = int(seg["end_time"])
        for s in range(start, end + 1):
            silent_seconds.add(s)

    # Score each second of the video
    segment_scores = {}

    for i in range(1, len(frames)):
        prev_timestamp, prev_frame = frames[i - 1]
        curr_timestamp, curr_frame = frames[i]

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        motion_score = float(np.mean(diff))

        second = int(curr_timestamp)

        # Penalize silent moments
        if second in silent_seconds:
            motion_score *= 0.3

        segment_scores[second] = motion_score

    if not segment_scores:
        return []

    # Find best non-overlapping segments
    selected = []
    used_seconds = set()

    # Sort seconds by score descending
    sorted_seconds = sorted(
        segment_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for second, score in sorted_seconds:

        # Check overlap with already selected segments
        too_close = False
        for used in used_seconds:
            if abs(second - used) < clip_length:
                too_close = True
                break

        if too_close:
            continue

        # Build clip around this second
        start = max(0.0, float(second) - 5.0)
        end = min(video_duration, start + clip_length)

        if end == video_duration:
            start = max(0.0, end - clip_length)

        selected.append((round(start, 2), round(end, 2)))
        used_seconds.add(second)

        if len(selected) >= max_clips:
            break

    return selected


# ─────────────────────────────────────────────
# FUNCTION 8 — SELECT BEST CLIP SEGMENTS
# ─────────────────────────────────────────────

def select_best_segments(
    scene_changes: List[float],
    video_duration: float,
    clip_length: float = 30.0,
    max_clips: int = 3
) -> List[Tuple[float, float]]:
    """
    From scene change timestamps, select best segments for shorts.
    Returns list of (start, end) tuples in seconds.
    """

    if not scene_changes:
        segments = []
        start = 0.0

        while start + clip_length < video_duration and len(segments) < max_clips:
            segments.append((start, start + clip_length))
            start += clip_length

        return segments

    segments = []
    used_timestamps = set()

    for change_time in scene_changes:

        too_close = False
        for used in used_timestamps:
            if abs(change_time - used) < clip_length:
                too_close = True
                break

        if too_close:
            continue

        start = max(0.0, change_time - 5.0)
        end = min(video_duration, start + clip_length)

        if end == video_duration:
            start = max(0.0, end - clip_length)

        segments.append((round(start, 2), round(end, 2)))
        used_timestamps.add(change_time)

        if len(segments) >= max_clips:
            break

    return segments


# ─────────────────────────────────────────────
# FUNCTION 9 — CHECK IF VIDEO IS LANDSCAPE
# ─────────────────────────────────────────────

def is_landscape(video_path: str) -> bool:
    """
    Returns True if video is landscape (wider than tall).
    Returns False if already vertical.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return width > height


# ─────────────────────────────────────────────
# FUNCTION 10 — TRIM AND CROP CLIP TO VERTICAL
# ─────────────────────────────────────────────

def trim_and_export_vertical_clip(
    video_path: str,
    start: float,
    end: float,
    output_path: str
) -> str:
    """
    Trim video between start and end seconds.
    Crop to 9:16 vertical format.
    If landscape → apply blurred background instead of hard crop.
    """

    if is_landscape(video_path):
        return export_vertical_with_blur(video_path, start, end, output_path)

    video = VideoFileClip(video_path)
    clip = video.subclip(start, end)

    width = clip.w
    height = clip.h

    target_aspect = 9 / 16
    current_aspect = width / height

    if current_aspect > target_aspect:
        new_width = int(height * target_aspect)
        x_center = width // 2
        x1 = x_center - new_width // 2
        x2 = x_center + new_width // 2
        clip = clip.crop(x1=x1, y1=0, x2=x2, y2=height)
    else:
        new_height = int(width / target_aspect)
        y_center = height // 2
        y1 = y_center - new_height // 2
        y2 = y_center + new_height // 2
        clip = clip.crop(x1=0, y1=y1, x2=width, y2=y2)

    clip = clip.resize((1080, 1920))

    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    clip.close()
    video.close()

    return output_path


# ─────────────────────────────────────────────
# FUNCTION 11 — EXPORT VERTICAL WITH BLUR BACKGROUND
# ─────────────────────────────────────────────

def export_vertical_with_blur(
    video_path: str,
    start: float,
    end: float,
    output_path: str
) -> str:
    """
    Convert landscape video to vertical with blurred background.

    Output looks like:
    ┌───────────────┐
    │ ░░ blurred ░░ │
    │ ░░ blurred ░░ │
    │  clear video  │
    │  clear video  │
    │ ░░ blurred ░░ │
    │ ░░ blurred ░░ │
    └───────────────┘
    """

    target_w = 1080
    target_h = 1920

    video = VideoFileClip(video_path)
    clip = video.subclip(start, end)

    # Scale original clip to fit target width
    scale_factor = target_w / clip.w
    scaled_h = int(clip.h * scale_factor)
    scaled_clip = clip.resize(width=target_w)

    # Create blurred background
    # Fill entire 9:16 frame with blurred version of video
    bg_scale = max(target_w / clip.w, target_h / clip.h)
    bg_clip = clip.resize(bg_scale)

    # Crop background to exact target size
    bg_x = (bg_clip.w - target_w) // 2
    bg_y = (bg_clip.h - target_h) // 2
    bg_clip = bg_clip.crop(
        x1=bg_x,
        y1=bg_y,
        x2=bg_x + target_w,
        y2=bg_y + target_h
    )

    # Apply blur to background frames
    def blur_frame(frame):
        return cv2.GaussianBlur(frame, (51, 51), 0)

    bg_clip = bg_clip.fl_image(blur_frame)

    # Position scaled clip in center of frame
    y_position = (target_h - scaled_h) // 2

    # Composite: blurred background + clear centered video
    final = CompositeVideoClip(
        [
            bg_clip.set_position((0, 0)),
            scaled_clip.set_position(("center", y_position))
        ],
        size=(target_w, target_h)
    )

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    clip.close()
    video.close()
    bg_clip.close()
    final.close()

    return output_path