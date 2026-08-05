from fastapi import APIRouter

from .schemas import AIRequest, AIResponse
from .service import route_action

router = APIRouter()


@router.post("/action", response_model=AIResponse)
def ai_action(request: AIRequest):

    result = route_action(request.message)

    return AIResponse(
        reply=f"Detected intent: {result['intent']}",
        action=result["intent"],
        data={}
    )