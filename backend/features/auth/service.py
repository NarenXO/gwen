import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from sqlalchemy.orm import Session

from config.settings import get_settings
from features.auth.models import User, Token

settings = get_settings()


GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_auth_url():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/yt-analytics.readonly",
        "access_type": "offline",
        "prompt": "consent"
    }

    request = requests.Request("GET", GOOGLE_AUTH_BASE, params=params).prepare()
    return request.url


def exchange_code_for_token(code: str):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()


def get_google_user_info(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    response.raise_for_status()
    return response.json()


def save_user_and_tokens(db: Session, token_data: dict):
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data["expires_in"]

    expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)

    user_info = get_google_user_info(access_token)

    google_id = user_info["id"]
    email = user_info["email"]
    name = user_info.get("name")
    picture = user_info.get("picture")

    user = db.query(User).filter(User.google_id == google_id).first()

    if not user:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            profile_picture=picture
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = Token(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expiry=expiry_time
    )

    db.add(token)
    db.commit()

    return user