from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from features.youtube.analytics_service import get_channel_summary

router = APIRouter()


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    return get_channel_summary(db)