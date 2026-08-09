import { motion } from "framer-motion";

import { StaticGwenLogo } from "@/components/gwen/StaticGwenLogo";

export function HomeHero({ hideLogo = false }: { hideLogo?: boolean }) {
  return (
    <div className="relative flex min-h-screen flex-col items-center md:flex-row">
      {/* Left half: GWEN mark only — no panel/box, web animation stays visible around it */}
      <div className="flex w-full items-center justify-center py-16 md:h-screen md:w-1/2 md:py-0">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: hideLogo ? 0 : 1 }}
          transition={{ duration: 0 }}
          className="relative flex aspect-[120/140] w-[min(90vw,75vh,36rem)] items-center justify-center md:w-[min(50vw,85vh,48rem)] shrink-0"
        >
          {/* Frosted glass fill, clipped to the face silhouette itself */}
          <div
            className="absolute inset-0 backdrop-blur-xl backdrop-saturate-150"
            style={{
              clipPath: "url(#static-gwen-face-clip)",
              background: "var(--glass)",
            }}
          />
          <StaticGwenLogo
            className="relative h-full w-full"
            variant="neon"
            faceFill={false}
          />
        </motion.div>
      </div>

      {/* Right half: welcome copy */}
      <div className="flex w-full items-center px-6 py-16 md:h-screen md:w-1/2 md:px-14">
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.9 }}
          className="text-5xl leading-[1.05] font-semibold sm:text-6xl lg:text-7xl"
        >
          Welcome to <span className="neon-text">GWEN.</span>
        </motion.h1>
      </div>
    </div>
  );
}
