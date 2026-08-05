from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.database import get_db
from features.auth.service import (
    get_google_auth_url,
    exchange_code_for_token,
    save_user_and_tokens
)

router = APIRouter()


@router.get("/login")
def login():
    auth_url = get_google_auth_url()
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback(code: str, db: Session = Depends(get_db)):
    token_data = exchange_code_for_token(code)
    user = save_user_and_tokens(db, token_data)

    return {
        "message": "Authentication successful",
        "user_email": user.email
    }