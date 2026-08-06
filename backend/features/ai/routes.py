<<<<<<< HEAD
from fastapi import APIRouter

from .schemas import AIRequest, AIResponse
from .service import route_action
=======
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from features.ai.service import handle_ai_action
>>>>>>> main

router = APIRouter()


<<<<<<< HEAD
@router.post("/action", response_model=AIResponse)
def ai_action(request: AIRequest):

    result = route_action(request.message)

    return AIResponse(
        reply=f"Detected intent: {result['intent']}",
        action=result["intent"],
        data={}
    )
=======
class AIRequest(BaseModel):
    message: str


@router.post("/action")
def ai_action(payload: AIRequest, db: Session = Depends(get_db)):
    return handle_ai_action(db, payload.message)
>>>>>>> main
