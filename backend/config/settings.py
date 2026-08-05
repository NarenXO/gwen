import os
from dotenv import load_dotenv
from functools import lru_cache

# Load .env file
load_dotenv()


class Settings:
    # App Settings
    PROJECT_NAME: str = "GWEN Backend"
    API_V1_STR: str = "/api"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8000/auth/callback"
    )

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/gwen"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")


@lru_cache()
def get_settings():
    return Settings()