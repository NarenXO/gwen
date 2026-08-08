"""GWEN AI Intelligence Engine.

This module provides pure business logic for the GWEN YouTube Creator Assistant.
It handles intent classification, prompt engineering for Gemini, AI reasoning
helpers, and response formatting helpers without any side effects or external API calls.

Role of intelligence.py:
1. Intent detection from natural language creator messages
2. Prompt engineering tailored for channel analytics, comments, video analysis,
   creator style, and content strategy
3. Pure AI reasoning and formatting helpers
"""

import re
from typing import Any, Dict, List, Optional, Union

# ====================================================
# INTENT CONSTANTS
# ====================================================
INTENT_ANALYTICS_SUMMARY = "analytics_summary"
INTENT_VIDEO_ANALYSIS = "video_analysis"
INTENT_COMMENT_ANALYSIS = "comment_analysis"
INTENT_CONTENT_STRATEGY = "content_strategy"
INTENT_CREATOR_TWIN = "creator_twin"
INTENT_GENERAL_CHAT = "general_chat"

ALL_INTENTS = [
    INTENT_ANALYTICS_SUMMARY,
    INTENT_VIDEO_ANALYSIS,
    INTENT_COMMENT_ANALYSIS,
    INTENT_CONTENT_STRATEGY,
    INTENT_CREATOR_TWIN,
    INTENT_GENERAL_CHAT,
]


# ====================================================
# 1. INTENT DETECTION
# ====================================================
def classify_intent(message: str) -> str:
    """Classify a user's natural language request into a supported GWEN intent.

    Analyzes intent based on natural phrases, intent keyphrase matching,
    and keyword cluster patterns.

    Args:
        message (str): The raw input query from the YouTube creator.

    Returns:
        str: The identified intent identifier string.

    Examples:
        >>> classify_intent("Analyze my channel")
        'analytics_summary'
        >>> classify_intent("How is my performance?")
        'analytics_summary'
        >>> classify_intent("Review my newest upload")
        'video_analysis'
        >>> classify_intent("Analyze latest video")
        'video_analysis'
        >>> classify_intent("What are viewers saying?")
        'comment_analysis'
        >>> classify_intent("Analyze comments")
        'comment_analysis'
        >>> classify_intent("Give me new content ideas")
        'content_strategy'
        >>> classify_intent("What should I upload?")
        'content_strategy'
        >>> classify_intent("Generate title")
        'creator_twin'
        >>> classify_intent("Write description")
        'creator_twin'
    """
    if not message or not isinstance(message, str):
        return INTENT_GENERAL_CHAT

    text = message.lower().strip()

    # Rule-based exact phrase pattern mappings
    phrase_rules = [
        (
            INTENT_ANALYTICS_SUMMARY,
            [
                "analyze my channel",
                "analyze channel",
                "channel analysis",
                "channel health",
                "channel summary",
                "channel stats",
                "channel performance",
                "how is my performance",
                "how's my performance",
                "my performance",
                "channel metrics",
                "channel overview",
                "overall performance",
                "performance summary",
                "channel status",
                "performance snapshot",
                "how is my channel",
                "how's my channel",
                "how am i doing",
                "channel growth",
                "channel analytics",
                "show me my channel analytics",
                "show my channel analytics",
                "show me analytics",
                "my analytics",
                "how are my views doing",
                "how are my views",
                "how are views doing",
                "my views doing",
                "my views",
                "channel views",
                "views performance",
                "views stat",
                "views stats",
            ],
        ),
        (
            INTENT_VIDEO_ANALYSIS,
            [
                "review my newest upload",
                "review newest upload",
                "review latest video",
                "review newest video",
                "analyze latest video",
                "analyze newest upload",
                "analyze newest video",
                "analyze video",
                "video analysis",
                "video performance",
                "last video",
                "newest upload",
                "latest upload",
                "review video",
                "latest video performance",
                "analyze my video",
                "review my video",
                "video review",
                "how did my last video do",
                "how did my recent video perform",
                "what is wrong with my latest video",
                "what's wrong with my latest video",
                "what is wrong with my video",
            ],
        ),
        (
            INTENT_CREATOR_TWIN,
            [
                "how should i respond to my audience",
                "how should i respond",
                "respond to my audience",
                "respond to audience",
                "help me reply to my viewers",
                "help me reply",
                "reply to my viewers",
                "reply to viewers",
                "reply to my audience",
                "reply to audience",
                "respond to viewers",
                "respond to my viewers",
                "how to respond",
                "how to reply",
                "help me respond",
                "write reply",
                "draft reply",
                "generate reply",
                "reply to comments",
                "respond to comments",
                "generate title",
                "write description",
                "generate description",
                "write title",
                "create title",
                "creator twin",
                "generate tags",
                "craft title",
                "suggest title",
                "write tags",
                "title and description",
                "create description",
                "title generator",
                "description generator",
                "write a thumbnail text",
            ],
        ),
        (
            INTENT_COMMENT_ANALYSIS,
            [
                "what are viewers saying",
                "viewers saying",
                "comment analysis",
                "analyze comments",
                "review comments",
                "audience feedback",
                "comment sentiment",
                "viewer feedback",
                "what do comments say",
                "what are people saying",
                "read comments",
                "comments feedback",
                "audience sentiment",
            ],
        ),
        (
            INTENT_CONTENT_STRATEGY,
            [
                "give me new content ideas",
                "new content ideas",
                "content ideas",
                "what should i upload",
                "video ideas",
                "content strategy",
                "ideas for video",
                "give me video ideas",
                "what to upload",
                "suggest video ideas",
                "next video ideas",
                "content roadmap",
                "future video ideas",
                "topics to cover",
                "what video should i make",
                "what videos should i make",
                "what videos should i make next",
                "what video should i make next",
                "videos to make next",
                "content plan",
                "give me a content plan",
                "give me content plan",
                "videos to make",
                "what to make next",
            ],
        ),
    ]

    # Pass 1: Direct keyphrase / substring match
    for intent, phrases in phrase_rules:
        for phrase in phrases:
            if phrase in text:
                return intent

    # Pass 2: Keyword combinations for natural variation

    # 1. Creator Twin / Reply intent precedence over generic comment analysis
    if any(k in text for k in ["reply", "respond", "response"]) and any(
        k in text for k in ["viewer", "viewers", "audience", "comment", "comments", "people", "fan", "fans", "subscriber", "subscribers"]
    ):
        return INTENT_CREATOR_TWIN

    # 2. Analytics Summary
    if any(k in text for k in ["channel", "performance", "analytics", "stats", "health", "view", "views", "metrics"]) and any(
        k in text for k in ["analyze", "how", "check", "summary", "report", "overall", "doing", "show", "get", "see"]
    ):
        return INTENT_ANALYTICS_SUMMARY

    # 3. Video Analysis
    if any(k in text for k in ["video", "upload"]) and any(
        k in text for k in ["analyze", "review", "newest", "latest", "recent", "last", "performance", "wrong"]
    ):
        return INTENT_VIDEO_ANALYSIS

    # 4. Comment Analysis
    if any(k in text for k in ["comment", "comments", "viewer", "viewers", "audience", "feedback"]):
        return INTENT_COMMENT_ANALYSIS

    # 5. Content Strategy
    if (
        any(k in text for k in ["idea", "ideas", "upload", "strategy", "topic", "topics", "plan", "roadmap"])
        and any(k in text for k in ["content", "what", "next", "give", "suggest", "future", "new", "make"])
    ) or (
        "videos" in text and any(k in text for k in ["make next", "should i make", "to make"])
    ):
        return INTENT_CONTENT_STRATEGY

    # 6. Creator Twin (Title / Description / Tags)
    if any(k in text for k in ["title", "description", "tag", "tags"]) and any(
        k in text for k in ["generate", "write", "create", "make", "draft", "suggest", "craft"]
    ):
        return INTENT_CREATOR_TWIN

    return INTENT_GENERAL_CHAT


# ====================================================
# 2. BUILD PERFORMANCE PROMPT
# ====================================================
def build_performance_prompt(
    views: Union[int, float, str],
    watch_time_minutes: Union[int, float, str],
    average_view_duration_seconds: Union[int, float, str],
    channel_health: str,
    latest_video_title: str,
    latest_video_views: Union[int, float, str],
    latest_video_likes: Union[int, float, str],
    latest_video_comments: Union[int, float, str],
) -> str:
    """Build a system prompt for analyzing overall channel performance.

    Instructs Gemini to strictly use only provided numbers without inventing
    or fabricating metrics, outputting in a concise 3-section format.

    Args:
        views: Total channel views.
        watch_time_minutes: Total watch time in minutes.
        average_view_duration_seconds: Average view duration in seconds.
        channel_health: Qualitative channel health indicator.
        latest_video_title: Title of the newest video.
        latest_video_views: View count of the newest video.
        latest_video_likes: Like count of the newest video.
        latest_video_comments: Comment count of the newest video.

    Returns:
        str: Formatted prompt string for Gemini API.
    """
    return f"""You are GWEN, an expert AI YouTube Creator Assistant.

Analyze the following channel metrics and latest video performance data:

--- CHANNEL OVERALL STATS ---
- Total Views: {views}
- Watch Time (minutes): {watch_time_minutes}
- Average View Duration (seconds): {average_view_duration_seconds}
- Channel Health: {channel_health}

--- LATEST VIDEO PERFORMANCE ---
- Title: "{latest_video_title}"
- Views: {latest_video_views}
- Likes: {latest_video_likes}
- Comments: {latest_video_comments}

--- CRITICAL CONSTRAINTS ---
1. Use ONLY the provided numbers and metrics above.
2. NEVER invent statistics, fabricate percentages, or assume unprovided metrics.
3. Keep the answer concise and direct.

--- REQUIRED OUTPUT FORMAT ---
Please structure your response strictly with these exact section headers:

📊 Performance Snapshot
(Concise summary of overall channel and latest video performance based strictly on the stats.)

📈 Growth Insight
(Actionable analysis of watch time, retention, and audience engagement trends.)

🎯 Action Plan
(3 practical, high-impact steps the creator should execute next.)"""


# ====================================================
# 3. BUILD COMMENT PROMPT
# ====================================================
def build_comment_prompt(
    video_title: str,
    comments: Union[List[str], List[Dict[str, Any]]],
) -> str:
    """Build a prompt for analyzing audience sentiment and feedback in video comments.

    Args:
        video_title (str): Title of the video being analyzed.
        comments (Union[List[str], List[Dict[str, Any]]]): Raw comments text list or comment dict objects.

    Returns:
        str: Formatted prompt string for Gemini API.
    """
    formatted_comments = _format_comment_list(comments)

    return f"""You are GWEN, an expert AI YouTube Creator Assistant.

Analyze the audience comments for the video titled: "{video_title}"

--- COMMENTS DATA ---
{formatted_comments}

--- ANALYSIS REQUIREMENTS ---
Please examine the audience feedback and provide a structured analysis covering:

1. Audience Mood: Describe the dominant emotional tone and sentiment of viewers.
2. Recurring Themes: Highlight key topics or ideas mentioned repeatedly by multiple viewers.
3. Positive Feedback: Summarize specific elements or moments viewers appreciated.
4. Criticism: Identify any complaints, constructive criticism, or technical issues raised.
5. Questions: List common or notable questions asked by the audience.
6. Suggested Creator Action: Provide EXACTLY ONE clear, actionable step for the creator (e.g. pinned comment, follow-up topic, or community post).

Keep the analysis insightful, concise, and focused on helping the creator engage their audience effectively."""


# ====================================================
# 4. BUILD VIDEO ANALYSIS PROMPT
# ====================================================
def build_video_analysis_prompt(
    title: str,
    views: Union[int, float, str],
    likes: Union[int, float, str],
    comments: Union[int, float, str, List[Any]],
) -> str:
    """Build a prompt for in-depth single video performance and content review.

    Args:
        title (str): Video title.
        views (Union[int, float, str]): View count.
        likes (Union[int, float, str]): Like count.
        comments (Union[int, float, str, List[Any]]): Comment count or comment list.

    Returns:
        str: Formatted prompt string for Gemini API.
    """
    comment_count = len(comments) if isinstance(comments, list) else comments

    return f"""You are GWEN, an expert AI YouTube Creator Assistant.

Analyze the performance metadata for this video:

--- VIDEO DETAILS ---
- Title: "{title}"
- Views: {views}
- Likes: {likes}
- Comments: {comment_count}

--- ANALYSIS REQUIREMENTS ---
Please provide a targeted evaluation addressing:

1. Strengths: What worked well based on title packaging and engagement numbers.
2. Weaknesses: Potential flaws, friction points, or title/topic mismatch causing drop-off.
3. CTR Improvement Ideas: 2-3 specific title tweaks or thumbnail concept revisions to increase click-through rate.
4. Retention Suggestions: Practical advice on pacing, hook, or structure to hold viewer attention longer.
5. One Practical Improvement: EXACTLY ONE high-priority action item the creator can immediately apply to their next upload.

Ensure the advice is realistic, actionable, and tailored to creator growth."""


# ====================================================
# 5. BUILD CREATOR TWIN PROMPT
# ====================================================
def build_creator_twin_prompt(
    recent_titles: List[str],
    recent_descriptions: List[str],
    topic_or_concept: Optional[str] = None,
) -> str:
    """Build a prompt for Creator Twin to mirror the channel's writing style and tone.

    Args:
        recent_titles (List[str]): List of recent video titles.
        recent_descriptions (List[str]): List of recent video descriptions.
        topic_or_concept (Optional[str]): Optional topic/idea for the new video.

    Returns:
        str: Formatted prompt string for Gemini API.
    """
    titles_block = "\n".join(f"- {t}" for t in recent_titles) if recent_titles else "No recent titles provided."
    descriptions_block = (
        "\n\n".join(f"[Sample Description]\n{d}" for d in recent_descriptions)
        if recent_descriptions
        else "No recent descriptions provided."
    )
    concept_clause = f"\nTarget Topic/Concept: {topic_or_concept}" if topic_or_concept else ""

    return f"""You are GWEN, operating as the creator's "Creator Twin".

Your objective is to learn the creator's unique voice, writing style, formatting structure, and tone from their past content, and generate new video metadata.

--- CREATOR STYLE EXAMPLES ---
Titles:
{titles_block}

Descriptions:
{descriptions_block}
{concept_clause}

--- INSTRUCTIONS ---
1. Learn and adopt the creator's distinct voice, tone, emoji usage, formatting habits, and call-to-action style.
2. Generate new content that seamlessly fits their channel identity:
   - 3 Title Options (high CTR potential, matching creator style)
   - 1 Full Description (matching their formatting layout and tone)
   - 10-15 Tags (comma-separated, SEO-optimized tags matching the niche)
3. Keep creator tone 100% consistent throughout."""


# ====================================================
# 6. BUILD CONTENT STRATEGY PROMPT
# ====================================================
def build_content_strategy_prompt(
    analytics_summary: Union[str, Dict[str, Any]],
    recent_uploads: Union[List[str], List[Dict[str, Any]]],
) -> str:
    """Build a prompt for generating a strategic 10-idea content plan.

    Args:
        analytics_summary (Union[str, Dict[str, Any]]): Channel performance summary.
        recent_uploads (Union[List[str], List[Dict[str, Any]]]): List of recent video titles or metadata dicts.

    Returns:
        str: Formatted prompt string for Gemini API.
    """
    if isinstance(analytics_summary, dict):
        analytics_formatted = "\n".join(f"- {k}: {v}" for k, v in analytics_summary.items())
    else:
        analytics_formatted = str(analytics_summary)

    uploads_formatted = []
    if isinstance(recent_uploads, list):
        for item in recent_uploads:
            if isinstance(item, dict):
                title = item.get("title", str(item))
                views = item.get("views", "N/A")
                uploads_formatted.append(f"- {title} (Views: {views})")
            else:
                uploads_formatted.append(f"- {item}")
    uploads_text = "\n".join(uploads_formatted) if uploads_formatted else "No recent uploads provided."

    return f"""You are GWEN, an expert AI YouTube Content Strategist.

Based on the channel's performance metrics and recent upload history, build a strategic content plan:

--- CHANNEL ANALYTICS SUMMARY ---
{analytics_formatted}

--- RECENT UPLOADS ---
{uploads_text}

--- STRATEGY DELIVERABLES ---
Please output a comprehensive content plan containing:

1. 10 Video Ideas:
   For EACH of the 10 ideas, specify:
   - Working Title
   - Reasoning (Data-driven justification why this topic will perform)
   - Confidence Level (e.g. High, Medium)
   - Potential Audience (Target demographic or viewer interest segment)

2. Publishing Strategy:
   - Recommended posting schedule and upload cadence.
   - Pacing recommendations (balancing search-focused evergreen videos vs high-CTR viral topics)."""


# ====================================================
# PURE REASONING & FORMATTING HELPERS
# ====================================================
def _format_comment_list(comments: Union[List[str], List[Dict[str, Any]]]) -> str:
    """Pure helper to format a comment list into clean text for prompt insertion."""
    if not comments:
        return "No viewer comments available."

    lines = []
    for idx, comment in enumerate(comments, 1):
        if isinstance(comment, dict):
            text = comment.get("text") or comment.get("content") or comment.get("comment") or str(comment)
            author = comment.get("author") or comment.get("user") or comment.get("authorDisplayName")
            lines.append(f"{idx}. {author}: {text}" if author else f"{idx}. {text}")
        else:
            lines.append(f"{idx}. {str(comment)}")

    return "\n".join(lines)


def format_ai_response(
    reply: str, action: Optional[str] = None, data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Pure helper to package AI response details into a standardized dictionary payload.

    Args:
        reply (str): Text response generated for the creator.
        action (Optional[str]): Intent or action identifier.
        data (Optional[Dict[str, Any]]): Supplementary payload or structured data.

    Returns:
        Dict[str, Any]: Standardized response dictionary.
    """
    return {
        "reply": reply or "",
        "action": action or INTENT_GENERAL_CHAT,
        "data": data if data is not None else {},
    }


def extract_key_insights(response_text: str) -> List[str]:
    """Pure helper to parse bulleted or numbered insights from AI response text.

    Args:
        response_text (str): Raw string text returned from an LLM.

    Returns:
        List[str]: List of clean insight strings.
    """
    if not response_text:
        return []

    insights = []
    for line in response_text.splitlines():
        line_str = line.strip()
        # Match lines starting with bullet symbols or numbers
        if re.match(r"^([\bullet\-\*\•]|\d+[\.\)])\s+", line_str):
            clean_line = re.sub(r"^([\bullet\-\*\•]|\d+[\.\)])\s+", "", line_str)
            if clean_line:
                insights.append(clean_line)

    return insights
