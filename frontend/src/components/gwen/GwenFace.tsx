import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export type GwenExpression = "neutral" | "curious" | "happy" | "focused";
export type GwenVariant = "neon" | "soft" | "sharp" | "filled";

/**
 * Exact spec geometry on a 400x400 unit grid, symmetry axis x=200.
 * The right eye is this same path mirrored horizontally across x=200.
 */
const EYE_LEFT =
  "M 195 210 C 185 160, 150 130, 90 140 C 80 142, 85 160, 105 190 C 125 230, 155 250, 195 240 C 200 238, 200 225, 195 210 Z";

const EYE_STROKE = "#FF69B4";
const EYE_FILL = "#FFFFFF";

const variantStyle: Record<GwenVariant, { fill: string; stroke: number; glow: number }> = {
  neon: { fill: EYE_FILL, stroke: 8, glow: 1 },
  soft: { fill: EYE_FILL, stroke: 8, glow: 0.55 },
  sharp: { fill: EYE_FILL, stroke: 8, glow: 0.4 },
  filled: { fill: EYE_FILL, stroke: 8, glow: 1.3 },
};

const expressionTransform: Record<GwenExpression, { y: number; scaleY: number; rotate: number }> = {
  neutral: { y: 0, scaleY: 1, rotate: 0 },
  curious: { y: 0, scaleY: 1, rotate: -4 },
  happy: { y: -10, scaleY: 0.92, rotate: 0 },
  focused: { y: 4, scaleY: 0.55, rotate: 0 },
};

/**
 * GWEN mark: black oval face silhouette with Spider-Gwen leaf eyes.
 * Blink collapses scaleY to 0 around the 200px 200px center; stroke is constant.
 */
export function GwenFace({
  expression = "curious",
  variant = "neon",
  className,
  blink = true,
  faceFill = true,
}: {
  expression?: GwenExpression;
  variant?: GwenVariant;
  className?: string;
  blink?: boolean;
  /** When false, the silhouette is left transparent so a glass layer can show through. */
  faceFill?: boolean;
}) {
  const [frame, setFrame] = useState(0);
  const style = variantStyle[variant];
  const ex = expressionTransform[expression];

  useEffect(() => {
    if (!blink) return;
    let timer: ReturnType<typeof setTimeout>;
    const step = (next: number) => {
      setFrame(next);
      const delay = next === 0 ? 2600 + Math.random() * 2200 : 90;
      timer = setTimeout(() => step((next + 1) % 4), delay);
    };
    timer = setTimeout(() => step(1), 1800);
    return () => clearTimeout(timer);
  }, [blink]);

  const closed = frame === 2;
  const closing = frame === 1 || frame === 3;
  const scaleY = closed ? 0 : closing ? 0.45 : ex.scaleY;

  const eye = (
    <path
      d={EYE_LEFT}
      fill={style.fill}
      stroke={EYE_STROKE}
      strokeWidth={style.stroke}
      strokeLinejoin="round"
      strokeLinecap="round"
    />
  );

  return (
    <svg
      viewBox="0 0 400 466"
      className={className}
      role="img"
      aria-label="GWEN"
      style={{ overflow: "visible" }}
    >
      <defs>
        <radialGradient id="gwen-face" cx="50%" cy="35%" r="75%">
          <stop offset="0%" stopColor="oklch(0.16 0.02 320)" />
          <stop offset="100%" stopColor="oklch(0.03 0.01 320)" />
        </radialGradient>
        <filter id="gwen-glow" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation={6 * style.glow} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {faceFill && <ellipse cx="200" cy="233" rx="173" ry="220" fill="url(#gwen-face)" />}
      <ellipse
        cx="200"
        cy="233"
        rx="173"
        ry="220"
        fill="none"
        stroke={EYE_STROKE}
        strokeOpacity="0.28"
        strokeWidth="4"
      />

      <motion.g
        filter="url(#gwen-glow)"
        animate={{ y: ex.y, rotate: ex.rotate }}
        transition={{ type: "spring", stiffness: 120, damping: 14 }}
        style={{ originX: "200px", originY: "200px" }}
      >
        <motion.g
          animate={{ scaleY }}
          transition={{ duration: 0.09, ease: "easeOut" }}
          style={{ originX: "200px", originY: "200px", transformOrigin: "200px 200px" }}
        >
          {eye}
          <g transform="translate(400, 0) scale(-1, 1)">{eye}</g>
        </motion.g>
      </motion.g>
    </svg>
  );
}
