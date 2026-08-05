from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from features.auth.token_utils import get_latest_token


def get_youtube_client(db: Session):
    access_token = get_latest_token(db)

    credentials = Credentials(token=access_token)

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials,
        cache_discovery=False
    )

    return youtube


def get_channel_info(db: Session):
    youtube = get_youtube_client(db)

    request = youtube.channels().list(
        part="snippet,statistics",
        mine=True
    )

    response = request.execute()

    return response


def get_latest_video(db: Session):
    youtube = get_youtube_client(db)

    request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        order="date",
        maxResults=1
    )

    response = request.execute()

    return response