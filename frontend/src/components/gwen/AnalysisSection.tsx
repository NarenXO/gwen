import { motion } from "framer-motion";

/** Mock data matches the confirmed analytics_summary / comment_analysis shapes. */
const summary = { channel_name: "Gwen Studio", views: 1284900, subscribers: 84200, videos: 213 };
const sentiment = { positive: 68, neutral: 22, negative: 10 };
const series = [12, 20, 16, 30, 26, 42, 38, 55, 60, 74, 69, 92];
const themes = [
  { theme: "Editing tutorials", weight: 42 },
  { theme: "Gear questions", weight: 27 },
  { theme: "Upload schedule", weight: 18 },
  { theme: "Collab requests", weight: 13 },
];

function points(values: number[], w: number, h: number) {
  const max = Math.max(...values);
  return values.map((v, i) => ({
    x: (i / (values.length - 1)) * w,
    y: h - (v / max) * (h - 12) - 6,
  }));
}

function GrowthGraph() {
  const w = 620;
  const h = 220;
  const p = points(series, w, h);
  const line = p
    .map((pt, i) => `${i === 0 ? "M" : "L"} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`)
    .join(" ");
  const area = `${line} L ${w} ${h} L 0 ${h} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-56 w-full">
      <defs>
        <linearGradient id="gwen-area" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--neon)" stopOpacity="0.4" />
          <stop offset="100%" stopColor="var(--neon)" stopOpacity="0" />
        </linearGradient>
        <filter id="gwen-line-glow" x="-20%" y="-40%" width="140%" height="200%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {[0.25, 0.5, 0.75].map((g) => (
        <line
          key={g}
          x1="0"
          x2={w}
          y1={h * g}
          y2={h * g}
          stroke="var(--border)"
          strokeDasharray="4 8"
        />
      ))}

      <motion.path
        d={area}
        fill="url(#gwen-area)"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 1.4, duration: 1 }}
      />
      <motion.path
        d={line}
        fill="none"
        stroke="var(--neon)"
        strokeWidth="3"
        strokeLinecap="round"
        filter="url(#gwen-line-glow)"
        initial={{ pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 2, ease: "easeInOut" }}
      />
      {p.map((pt, i) => (
        <motion.circle
          key={i}
          cx={pt.x}
          cy={pt.y}
          r="4"
          fill="var(--neon)"
          initial={{ opacity: 0, scale: 0 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.15 * i, type: "spring", stiffness: 240, damping: 16 }}
        />
      ))}
    </svg>
  );
}

function Metric({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="glass-panel rounded-2xl p-5">
      <p className="text-[10px] tracking-[0.25em] text-muted-foreground uppercase">{label}</p>
      <p className="mt-2 text-3xl font-semibold neon-text">{value}</p>
      {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
    </div>
  );
}

export function AnalysisSection() {
  return (
    <div className="mx-auto min-h-screen w-full max-w-6xl px-6 py-24">
      <p className="text-xs tracking-[0.4em] text-primary uppercase">Analysis</p>
      <h2 className="mt-3 text-4xl font-semibold sm:text-5xl">Channel Intelligence</h2>

      <div className="mt-10 grid gap-4 sm:grid-cols-3">
        <Metric
          label="Views (30d)"
          value={summary.views.toLocaleString()}
          sub={summary.channel_name}
        />
        <Metric label="Watch time" value="41.2k hrs" sub="+18% vs previous period" />
        <Metric label="Health score" value="86 / 100" sub={`${summary.videos} videos tracked`} />
      </div>

      <div className="glass-panel mt-6 rounded-3xl p-6">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="text-lg font-semibold">Performance Overview</h3>
          <span className="text-xs text-muted-foreground">
            {summary.subscribers.toLocaleString()} subscribers
          </span>
        </div>
        <GrowthGraph />
        <p className="mt-4 text-sm leading-relaxed text-foreground/75">
          <span className="text-primary">AI summary.</span> Growth is compounding on tutorial-style
          uploads, with retention peaking when the hook lands under eight seconds. Shift two uploads
          per month toward the editing series and hold the current publishing cadence.
        </p>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="glass-panel rounded-3xl p-6">
          <h3 className="text-lg font-semibold">Audience Intelligence</h3>
          <p className="mt-1 text-xs text-muted-foreground">Comment sentiment</p>
          <div className="mt-4 space-y-4">
            {(
              [
                ["Positive", sentiment.positive],
                ["Neutral", sentiment.neutral],
                ["Negative", sentiment.negative],
              ] as const
            ).map(([label, value]) => (
              <div key={label}>
                <div className="flex justify-between text-sm">
                  <span className="text-foreground/80">{label}</span>
                  <span className="neon-text">{value}%</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
                  <motion.div
                    className="h-full rounded-full bg-primary"
                    style={{ boxShadow: "0 0 14px oklch(0.72 0.3 340 / 0.6)" }}
                    initial={{ width: 0 }}
                    whileInView={{ width: `${value}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.2, ease: "easeOut" }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-3xl p-6">
          <h3 className="text-lg font-semibold">Recurring themes</h3>
          <ul className="mt-4 space-y-3">
            {themes.map((t) => (
              <li key={t.theme} className="flex items-center justify-between text-sm">
                <span className="text-foreground/80">{t.theme}</span>
                <span className="rounded-full border border-primary/40 px-2 py-0.5 text-xs text-primary">
                  {t.weight}%
                </span>
              </li>
            ))}
          </ul>
          <h4 className="mt-6 text-sm font-semibold">Engagement suggestions</h4>
          <ul className="mt-2 space-y-2 text-sm text-foreground/70">
            <li>Pin a gear list comment on the three highest-traffic tutorials.</li>
            <li>Reply within two hours on upload day to lift comment velocity.</li>
            <li>Turn the top collab requests into a community post poll.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
