import { AnimatePresence, motion } from "framer-motion";
import { ArrowUp, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

import { postAiAction, sectionToCurrentPage, type AIResponse, type SectionId } from "@/api/ai";
import { toErrorMessage } from "@/api/client";
import { GwenFace, type GwenExpression } from "@/components/gwen/GwenFace";

type ChatMessage =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; response?: AIResponse }
  | { role: "error"; content: string };

/**
 * Portable floating GWEN agent.
 * Self-contained state, no global CSS assumptions, no app-root dependency —
 * safe to mount later inside a Shadow DOM content script on youtube.com.
 */
export function ChatAgent({ section }: { section: SectionId }) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const last = messages[messages.length - 1];
  const expression: GwenExpression = loading
    ? "focused"
    : last?.role === "assistant"
      ? "happy"
      : "curious";

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open, loading]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await postAiAction({
        message: text,
        conversation_history: history,
        current_page: sectionToCurrentPage(section),
      });
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply, response: res }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", content: toErrorMessage(err) }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed right-4 bottom-4 z-50 flex flex-col items-end gap-3 sm:right-6 sm:bottom-6">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.94 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.94 }}
            transition={{ type: "spring", stiffness: 220, damping: 22 }}
            className="glass-panel flex h-[26rem] w-[min(23rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl"
          >
            <div className="flex items-center justify-between border-b border-border/60 px-4 py-3">
              <div className="flex items-center gap-2">
                <GwenFace className="h-6 w-6" expression={expression} variant="soft" />
                <div>
                  <p className="text-sm font-semibold">GWEN</p>
                  <p className="text-[10px] tracking-widest text-muted-foreground uppercase">
                    {loading ? "Thinking" : "Online"}
                  </p>
                </div>
              </div>
              <button
                type="button"
                aria-label="Close chat"
                onClick={() => setOpen(false)}
                className="rounded-full p-1.5 text-muted-foreground transition-colors hover:text-primary"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
              {messages.length === 0 && (
                <p className="text-sm leading-relaxed text-muted-foreground">
                  Ask about channel performance, comment sentiment, or what to publish next.
                </p>
              )}
              {messages.map((m, i) => (
                <div key={i} className={m.role === "user" ? "flex justify-end" : undefined}>
                  {m.role === "user" ? (
                    <span className="max-w-[85%] rounded-2xl bg-primary px-3 py-2 text-sm text-primary-foreground">
                      {m.content}
                    </span>
                  ) : m.role === "error" ? (
                    <p className="rounded-2xl border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-foreground">
                      {m.content}
                    </p>
                  ) : (
                    <div className="space-y-2">
                      <div className="text-sm leading-relaxed [&_a]:text-primary [&_code]:text-primary [&_li]:ml-4 [&_li]:list-disc [&_strong]:text-foreground">
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                      </div>
                      {m.response && <ActionCard response={m.response} />}
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <motion.p
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.6, repeat: Infinity }}
                  className="text-sm text-primary"
                >
                  Thinking...
                </motion.p>
              )}
            </div>

            <div className="border-t border-border/60 p-3">
              <div className="flex items-end gap-2 rounded-2xl border border-input bg-background/50 px-3 py-2">
                <textarea
                  ref={inputRef}
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void send();
                    }
                  }}
                  placeholder="Ask GWEN..."
                  className="max-h-24 flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                />
                <button
                  type="button"
                  aria-label="Send"
                  disabled={loading || !input.trim()}
                  onClick={() => void send()}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-opacity disabled:opacity-40"
                >
                  <ArrowUp className="h-4 w-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        type="button"
        aria-label={open ? "Collapse GWEN" : "Open GWEN"}
        onClick={() => setOpen((v) => !v)}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.94 }}
        animate={{ y: [0, -6, 0] }}
        transition={{ y: { duration: 4, repeat: Infinity, ease: "easeInOut" } }}
        className="glass-panel neon-glow flex h-16 w-16 items-center justify-center rounded-full"
      >
        <GwenFace
          className="h-11 w-11"
          expression={expression}
          variant={loading ? "sharp" : open ? "filled" : "neon"}
        />
      </motion.button>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-border/60 bg-background/40 px-3 py-2">
      <p className="text-[10px] tracking-widest text-muted-foreground uppercase">{label}</p>
      <p className="text-sm font-semibold neon-text">{value}</p>
    </div>
  );
}

/** Renders the structured component matching the returned AIAction. */
function ActionCard({ response }: { response: AIResponse }) {
  const d = response.data as Record<string, string | number>;
  switch (response.action) {
    case "analytics_summary":
      return (
        <div className="grid grid-cols-2 gap-2">
          <Stat label="Channel" value={d["channel_name"] ?? "-"} />
          <Stat label="Views" value={d["views"] ?? "-"} />
          <Stat label="Subscribers" value={d["subscribers"] ?? "-"} />
          <Stat label="Videos" value={d["videos"] ?? "-"} />
        </div>
      );
    case "video_analysis":
      return (
        <div className="grid grid-cols-2 gap-2">
          <Stat label="Video" value={d["video_title"] ?? "-"} />
          <Stat label="Views" value={d["views"] ?? "-"} />
          <Stat label="Likes" value={d["likes"] ?? "-"} />
          <Stat label="Comments" value={d["comments"] ?? "-"} />
        </div>
      );
    case "comment_analysis":
      return (
        <div className="grid grid-cols-3 gap-2">
          <Stat label="Positive" value={d["positive"] ?? "-"} />
          <Stat label="Neutral" value={d["neutral"] ?? "-"} />
          <Stat label="Negative" value={d["negative"] ?? "-"} />
        </div>
      );
    case "creator_twin":
      return (
        <div className="grid grid-cols-2 gap-2">
          <Stat label="Persona" value={d["persona"] ?? "-"} />
          <Stat label="Tone" value={d["tone"] ?? "-"} />
        </div>
      );
    case "content_strategy":
      return (
        <div className="grid grid-cols-1 gap-2">
          <Stat label="Recommended topic" value={d["recommended_topic"] ?? "-"} />
          <Stat label="Reason" value={d["reason"] ?? "-"} />
        </div>
      );
    default:
      return null;
  }
}
