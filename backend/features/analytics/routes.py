from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from features.youtube.analytics_service import get_channel_summary

router = APIRouter()


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    data = get_channel_summary(db)

    if not data.get("rows"):
        return {
            "views": 0,
            "watch_time_minutes": 0,
            "average_view_duration_seconds": 0
        }

    row = data["rows"][0]

    return {
        "views": row[0],
        "watch_time_minutes": row[1],
        "average_view_duration_seconds": row[2]
    }