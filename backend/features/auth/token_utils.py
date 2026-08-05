import requests
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from config.settings import get_settings
from features.auth.models import Token

settings = get_settings()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def get_latest_token(db: Session):
    token = db.query(Token).order_by(Token.created_at.desc()).first()

    if not token:
        raise Exception("No token found. Please authenticate first.")

    # ✅ Normalize expiry to UTC safely
    expiry_time = token.expiry

    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)

    # If token expired → refresh
    if expiry_time < current_time:
        refreshed = refresh_access_token(token.refresh_token)

        token.access_token = refreshed["access_token"]
        token.expiry = current_time + timedelta(
            seconds=refreshed["expires_in"]
        )

        db.commit()

    return token.access_token


def refresh_access_token(refresh_token: str):
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()