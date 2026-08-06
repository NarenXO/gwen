from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from features.auth.token_utils import get_latest_token
from features.auth.models import Token
from config.settings import get_settings


settings = get_settings()

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


def fetch_recent_videos(db: Session, page_token=None, limit: int = 5):
    youtube = get_youtube_client(db)

    request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        order="date",
        maxResults=limit,
        pageToken=page_token
    )

    response = request.execute()

    videos = []

    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"]
        })

    next_page_token = response.get("nextPageToken")

    return videos, next_page_token

def fetch_latest_video(db: Session):
    youtube = get_youtube_client(db)

    request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        order="date",
        maxResults=1
    )

    response = request.execute()

    if not response.get("items"):
        return None

    item = response["items"][0]

    return {
        "video_id": item["id"]["videoId"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "published_at": item["snippet"]["publishedAt"]
    }


def fetch_video_details(db: Session, video_id: str):
    youtube = get_youtube_client(db)

    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )

    response = request.execute()

    if not response.get("items"):
        return None

    item = response["items"][0]

    return {
        "video_id": video_id,
        "title": item["snippet"]["title"],
        "views": item["statistics"].get("viewCount", 0),
        "likes": item["statistics"].get("likeCount", 0),
        "comments": item["statistics"].get("commentCount", 0)
    }


def fetch_comments(db: Session, video_id: str):
    youtube = get_youtube_client(db)

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=20
    )

    response = request.execute()

    comments = []

    for item in response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]

        comments.append({
            "comment_id": item["snippet"]["topLevelComment"]["id"],
            "author": comment["authorDisplayName"],
            "text": comment["textDisplay"],
            "like_count": comment["likeCount"],
            "published_at": comment["publishedAt"]
        })

    return comments


def reply_to_comment(db: Session, comment_id: str, text: str):
    youtube = get_youtube_client(db)

    request = youtube.comments().insert(
        part="snippet",
        body={
            "snippet": {
                "parentId": comment_id,
                "textOriginal": text
            }
        }
    )

    response = request.execute()

    return {
        "reply_id": response["id"],
        "text": response["snippet"]["textDisplay"]
    }