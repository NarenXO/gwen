import { motion } from "framer-motion";
import { useEffect, useState } from "react";

import { GwenFace } from "@/components/gwen/GwenFace";

const KEY = "gwen-landing-played";

/**
 * One single logo, one unbroken motion.
 *
 * 3D structure (order matters):
 *  - outer motion.div: owns `perspective: 1000px` + the zoom (scale) and the
 *    glide to the left half (x). It is the PARENT that provides depth.
 *  - inner motion.div: owns `transform-style: preserve-3d` and the rotateY
 *    spin. Being a direct child of the perspective element is what makes the
 *    face genuinely foreshorten (narrow edge-on, widen back out).
 */
export function LandingSequence({ onDone }: { onDone: () => void }) {
  const [gone, setGone] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => {
      sessionStorage.setItem(KEY, "1");
      setGone(true);
      onDone();
    }, 4200);
    return () => clearTimeout(t);
  }, [onDone]);

  if (gone) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center">
      <motion.div
        className="aspect-[120/140] w-[min(34vw,62vh,26rem)]"
        style={{ perspective: 1000, perspectiveOrigin: "50% 50%" }}
        initial={{ scale: 0.18, x: 0, opacity: 0 }}
        animate={{
          scale: [0.18, 1.1, 1.75, 1, 1],
          x: ["0vw", "0vw", "0vw", "-25vw", "-25vw"],
          opacity: [0, 1, 1, 1, 1],
        }}
        transition={{
          duration: 4.2,
          times: [0, 0.3, 0.55, 0.9, 1],
          ease: [0.22, 1, 0.36, 1],
        }}
      >
        <motion.div
          className="h-full w-full"
          style={{ transformStyle: "preserve-3d", backfaceVisibility: "visible" }}
          initial={{ rotateY: 0 }}
          animate={{ rotateY: [0, 260, 540, 720, 720] }}
          transition={{
            duration: 4.2,
            times: [0, 0.3, 0.55, 0.9, 1],
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <div className="relative h-full w-full">
            <div
              className="absolute inset-0 backdrop-blur-xl backdrop-saturate-150"
              style={{ clipPath: "ellipse(43% 47% at 50% 50%)", background: "var(--glass)" }}
            />
            <GwenFace
              className="relative h-full w-full"
              variant="neon"
              expression="neutral"
              faceFill={false}
            />
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

export function landingAlreadyPlayed() {
  if (typeof window === "undefined") return true;
  return sessionStorage.getItem(KEY) === "1";
}
