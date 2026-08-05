from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from features.auth.token_utils import get_latest_token


def get_analytics_client(db: Session):
    access_token = get_latest_token(db)

    credentials = Credentials(token=access_token)

    analytics = build(
        "youtubeAnalytics",
        "v2",
        credentials=credentials,
        cache_discovery=False
    )

    return analytics


def get_channel_summary(db: Session):
    analytics = get_analytics_client(db)

    request = analytics.reports().query(
        ids="channel==MINE",
        startDate="2024-01-01",
        endDate="2025-12-31",
        metrics="views,estimatedMinutesWatched,averageViewDuration"
    )

    response = request.execute()

    return response