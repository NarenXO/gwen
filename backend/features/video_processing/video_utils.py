# video_utils.py
# Everything related to video frames, scenes, clips

import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import os
from typing import List, Tuple


# ─────────────────────────────────────────────
# FUNCTION 1 — EXTRACT FRAMES
# ─────────────────────────────────────────────

def extract_frames(video_path: str, interval_seconds: float = 1.0) -> List[Tuple]:
    """
    Extract frames from video at regular intervals.
    
    Returns list of (timestamp, frame) tuples.
    Frame is a numpy array (image).
    
    Example:
        frames = extract_frames("video.mp4", interval_seconds=1.0)
        # Returns: [(0.0, array), (1.0, array), (2.0, array), ...]
    """
    
    frames = []
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    # How many frames to skip between extractions
    frames_per_interval = int(fps * interval_seconds)
    
    frame_index = 0
    
    while True:
        # Jump to specific frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        success, frame = cap.read()
        
        if not success:
            break
        
        # Calculate timestamp in seconds
        timestamp = frame_index / fps
        
        frames.append((timestamp, frame))
        
        # Move to next interval
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
    
    duration = total_frames / fps
    return round(duration, 2)


# ─────────────────────────────────────────────
# FUNCTION 4 — DETECT STATIC SCENES
# ─────────────────────────────────────────────

def detect_static_scenes(frames: List[Tuple], threshold: float = 10.0) -> List[dict]:
    """
    Compare consecutive frames.
    If difference is very low → scene is static (boring, no movement).
    
    threshold: lower = more sensitive (detects smaller differences)
    
    Returns list of static scene segments with timestamps.
    
    Example output:
        [
            {"start_time": 45.0, "end_time": 52.0, "duration": 7.0},
            {"start_time": 120.0, "end_time": 125.0, "duration": 5.0}
        ]
    """
    
    static_segments = []
    
    static_start = None
    
    for i in range(1, len(frames)):
        
        prev_timestamp, prev_frame = frames[i - 1]
        curr_timestamp, curr_frame = frames[i]
        
        # Convert frames to grayscale for comparison
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference between frames
        diff = cv2.absdiff(prev_gray, curr_gray)
        
        # Mean difference value
        mean_diff = np.mean(diff)
        
        if mean_diff < threshold:
            # Scene is static
            if static_start is None:
                static_start = prev_timestamp
        else:
            # Scene changed
            if static_start is not None:
                duration = prev_timestamp - static_start
                
                # Only record if static for more than 3 seconds
                if duration > 3.0:
                    static_segments.append({
                        "start_time": round(static_start, 2),
                        "end_time": round(prev_timestamp, 2),
                        "duration": round(duration, 2)
                    })
                
                static_start = None
    
    # Handle case where video ends while still static
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
    Look at first 30 seconds.
    Measure how dynamic the content is.
    Find first point where content becomes less engaging.
    
    Returns hook duration in seconds.
    A good hook is fast-paced in first 15-20 seconds.
    """
    
    # Only look at first N seconds
    first_section_frames = [
        (t, f) for t, f in frames if t <= check_first_n_seconds
    ]
    
    if len(first_section_frames) < 2:
        return 0.0
    
    # Calculate frame differences in first section
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
    
    # Find average activity level
    avg_activity = np.mean([d for _, d in differences])
    
    # Hook ends when activity drops below average
    hook_end = 0.0
    
    for timestamp, activity in differences:
        if activity >= avg_activity * 0.5:
            hook_end = timestamp
    
    return round(hook_end, 2)


# ─────────────────────────────────────────────
# FUNCTION 6 — DETECT SCENE CHANGES (For Shorts)
# ─────────────────────────────────────────────

def detect_scene_changes(frames: List[Tuple], threshold: float = 30.0) -> List[float]:
    """
    Detect timestamps where scene changes suddenly.
    High frame difference = scene change = potentially interesting moment.
    
    Returns list of timestamps where scene changes happen.
    These are good candidates for short clips.
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
# FUNCTION 7 — SELECT BEST CLIP SEGMENTS
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
        # No scene changes detected, just split video into chunks
        segments = []
        start = 0.0
        
        while start + clip_length < video_duration and len(segments) < max_clips:
            segments.append((start, start + clip_length))
            start += clip_length
        
        return segments
    
    # Group scene changes into clusters
    # Select top N most active clusters
    segments = []
    used_timestamps = set()
    
    for change_time in scene_changes:
        
        # Don't overlap clips
        too_close = False
        for used in used_timestamps:
            if abs(change_time - used) < clip_length:
                too_close = True
                break
        
        if too_close:
            continue
        
        # Build clip around this scene change
        start = max(0.0, change_time - 5.0)     # Start 5 seconds before
        end = min(video_duration, start + clip_length)
        
        # Adjust start if end is at video boundary
        if end == video_duration:
            start = max(0.0, end - clip_length)
        
        segments.append((round(start, 2), round(end, 2)))
        used_timestamps.add(change_time)
        
        if len(segments) >= max_clips:
            break
    
    return segments


# ─────────────────────────────────────────────
# FUNCTION 8 — TRIM AND CROP CLIP TO VERTICAL
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
    Save to output_path.
    
    Returns output_path if successful.
    """
    
    # Load video
    video = VideoFileClip(video_path)
    
    # Trim the clip
    clip = video.subclip(start, end)
    
    # Get dimensions
    width = clip.w
    height = clip.h
    
    # Calculate crop dimensions for 9:16
    target_aspect = 9 / 16
    current_aspect = width / height
    
    if current_aspect > target_aspect:
        # Video is wider than 9:16, crop width
        new_width = int(height * target_aspect)
        x_center = width // 2
        x1 = x_center - new_width // 2
        x2 = x_center + new_width // 2
        
        clip = clip.crop(x1=x1, y1=0, x2=x2, y2=height)
    
    else:
        # Video is taller than 9:16, crop height
        new_height = int(width / target_aspect)
        y_center = height // 2
        y1 = y_center - new_height // 2
        y2 = y_center + new_height // 2
        
        clip = clip.crop(x1=0, y1=y1, x2=width, y2=y2)
    
    # Resize to standard vertical resolution
    clip = clip.resize((1080, 1920))
    
    # Export
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )
    
    # Clean up
    clip.close()
    video.close()
    
    return output_path