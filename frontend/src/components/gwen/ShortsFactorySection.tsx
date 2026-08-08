import { motion } from "framer-motion";
import { Download, Upload } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { toErrorMessage } from "@/api/client";
import { downloadUrl, generateShorts } from "@/api/video";
import { GwenFace } from "@/components/gwen/GwenFace";

/** Pulls clip filenames out of the strict JSON response without transforming it. */
function extractFilenames(data: Record<string, unknown>): string[] {
  const out: string[] = [];
  const visit = (value: unknown) => {
    if (typeof value === "string" && /\.(mp4|mov|webm)$/i.test(value)) {
      out.push(value.split("/").pop() as string);
      return;
    }
    if (Array.isArray(value)) value.forEach(visit);
    else if (value && typeof value === "object") Object.values(value).forEach(visit);
  };
  visit(data);
  return [...new Set(out)];
}

const STAGES = [
  "Reading the timeline",
  "Scoring hook density",
  "Finding standalone moments",
  "Cutting vertical clips",
  "Rendering output",
];

function WaitingState({ startedAt }: { startedAt: number }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000);
    return () => clearInterval(id);
  }, [startedAt]);

  // Expected window is 2-5 minutes; cap the indicator short of complete.
  const progress = Math.min(96, (elapsed / 240) * 100);
  const stage = STAGES[Math.min(STAGES.length - 1, Math.floor(elapsed / 48))];

  return (
    <div className="glass-panel mt-6 rounded-3xl p-8 text-center">
      <motion.div
        animate={{ scale: [1, 1.04, 1] }}
        transition={{ duration: 2.6, repeat: Infinity, ease: "easeInOut" }}
        className="mx-auto h-24 w-24"
      >
        <GwenFace className="h-full w-full" expression="focused" variant="sharp" />
      </motion.div>
      <p className="mt-5 text-sm text-primary">{stage}...</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Generating shorts usually takes 2 to 5 minutes. Elapsed {Math.floor(elapsed / 60)}m{" "}
        {elapsed % 60}s.
      </p>
      <div className="mx-auto mt-5 h-2 max-w-md overflow-hidden rounded-full bg-muted">
        <motion.div
          className="h-full rounded-full bg-primary"
          style={{ boxShadow: "0 0 16px oklch(0.72 0.3 340 / 0.6)" }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: "linear", duration: 1 }}
        />
      </div>
    </div>
  );
}

export function ShortsFactorySection() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [clips, setClips] = useState<string[]>([]);
  const [raw, setRaw] = useState<Record<string, unknown> | null>(null);

  const handle = async (file: File) => {
    setFileName(file.name);
    setError(null);
    setClips([]);
    setRaw(null);
    setStartedAt(Date.now());
    try {
      const data = await generateShorts(file);
      setRaw(data);
      setClips(extractFilenames(data));
    } catch (err) {
      setError(toErrorMessage(err));
    } finally {
      setStartedAt(null);
    }
  };

  return (
    <div className="mx-auto min-h-screen w-full max-w-6xl px-6 py-24">
      <p className="text-xs tracking-[0.4em] text-primary uppercase">Shorts Factory</p>
      <h2 className="mt-3 text-4xl font-semibold sm:text-5xl">Clips, auto-detected</h2>
      <p className="mt-4 max-w-xl text-sm text-foreground/70">
        Upload a long-form video. GWEN detects the strongest standalone moments and cuts them into
        vertical shorts you can preview and download.
      </p>

      <button
        type="button"
        disabled={startedAt !== null}
        onClick={() => inputRef.current?.click()}
        className="glass-panel mt-8 flex w-full flex-col items-center justify-center gap-2 rounded-3xl border-dashed px-6 py-12 text-sm text-foreground/75 transition-colors hover:text-primary disabled:opacity-60"
      >
        <Upload className="h-6 w-6 text-primary" />
        {fileName ?? "Select a video to generate shorts"}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) void handle(file);
        }}
      />

      {startedAt !== null && <WaitingState startedAt={startedAt} />}

      {error && (
        <p className="mt-6 rounded-2xl border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm">
          {error}
        </p>
      )}

      {clips.length > 0 && (
        <>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {clips.map((filename) => (
              <motion.div
                key={filename}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel overflow-hidden rounded-3xl p-4"
              >
                <video
                  src={downloadUrl(filename)}
                  controls
                  playsInline
                  className="aspect-[9/16] w-full rounded-2xl bg-black object-cover"
                />
                <p className="mt-3 truncate text-xs text-muted-foreground">{filename}</p>
                <a
                  href={downloadUrl(filename)}
                  download={filename}
                  className="mt-3 inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-xs font-medium text-primary-foreground"
                >
                  <Download className="h-3.5 w-3.5" /> Download
                </a>
              </motion.div>
            ))}
          </div>
          <p className="mt-6 text-sm text-foreground/70">
            <span className="text-primary">Suggested publishing time.</span> Weekdays 18:00 local,
            spaced two days apart for the strongest carry-over.
          </p>
        </>
      )}

      {raw && clips.length === 0 && !error && (
        <pre className="glass-panel mt-6 overflow-x-auto rounded-2xl p-4 text-xs text-foreground/70">
          {JSON.stringify(raw, null, 2)}
        </pre>
      )}
    </div>
  );
}
