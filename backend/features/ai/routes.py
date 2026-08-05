from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from features.ai.service import handle_ai_action

router = APIRouter()


class AIRequest(BaseModel):
    message: str


@router.post("/action")
def ai_action(payload: AIRequest, db: Session = Depends(get_db)):
    return handle_ai_action(db, payload.message)