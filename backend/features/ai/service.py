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