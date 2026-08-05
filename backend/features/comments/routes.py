from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from features.youtube.data_service import fetch_comments, reply_to_comment
from pydantic import BaseModel


router = APIRouter()


@router.get("/{video_id}")
def get_comments(video_id: str, db: Session = Depends(get_db)):
    return fetch_comments(db, video_id)


class ReplyRequest(BaseModel):
    comment_id: str
    text: str


@router.post("/reply")
def reply_comment(payload: ReplyRequest, db: Session = Depends(get_db)):
    return reply_to_comment(db, payload.comment_id, payload.text)