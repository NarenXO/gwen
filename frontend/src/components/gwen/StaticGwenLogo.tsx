import { type GwenVariant } from "./GwenFace";

/**
 * Static eye spec for Landing and Home:
 * tilted-flame shape, sharp flame-flick top-outer corners, deep organic bottom curves, 
 * sharpened inner corners, narrow inner gap.
 */
const EYE_LEFT_STATIC = "M 180 235 C 160 285, 90 270, 50 190 C 30 140, 40 100, 30 70 C 110 110, 160 170, 180 215 Z";
const EYE_STROKE = "#FF69B4";
const EYE_FILL = "#FFFFFF";

export const FACE_PATH = "M 200 25 C 280 25, 340 81, 340 161 C 340 245, 305 309, 258 349 C 238 367, 215 377, 200 381 C 185 377, 162 367, 142 349 C 95 309, 60 245, 60 161 C 60 81, 120 25, 200 25 Z";

const variantStyle: Record<GwenVariant, { fill: string; glow: number }> = {
  neon: { fill: EYE_FILL, glow: 1 },
  soft: { fill: EYE_FILL, glow: 0.55 },
  sharp: { fill: EYE_FILL, glow: 0.4 },
  filled: { fill: EYE_FILL, glow: 1.3 },
};

export function StaticGwenLogo({
  variant = "neon",
  className,
  faceFill = true,
}: {
  variant?: GwenVariant;
  className?: string;
  faceFill?: boolean;
}) {
  const style = variantStyle[variant];

  const eye = (
    <path
      d={EYE_LEFT_STATIC}
      fill={style.fill}
      stroke={EYE_STROKE}
      strokeWidth={6}
      strokeLinejoin="miter"
      strokeMiterlimit={4}
      strokeLinecap="round"
    />
  );

  return (
    <svg
      viewBox="0 0 400 500"
      className={className}
      role="img"
      aria-label="GWEN Logo"
      style={{ overflow: "visible" }}
    >
      <defs>
        <clipPath id="static-gwen-face-clip" clipPathUnits="objectBoundingBox">
          <path d="M 0.5000 0.0500 C 0.7000 0.0500 0.8500 0.1620 0.8500 0.3220 C 0.8500 0.4900 0.7625 0.6180 0.6450 0.6980 C 0.5950 0.7340 0.5375 0.7540 0.5000 0.7620 C 0.4625 0.7540 0.4050 0.7340 0.3550 0.6980 C 0.2375 0.6180 0.1500 0.4900 0.1500 0.3220 C 0.1500 0.1620 0.3000 0.0500 0.5000 0.0500 Z" />
        </clipPath>
        <radialGradient id="static-gwen-face" cx="50%" cy="35%" r="75%">
          <stop offset="0%" stopColor="oklch(0.16 0.02 320)" />
          <stop offset="100%" stopColor="oklch(0.03 0.01 320)" />
        </radialGradient>
        <filter id="static-gwen-glow" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation={6 * style.glow} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {faceFill && <path d={FACE_PATH} fill="#000000" />}
      
      <path
        d={FACE_PATH}
        fill="none"
        stroke={EYE_STROKE}
        strokeOpacity="0.28"
        strokeWidth="4"
      />

      <g filter="url(#static-gwen-glow)" transform="translate(200, 210) scale(0.78) translate(-200, -200)">
        {eye}
        <g transform="translate(400, 0) scale(-1, 1)">{eye}</g>
      </g>
    </svg>
  );
}
