# schemas.py
# These define what data looks like coming IN and going OUT

from pydantic import BaseModel
from typing import List, Optional


# ─────────────────────────────────────────────
# VIDEO DOCTOR SCHEMAS
# ─────────────────────────────────────────────

class DeadAirSegment(BaseModel):
    start_time: float      # seconds
    end_time: float        # seconds
    duration: float        # seconds


class StaticSceneSegment(BaseModel):
    start_time: float
    end_time: float
    duration: float


class VideoAnalysisResponse(BaseModel):
    overall_score: int                              # 0-100
    hook_duration: float                            # seconds
    dead_air_segments: List[DeadAirSegment]
    static_scene_segments: List[StaticSceneSegment]
    audio_silence_detected: bool
    resolution: str                                 # "1920x1080"
    duration: float                                 # total seconds
    recommendations: List[str]
    upload_warnings: List[str]                      # QA checks


# ─────────────────────────────────────────────
# SHORTS FACTORY SCHEMAS
# ─────────────────────────────────────────────

class ShortClip(BaseModel):
    start: float           # seconds
    end: float             # seconds
    file_path: str         # where the clip is saved
    subtitle_file: str     # where the SRT file is saved
    duration: float        # clip length


class ShortsResponse(BaseModel):
    clips: List[ShortClip]
    total_clips_generated: int


# ─────────────────────────────────────────────
# THUMBNAIL ANALYZER SCHEMAS
# ─────────────────────────────────────────────

class ThumbnailAnalysisResponse(BaseModel):
    sharpness_score: float      # 0.0 - 1.0
    brightness_score: float     # 0.0 - 1.0
    contrast_score: float       # 0.0 - 1.0
    face_detected: bool
    composition_feedback: str
    recommendations: List[str]# schemas.py
# These define what data looks like coming IN and going OUT

from pydantic import BaseModel
from typing import List, Optional


# ─────────────────────────────────────────────
# VIDEO DOCTOR SCHEMAS
# ─────────────────────────────────────────────

class DeadAirSegment(BaseModel):
    start_time: float      # seconds
    end_time: float        # seconds
    duration: float        # seconds


class StaticSceneSegment(BaseModel):
    start_time: float
    end_time: float
    duration: float


class VideoAnalysisResponse(BaseModel):
    overall_score: int                              # 0-100
    hook_duration: float                            # seconds
    dead_air_segments: List[DeadAirSegment]
    static_scene_segments: List[StaticSceneSegment]
    audio_silence_detected: bool
    resolution: str                                 # "1920x1080"
    duration: float                                 # total seconds
    recommendations: List[str]
    upload_warnings: List[str]                      # QA checks


# ─────────────────────────────────────────────
# SHORTS FACTORY SCHEMAS
# ─────────────────────────────────────────────

class ShortClip(BaseModel):
    start: float           # seconds
    end: float             # seconds
    file_path: str         # where the clip is saved
    subtitle_file: str     # where the SRT file is saved
    duration: float        # clip length


class ShortsResponse(BaseModel):
    clips: List[ShortClip]
    total_clips_generated: int


# ─────────────────────────────────────────────
# THUMBNAIL ANALYZER SCHEMAS
# ─────────────────────────────────────────────

class ThumbnailAnalysisResponse(BaseModel):
    sharpness_score: float      # 0.0 - 1.0
    brightness_score: float     # 0.0 - 1.0
    contrast_score: float       # 0.0 - 1.0
    face_detected: bool
    composition_feedback: str
    recommendations: List[str]