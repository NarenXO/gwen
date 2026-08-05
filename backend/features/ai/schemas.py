from typing import Optional, Dict, Any
from pydantic import BaseModel


class AIRequest(BaseModel):
    message: str


class AIResponse(BaseModel):
    reply: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None