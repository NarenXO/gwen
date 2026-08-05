from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from features.youtube.data_service import (
    fetch_latest_video,
    fetch_video_details
)

router = APIRouter()


@router.get("/latest")
def latest_video(db: Session = Depends(get_db)):
    video = fetch_latest_video(db)
    if not video:
        return {"message": "No videos found"}
    return video


@router.get("/{video_id}")
def video_details(video_id: str, db: Session = Depends(get_db)):
    video = fetch_video_details(db, video_id)
    if not video:
        return {"message": "Video not found"}
    return video