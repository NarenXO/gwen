<<<<<<< HEAD
from typing import Dict


def route_action(message: str) -> Dict:
    """
    Determines which AI module should handle the user's request.
    """

    text = message.lower()

    if "analytics" in text or "performance" in text:
        return {"intent": "analytics_summary"}

    elif "idea" in text or "content" in text:
        return {"intent": "content_strategy"}

    elif "comment" in text:
        return {"intent": "analyze_comments"}

    elif "thumbnail" in text:
        return {"intent": "analyze_thumbnail"}

    elif "video" in text:
        return {"intent": "video_analyze"}

    elif "title" in text or "description" in text:
        return {"intent": "creator_twin"}

    elif "schedule" in text:
        return {"intent": "schedule_upload"}

    return {"intent": "unknown"}
=======
import os
from google import genai
from sqlalchemy.orm import Session

from features.youtube.analytics_service import get_channel_summary
from features.youtube.data_service import (
    fetch_latest_video,
    fetch_video_details,
    fetch_comments,
    fetch_recent_videos
)

# ✅ Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# =====================================================
# ✅ SAFE GEMINI CALL
# =====================================================
def call_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt,
        )

        if hasattr(response, "text") and response.text:
            return response.text

        return response.candidates[0].content.parts[0].text

    except Exception:
        return "AI analysis temporarily unavailable."


# =====================================================
# ✅ SIMPLE HEURISTIC CHANNEL HEALTH SCORE
# =====================================================
def compute_channel_health(views, watch_time, avg_duration):
    if views == 0:
        return "Early Stage"
    if avg_duration > 240:
        return "Strong Retention"
    if watch_time > 1000:
        return "Growing Momentum"
    return "Needs Optimization"


# =====================================================
# ✅ MAIN AI ROUTER
# =====================================================
def handle_ai_action(db: Session, message: str):
    message_lower = message.lower()

    # =====================================================
    # ✅ CHANNEL PERFORMANCE ANALYSIS
    # =====================================================
    if "performance" in message_lower or "analytics" in message_lower:

        analytics = get_channel_summary(db)
        latest_video = fetch_latest_video(db)

        if not analytics.get("rows"):
            return {
                "reply": "No analytics data available yet.",
                "action": None,
                "data": None
            }

        row = analytics["rows"][0]
        views = row[0]
        watch_time = row[1]
        avg_duration = row[2]

        health = compute_channel_health(views, watch_time, avg_duration)

        video_details = None
        if latest_video:
            video_details = fetch_video_details(db, latest_video["video_id"])

        # ✅ Strict zero-data handling
        if views == 0:
            return {
                "reply": f"""📊 Performance Snapshot:
- Channel Status: {health}
- No measurable performance data yet.

🎯 Action:
- Publish consistently.
- Improve discoverability with SEO titles and thumbnails.""",
                "action": None,
                "data": {
                    "views": views,
                    "watch_time_minutes": watch_time,
                    "avg_view_duration_seconds": avg_duration,
                    "health": health
                }
            }

        prompt = f"""
You are a senior YouTube growth strategist.

STRICT RULES:
- Use ONLY numbers provided.
- Do NOT invent percentages.
- Keep response under 130 words.
- Be concise and strategic.

CHANNEL METRICS:
Views: {views}
Watch Time (minutes): {watch_time}
Average View Duration (seconds): {avg_duration}
Channel Health: {health}

LATEST VIDEO:
Title: {latest_video['title'] if latest_video else 'N/A'}
Views: {video_details['views'] if video_details else 'N/A'}
Likes: {video_details['likes'] if video_details else 'N/A'}
Comments: {video_details['comments'] if video_details else 'N/A'}

Output format:

📊 Performance Snapshot:
- Key insight
- Strength
- Weakness

📈 Growth Insight:
- What limits growth

🎯 Action:
- 1 improvement
- 1 strategic move
"""

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": None,
            "data": {
                "views": views,
                "watch_time_minutes": watch_time,
                "avg_view_duration_seconds": avg_duration,
                "health": health,
                "latest_video": latest_video
            }
        }

      # =====================================================
    # ✅ SMART COMMENT ANALYSIS WITH PAGINATION
    # =====================================================
    if "comments" in message_lower:

        selected_video = None
        comments = None

        page_token = None
        checked_videos = 0
        max_videos_to_check = 50

        while checked_videos < max_videos_to_check:

            videos, page_token = fetch_recent_videos(
                db,
                page_token=page_token,
                limit=5
            )

            if not videos:
                break

            for video in videos:
                checked_videos += 1

                try:
                    fetched_comments = fetch_comments(db, video["video_id"])

                    if fetched_comments:
                        selected_video = video
                        comments = fetched_comments
                        break

                except Exception:
                    continue

            if selected_video:
                break

            if not page_token:
                break

        if not selected_video:
            return {
                "reply": "No videos with enabled comments found on this channel.",
                "action": None,
                "data": None
            }

        prompt = f"""
You are a YouTube audience analyst.

Analyze comments for video:
Title: {selected_video['title']}

Be concise and strategic.

COMMENTS:
{comments}

Output format:

💬 Audience Mood:
- Overall sentiment

🔥 Patterns:
- Recurring themes

🎯 Recommendation:
- 1 engagement strategy
"""

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": None,
            "data": {
                "video_analyzed": selected_video,
                "comments_count": len(comments)
            }
        }
    # =====================================================
    # ✅ LATEST VIDEO QUICK ANALYSIS
    # =====================================================
    if "latest video" in message_lower:

        video = fetch_latest_video(db)

        if not video:
            return {
                "reply": "No videos found.",
                "action": None,
                "data": None
            }

        details = fetch_video_details(db, video["video_id"])

        prompt = f"""
You are a YouTube growth advisor.

Analyze briefly.
Be concise and strategic.

Title: {details['title']}
Views: {details['views']}
Likes: {details['likes']}
Comments: {details['comments']}

Output:

📊 Quick Insight:
- Strength
- Weakness

🎯 Improvement:
- 1 actionable fix
"""

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": "show_video",
            "data": details
        }

    # =====================================================
    # ✅ DEFAULT
    # =====================================================
    reply = call_gemini(
        f"You are a professional YouTube strategist. Answer concisely: {message}"
    )

    return {
        "reply": reply,
        "action": None,
        "data": None
    }
>>>>>>> main
