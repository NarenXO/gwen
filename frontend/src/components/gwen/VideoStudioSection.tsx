import { motion } from "framer-motion";
import { Upload } from "lucide-react";
import { useRef, useState } from "react";

import { toErrorMessage } from "@/api/client";
import { analyzeThumbnail, analyzeVideo } from "@/api/video";

type Result = Record<string, unknown> | null;

function ResultFields({ data }: { data: Record<string, unknown> }) {
  return (
    <dl className="mt-4 space-y-2 text-sm">
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="flex gap-3 border-b border-border/50 pb-2">
          <dt className="w-40 shrink-0 text-[11px] tracking-widest text-muted-foreground uppercase">
            {key.replace(/_/g, " ")}
          </dt>
          <dd className="flex-1 break-words text-foreground/85">
            {typeof value === "object" && value !== null ? JSON.stringify(value) : String(value)}
          </dd>
        </div>
      ))}
    </dl>
  );
}

function UploadPanel({
  title,
  subtitle,
  accept,
  cta,
  onUpload,
}: {
  title: string;
  subtitle: string;
  accept: string;
  cta: string;
  onUpload: (file: File) => Promise<Record<string, unknown>>;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Result>(null);

  const handle = async (file: File) => {
    setFileName(file.name);
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      setResult(await onUpload(file));
    } catch (err) {
      setError(toErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel flex flex-col rounded-3xl p-6">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="mt-5 flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-primary/40 bg-primary/5 px-6 py-10 text-sm text-foreground/75 transition-colors hover:border-primary hover:text-primary"
      >
        <Upload className="h-5 w-5 text-primary" />
        {fileName ?? cta}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) void handle(file);
        }}
      />

      {loading && (
        <motion.p
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="mt-4 text-sm text-primary"
        >
          Analyzing...
        </motion.p>
      )}
      {error && (
        <p className="mt-4 rounded-xl border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm">
          {error}
        </p>
      )}
      {result && <ResultFields data={result} />}
    </div>
  );
}

export function VideoStudioSection() {
  return (
    <div className="mx-auto min-h-screen w-full max-w-6xl px-6 py-24">
      <p className="text-xs tracking-[0.4em] text-primary uppercase">Video Studio</p>
      <h2 className="mt-3 text-4xl font-semibold sm:text-5xl">Content Optimization</h2>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <UploadPanel
          title="Video Doctor"
          subtitle="Upload a video for a structural and retention diagnosis."
          accept="video/*"
          cta="Select a video file"
          onUpload={analyzeVideo}
        />
        <UploadPanel
          title="Thumbnail Analyzer"
          subtitle="Upload a thumbnail for clarity, contrast and click-appeal scoring."
          accept="image/*"
          cta="Select a thumbnail image"
          onUpload={analyzeThumbnail}
        />
      </div>

      <div className="glass-panel mt-6 grid gap-6 rounded-3xl p-6 sm:grid-cols-3">
        {[
          {
            title: "Hook improvement",
            body: "Move the payoff promise into the first six seconds and cut the channel intro.",
          },
          {
            title: "Thumbnail fix",
            body: "Raise subject contrast against the background and cap the text at three words.",
          },
          {
            title: "Engagement optimization",
            body: "Place one direct question at the midpoint and pin it as the first comment.",
          },
        ].map((rec) => (
          <div key={rec.title}>
            <h4 className="text-sm font-semibold neon-text">{rec.title}</h4>
            <p className="mt-2 text-sm leading-relaxed text-foreground/70">{rec.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
