from datetime import datetime, timezone
from sqlalchemy.orm import Session

from features.auth.models import Token


def get_latest_token(db: Session):
    token = db.query(Token).order_by(Token.created_at.desc()).first()

    if not token:
        raise Exception("No token found. Please login.")

    expiry_time = token.expiry

    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)

    # ✅ If expired → force re-login
    if expiry_time < current_time:
        raise Exception("Session expired. Please login again.")

    return token.access_token