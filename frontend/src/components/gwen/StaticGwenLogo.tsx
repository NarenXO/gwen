import { type GwenVariant } from "./GwenFace";

/**
 * Static eye spec for Landing and Home:
 * tilted-flame shape, sharp flame-flick top-outer corners, deep organic bottom curves, 
 * sharpened inner corners, narrow inner gap.
 */
const EYE_LEFT_STATIC = "M 180 235 C 160 285, 90 270, 50 190 C 30 140, 40 100, 30 70 C 110 110, 160 170, 180 215 Z";
const EYE_STROKE = "#FF69B4";
const EYE_FILL = "#FFFFFF";

export const FACE_PATH = "M 200.0 16.1 C 284.0 16.1 347.0 74.9 347.0 158.9 C 347.0 247.1 310.3 314.3 260.9 356.3 C 239.9 375.2 215.8 385.7 200.0 389.9 C 184.3 385.7 160.1 375.2 139.1 356.3 C 89.8 314.3 53.0 247.1 53.0 158.9 C 53.0 74.9 116.0 16.1 200.0 16.1 Z";

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
          <path d="M 0.5000 0.0322 C 0.7100 0.0322 0.8675 0.1498 0.8675 0.3178 C 0.8675 0.4942 0.7758 0.6286 0.6522 0.7126 C 0.5998 0.7504 0.5395 0.7714 0.5000 0.7798 C 0.4608 0.7714 0.4002 0.7504 0.3478 0.7126 C 0.2245 0.6286 0.1325 0.4942 0.1325 0.3178 C 0.1325 0.1498 0.2900 0.0322 0.5000 0.0322 Z" />
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
