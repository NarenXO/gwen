from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from features.ai.schemas import AIRequest, AIResponse
from features.ai.service import handle_ai_action

router = APIRouter()


@router.post("/action", response_model=AIResponse)
def ai_action(payload: AIRequest, db: Session = Depends(get_db)):
    return handle_ai_action(db, payload.message)
