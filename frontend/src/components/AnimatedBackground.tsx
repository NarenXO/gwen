import { motion } from 'framer-motion'

const circles = [
  {
    color: '#ec4899',
    size: 500,
    opacity: 0.15,
    className: 'left-[-10%] top-[-5%]',
    duration: 20,
    animate: { x: [0, 50, -30, 0], y: [0, -40, 30, 0] },
  },
  {
    color: '#22d3ee',
    size: 600,
    opacity: 0.12,
    className: 'bottom-[-10%] right-[-5%]',
    duration: 25,
    animate: { x: [0, -50, 40, 0], y: [0, 50, -35, 0] },
  },
  {
    color: '#a855f7',
    size: 450,
    opacity: 0.1,
    className: 'right-[10%] top-[40%]',
    duration: 18,
    animate: { x: [0, -35, 45, 0], y: [0, 45, -50, 0] },
  },
] as const

export default function AnimatedBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {circles.map((circle) => (
        <motion.div
          key={circle.color}
          className={`absolute rounded-full ${circle.className}`}
          style={{
            width: circle.size,
            height: circle.size,
            backgroundColor: circle.color,
            opacity: circle.opacity,
            filter: 'blur(120px)',
          }}
          animate={circle.animate}
          transition={{
            duration: circle.duration,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}
