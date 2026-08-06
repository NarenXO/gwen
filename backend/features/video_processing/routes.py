# routes.py
# API endpoints that frontend/backend calls

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
import os
import uuid
import shutil

from .service import analyze_video, generate_shorts, analyze_thumbnail
from .schemas import VideoAnalysisResponse, ShortsResponse, ThumbnailAnalysisResponse

# Create router
router = APIRouter(prefix="/video", tags=["Video Processing"])
thumbnail_router = APIRouter(prefix="/thumbnail", tags=["Thumbnail"])

# Temp directory for uploaded files
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_files")

# Only create if it doesn't already exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# ─────────────────────────────────────────────
# ENDPOINT 1 — VIDEO DOCTOR
# ─────────────────────────────────────────────

@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video_endpoint(video: UploadFile = File(...)):
    """
    Upload a video file.
    Returns full analysis: score, hook, static scenes, silence, recommendations.
    """

    if not video.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Upload MP4, MOV, AVI, or MKV."
        )

    file_id = str(uuid.uuid4())
    video_path = os.path.join(TEMP_DIR, f"{file_id}_{video.filename}")

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Run analysis in threadpool (non-blocking)
        result = await run_in_threadpool(analyze_video, video_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Clean up uploaded file
        if os.path.exists(video_path):
            os.remove(video_path)


# ─────────────────────────────────────────────
# ENDPOINT 2 — SHORTS FACTORY
# ─────────────────────────────────────────────

@router.post("/generate-shorts", response_model=ShortsResponse)
async def generate_shorts_endpoint(video: UploadFile = File(...)):
    """
    Upload a video file.
    Detects most engaging segments.
    Exports vertical 9:16 clips with blurred background for landscape videos.
    Returns clip info with file paths and subtitle files.
    """

    if not video.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Upload MP4, MOV, AVI, or MKV."
        )

    file_id = str(uuid.uuid4())
    video_path = os.path.join(TEMP_DIR, f"{file_id}_{video.filename}")

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Run shorts generation in threadpool (non-blocking)
        result = await run_in_threadpool(generate_shorts, video_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shorts generation failed: {str(e)}")

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


# ─────────────────────────────────────────────
# ENDPOINT 3 — THUMBNAIL ANALYZER
# ─────────────────────────────────────────────

@thumbnail_router.post("/analyze", response_model=ThumbnailAnalysisResponse)
async def analyze_thumbnail_endpoint(image: UploadFile = File(...)):
    """
    Upload a thumbnail image.
    Returns scores for brightness, contrast, sharpness, face detection.
    """

    if not image.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Upload JPG, PNG, or WEBP."
        )

    file_id = str(uuid.uuid4())
    image_path = os.path.join(TEMP_DIR, f"{file_id}_{image.filename}")

    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Run thumbnail analysis in threadpool (non-blocking)
        result = await run_in_threadpool(analyze_thumbnail, image_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail analysis failed: {str(e)}")

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


# ─────────────────────────────────────────────
# ENDPOINT 4 — DOWNLOAD CLIP
# ─────────────────────────────────────────────

@router.get("/download/{filename}")
async def download_clip(filename: str):
    """
    Download a generated short clip or subtitle file by filename.
    Use the file_path or subtitle_file returned from /generate-shorts.
    """

    # Security check — prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = os.path.join(TEMP_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found. It may have been cleaned up already."
        )

    # Determine media type
    if filename.endswith(".mp4"):
        media_type = "video/mp4"
    elif filename.endswith(".srt"):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename
    ) 