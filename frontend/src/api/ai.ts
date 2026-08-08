import { api, jsonHeaders } from "./client";

export type CurrentPage =
  | "dashboard"
  | "analytics"
  | "videos"
  | "comments"
  | "creator_twin"
  | "content_strategy"
  | "settings"
  | "home";

export type SectionId = "home" | "analysis" | "studio" | "shorts";

export type AIAction =
  | "analytics_summary"
  | "video_analysis"
  | "comment_analysis"
  | "creator_twin"
  | "content_strategy"
  | "general_chat"
  | "unknown";

export interface AIResponse {
  reply: string;
  action: AIAction;
  data: Record<string, unknown>;
}

export interface AIActionRequest {
  message: string;
  conversation_history: unknown[];
  current_page: CurrentPage;
  user_id?: string;
}

/** Maps the on-screen section to the backend `current_page` enum. */
export function sectionToCurrentPage(section: SectionId): CurrentPage {
  switch (section) {
    case "home":
      return "home";
    case "analysis":
      // Analysis merges analytics + comments; backend enum splits them.
      return "analytics";
    case "studio":
      return "videos";
    case "shorts":
      // TEMPORARY FALLBACK: the backend `current_page` enum has no value for
      // Shorts Factory, so we send "videos". Pending confirmation from Salman
      // (backend) — either add a "shorts" value or confirm this fallback.
      return "videos";
  }
}

export async function postAiAction(payload: AIActionRequest): Promise<AIResponse> {
  const { data } = await api.post<AIResponse>("/ai/action", payload, { headers: jsonHeaders });
  return data;
}
