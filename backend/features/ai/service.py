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

from features.ai.intelligence import (
    classify_intent,
    build_performance_prompt,
    build_comment_prompt,
    build_video_analysis_prompt,
    build_creator_twin_prompt,
    build_content_strategy_prompt
)

# ✅ Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# =====================================================
# ✅ SAFE GEMINI CALL
# =====================================================
def call_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
           model="models/gemini-3.5-flash",
            contents=prompt,
        )

        if hasattr(response, "text") and response.text:
            return response.text

        return response.candidates[0].content.parts[0].text

    except Exception as e:
        print("Gemini Error:", e)   # 👈 ADD THIS
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
from features.ai.intelligence import (
    classify_intent,
    build_performance_prompt,
    build_comment_prompt,
    build_video_analysis_prompt,
    build_creator_twin_prompt,
    build_content_strategy_prompt
)


def handle_ai_action(db: Session, message: str):

    intent = classify_intent(message)

    # =====================================================
    # ✅ ANALYTICS SUMMARY
    # =====================================================
    if intent == "analytics_summary":

        analytics = get_channel_summary(db)

        if not analytics.get("rows"):
            return {
                "reply": "No analytics data available yet.",
                "action": intent,
                "data": None
            }

        row = analytics["rows"][0]
        views = row[0]
        watch_time = row[1]
        avg_duration = row[2]

        health = compute_channel_health(views, watch_time, avg_duration)

        latest_video = fetch_latest_video(db)
        video_details = None

        if latest_video:
            video_details = fetch_video_details(db, latest_video["video_id"])

        prompt = build_performance_prompt(
            views,
            watch_time,
            avg_duration,
            health,
            latest_video["title"] if latest_video else "N/A",
            video_details["views"] if video_details else "N/A",
            video_details["likes"] if video_details else "N/A",
            video_details["comments"] if video_details else "N/A"
        )

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": intent,
            "data": {
                "views": views,
                "watch_time_minutes": watch_time,
                "avg_view_duration_seconds": avg_duration,
                "health": health
            }
        }

    # =====================================================
    # ✅ COMMENT ANALYSIS
    # =====================================================
    if intent == "comment_analysis":

        selected_video = None
        comments = None
        page_token = None

        max_checks = 20
        checked = 0

        while checked < max_checks:
            videos, page_token = fetch_recent_videos(
                db,
                page_token=page_token,
                limit=5
            )

            if not videos:
                break

            for video in videos:
                checked += 1
                try:
                    fetched_comments = fetch_comments(db, video["video_id"])
                    if fetched_comments:
                        selected_video = video
                        comments = fetched_comments
                        break
                except Exception:
                    continue

            if selected_video or not page_token:
                break

        if not selected_video:
            return {
                "reply": "No videos with enabled comments found.",
                "action": intent,
                "data": None
            }

        prompt = build_comment_prompt(
            selected_video["title"],
            comments
        )

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": intent,
            "data": {
                "video_analyzed": selected_video,
                "comments_count": len(comments)
            }
        }

    # =====================================================
    # ✅ VIDEO ANALYSIS
    # =====================================================
    if intent == "video_analysis":

        video = fetch_latest_video(db)

        if not video:
            return {
                "reply": "No videos found.",
                "action": intent,
                "data": None
            }

        details = fetch_video_details(db, video["video_id"])

        prompt = build_video_analysis_prompt(
            details["title"],
            details["views"],
            details["likes"],
            details["comments"]
        )

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": intent,
            "data": details
        }

    # =====================================================
    # ✅ CREATOR TWIN
    # =====================================================
    if intent == "creator_twin":

        # Placeholder for now — you can wire recent titles/descriptions later
        prompt = build_creator_twin_prompt([], [])

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": intent,
            "data": None
        }

    # =====================================================
    # ✅ CONTENT STRATEGY
    # =====================================================
    if intent == "content_strategy":

        analytics = get_channel_summary(db)
        recent = fetch_recent_videos(db)[0]

        prompt = build_content_strategy_prompt(
            analytics,
            recent
        )

        reply = call_gemini(prompt)

        return {
            "reply": reply,
            "action": intent,
            "data": None
        }

    # =====================================================
    # ✅ DEFAULT
    # =====================================================
    reply = call_gemini(
        f"You are a professional YouTube strategist. Answer concisely: {message}"
    )

    return {
        "reply": reply,
        "action": intent,
        "data": None
    }
    # =====================================================
    # ✅ COMMENT ANALYSIS
    # =====================================================
    if intent == "comment_analysis":

        selected_video = None
        comments = None
        page_token = None

        while True:
            videos, page_token = fetch_recent_videos(
                db,
                page_token=page_token,
                limit=5
            )

            if not videos:
                break

            for video in videos:
                try:
                    fetched_comments = fetch_comments(db, video["video_id"])
                    if fetched_comments:
                        selected_video = video
                        comments = fetched_comments
                        break
                except Exception:
                    continue

            if selected_video or not page_token:
                break

        if not selected_video:
            return {
                "reply": "No videos with enabled comments found.",
                "action": None,
                "data": None
            }

        prompt = build_comment_prompt(
            selected_video["title"],
            comments
        )

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
    # ✅ VIDEO ANALYSIS
    # =====================================================
    if intent == "video_analysis":

        video = fetch_latest_video(db)

        if not video:
            return {
                "reply": "No videos found.",
                "action": None,
                "data": None
            }

        details = fetch_video_details(db, video["video_id"])

        prompt = build_video_analysis_prompt(
            details["title"],
            details["views"],
            details["likes"],
            details["comments"]
        )

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