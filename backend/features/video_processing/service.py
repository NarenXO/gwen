# service.py
# This is the coordinator.
# It calls all utility functions and puts results together.

import os
import tempfile
import uuid
from typing import List

from .video_utils import (
    extract_frames,
    get_video_resolution,
    get_video_duration,
    detect_static_scenes,
    detect_hook_duration,
    detect_scene_changes,
    select_best_segments,
    trim_and_export_vertical_clip
)

from .audio_utils import (
    extract_audio_from_video,
    detect_silence_segments,
    generate_basic_srt
)

from .thumbnail_utils import (
    calculate_brightness,
    calculate_contrast,
    calculate_sharpness,
    detect_face,
    generate_composition_feedback
)

from .schemas import (
    VideoAnalysisResponse,
    DeadAirSegment,
    StaticSceneSegment,
    ShortsResponse,
    ShortClip,
    ThumbnailAnalysisResponse
)

# Temp folder for processing files
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_files")

# Only create if it doesn't already exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# ─────────────────────────────────────────────
# SERVICE 1 — VIDEO DOCTOR
# ─────────────────────────────────────────────

async def analyze_video(video_path: str) -> VideoAnalysisResponse:
    """
    Full video analysis.
    
    Steps:
    1. Extract frames
    2. Get resolution and duration
    3. Detect static scenes
    4. Detect hook duration
    5. Extract audio and detect silence
    6. Run upload QA checks
    7. Calculate overall score
    8. Return structured result
    """
    
    print(f"[Video Doctor] Starting analysis: {video_path}")
    
    # ── Step 1: Get basic info ──────────────
    resolution = get_video_resolution(video_path)
    duration = get_video_duration(video_path)
    
    print(f"[Video Doctor] Resolution: {resolution}, Duration: {duration}s")
    
    # ── Step 2: Extract frames ──────────────
    print("[Video Doctor] Extracting frames...")
    frames = extract_frames(video_path, interval_seconds=1.0)
    
    # ── Step 3: Detect static scenes ────────
    print("[Video Doctor] Detecting static scenes...")
    raw_static = detect_static_scenes(frames, threshold=10.0)
    
    static_scene_segments = [
        StaticSceneSegment(
            start_time=s["start_time"],
            end_time=s["end_time"],
            duration=s["duration"]
        )
        for s in raw_static
    ]
    
    # ── Step 4: Detect hook duration ────────
    print("[Video Doctor] Analyzing hook...")
    hook_duration = detect_hook_duration(frames)
    
    # ── Step 5: Audio analysis ──────────────
    print("[Video Doctor] Analyzing audio...")
    
    import tempfile
    # Use system temp to avoid OneDrive FFmpeg issues on Windows
    audio_path = os.path.join(
        tempfile.gettempdir(),
        f"{uuid.uuid4()}_audio.wav"
    )
    
    silence_segments = []
    audio_silence_detected = False
    dead_air_segments = []
    
    try:
        extract_audio_from_video(video_path, audio_path)
        raw_silence = detect_silence_segments(audio_path)
        
        audio_silence_detected = len(raw_silence) > 0
        
        dead_air_segments = [
            DeadAirSegment(
                start_time=s["start_time"],
                end_time=s["end_time"],
                duration=s["duration"]
            )
            for s in raw_silence
        ]
        
    except Exception as e:
        print(f"[Video Doctor] Audio analysis failed: {e}")
        audio_silence_detected = False
    
    finally:
        # Clean up audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
    
    # ── Step 6: Upload QA checks ─────────────
    upload_warnings = _run_upload_qa_checks(resolution, duration)
    
    # ── Step 7: Generate recommendations ────
    recommendations = _generate_recommendations(
        hook_duration=hook_duration,
        static_scenes=static_scene_segments,
        dead_air=dead_air_segments,
        resolution=resolution,
        duration=duration
    )
    
    # ── Step 8: Calculate overall score ─────
    overall_score = _calculate_overall_score(
        hook_duration=hook_duration,
        static_scene_count=len(static_scene_segments),
        dead_air_count=len(dead_air_segments),
        resolution=resolution,
        duration=duration
    )
    
    print(f"[Video Doctor] Analysis complete. Score: {overall_score}")
    
    return VideoAnalysisResponse(
        overall_score=overall_score,
        hook_duration=hook_duration,
        dead_air_segments=dead_air_segments,
        static_scene_segments=static_scene_segments,
        audio_silence_detected=audio_silence_detected,
        resolution=resolution,
        duration=duration,
        recommendations=recommendations,
        upload_warnings=upload_warnings
    )


# ─────────────────────────────────────────────
# SERVICE 2 — SHORTS FACTORY
# ─────────────────────────────────────────────

async def generate_shorts(video_path: str) -> ShortsResponse:
    """
    Generate short vertical clips from video.
    
    Steps:
    1. Extract frames
    2. Detect scene changes
    3. Select best segments
    4. Trim and crop each segment to 9:16
    5. Generate subtitle file
    6. Return clip info
    """
    
    print(f"[Shorts Factory] Starting: {video_path}")
    
    # ── Step 1: Extract frames ───────────────
    frames = extract_frames(video_path, interval_seconds=1.0)
    duration = get_video_duration(video_path)
    
    # ── Step 2: Find scene changes ───────────
    scene_changes = detect_scene_changes(frames, threshold=30.0)
    
    # ── Step 3: Select best segments ─────────
    segments = select_best_segments(
        scene_changes=scene_changes,
        video_duration=duration,
        clip_length=30.0,
        max_clips=3
    )
    
    # ── Step 4 & 5: Export each clip ─────────
    clips = []
    
    for i, (start, end) in enumerate(segments):
        
        clip_id = str(uuid.uuid4())[:8]
        clip_filename = f"short_{clip_id}.mp4"
        srt_filename = f"short_{clip_id}.srt"
        
        clip_path = os.path.join(TEMP_DIR, clip_filename)
        srt_path = os.path.join(TEMP_DIR, srt_filename)
        
        print(f"[Shorts Factory] Exporting clip {i+1}: {start}s → {end}s")
        
        try:
            # Export vertical clip
            trim_and_export_vertical_clip(video_path, start, end, clip_path)
            
            # Generate subtitle
            clip_duration = end - start
            generate_basic_srt(None, srt_path, clip_duration)
            
            clips.append(ShortClip(
                start=start,
                end=end,
                file_path=clip_path,
                subtitle_file=srt_path,
                duration=round(end - start, 2)
            ))
            
        except Exception as e:
            print(f"[Shorts Factory] Failed to export clip {i+1}: {e}")
            continue
    
    print(f"[Shorts Factory] Generated {len(clips)} clips")
    
    return ShortsResponse(
        clips=clips,
        total_clips_generated=len(clips)
    )


# ─────────────────────────────────────────────
# SERVICE 3 — THUMBNAIL ANALYZER
# ─────────────────────────────────────────────

async def analyze_thumbnail(image_path: str) -> ThumbnailAnalysisResponse:
    """
    Full thumbnail analysis.
    
    Steps:
    1. Calculate brightness
    2. Calculate contrast
    3. Calculate sharpness
    4. Detect face
    5. Generate feedback and recommendations
    """
    
    print(f"[Thumbnail Analyzer] Analyzing: {image_path}")
    
    # ── Calculate metrics ────────────────────
    brightness = calculate_brightness(image_path)
    contrast = calculate_contrast(image_path)
    sharpness = calculate_sharpness(image_path)
    face_detected = detect_face(image_path)
    
    # ── Generate feedback ────────────────────
    composition_feedback, recommendations = generate_composition_feedback(
        brightness=brightness,
        contrast=contrast,
        sharpness=sharpness,
        face_detected=face_detected
    )
    
    print(f"[Thumbnail Analyzer] Done. Face: {face_detected}, Brightness: {brightness}")
    
    return ThumbnailAnalysisResponse(
        sharpness_score=sharpness,
        brightness_score=brightness,
        contrast_score=contrast,
        face_detected=face_detected,
        composition_feedback=composition_feedback,
        recommendations=recommendations
    )


# ─────────────────────────────────────────────
# HELPER FUNCTIONS (Internal Only)
# ─────────────────────────────────────────────

def _run_upload_qa_checks(resolution: str, duration: float) -> List[str]:
    """Check video quality for upload suitability."""
    
    warnings = []
    
    # Check resolution
    try:
        width, height = map(int, resolution.split("x"))
        if width < 1280 or height < 720:
            warnings.append(f"Resolution {resolution} is below recommended 1280x720")
    except Exception:
        warnings.append("Could not verify resolution")
    
    # Check duration
    if duration < 60:
        warnings.append("Video is under 1 minute - may not perform well algorithmically")
    
    if duration > 3600:
        warnings.append("Video is over 1 hour - consider breaking into parts")
    
    return warnings


def _generate_recommendations(
    hook_duration,
    static_scenes,
    dead_air,
    resolution,
    duration
) -> List[str]:
    """Generate human-readable recommendations."""
    
    recommendations = []
    
    if hook_duration < 10:
        recommendations.append(
            "Hook is very weak (under 10 seconds). "
            "Make the first 15 seconds more dynamic to retain viewers."
        )
    elif hook_duration < 20:
        recommendations.append(
            "Hook is average. Try to make the first 20 seconds more engaging."
        )
    else:
        recommendations.append("Good hook duration - strong opening.")
    
    if len(static_scenes) > 3:
        recommendations.append(
            f"Found {len(static_scenes)} static/boring sections. "
            "Consider cutting or adding b-roll to these sections."
        )
    
    if len(dead_air) > 2:
        recommendations.append(
            f"Found {len(dead_air)} silence segments. "
            "Edit out dead air to improve pacing."
        )
    
    if not recommendations:
        recommendations.append("Video looks well-paced. Good work!")
    
    return recommendations


def _calculate_overall_score(
    hook_duration,
    static_scene_count,
    dead_air_count,
    resolution,
    duration
) -> int:
    """
    Calculate score 0-100 based on video quality factors.
    """
    
    score = 100
    
    # Penalize weak hook
    if hook_duration < 10:
        score -= 20
    elif hook_duration < 20:
        score -= 10
    
    # Penalize static scenes
    score -= min(static_scene_count * 5, 25)
    
    # Penalize dead air
    score -= min(dead_air_count * 5, 20)
    
    # Penalize low resolution
    try:
        width, height = map(int, resolution.split("x"))
        if width < 1280:
            score -= 10
    except Exception:
        score -= 5
    
    # Keep score in valid range
    score = max(0, min(100, score))
    
    return score