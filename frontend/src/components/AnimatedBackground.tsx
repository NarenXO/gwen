import { motion, type Easing } from "framer-motion";

const EASE: Easing = "easeInOut";

export default function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      {/* Circle 1 (Pink) */}
      <motion.div
        className="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] rounded-full bg-pink-500/20 blur-[120px]"
        animate={{
          x: [-30, 30, -30],
          y: [-40, 40, -40],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: EASE,
        }}
      />

      {/* Circle 2 (Cyan) */}
      <motion.div
        className="absolute bottom-[-10%] right-[-5%] w-[600px] h-[600px] rounded-full bg-cyan-500/15 blur-[130px]"
        animate={{
          x: [40, -40, 40],
          y: [30, -30, 30],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: EASE,
        }}
      />

      {/* Circle 3 (Purple) */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[450px] h-[450px] rounded-full bg-purple-500/15 blur-[120px]"
        animate={{
          scale: [1, 1.15, 1],
          x: [-20, 20, -20],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: EASE,
        }}
      />
    </div>
  );
}