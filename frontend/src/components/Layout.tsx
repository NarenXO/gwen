import { motion } from 'framer-motion'
import {
  BarChart3,
  LayoutDashboard,
  MessageSquare,
  Upload,
  Video,
} from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import AnimatedBackground from './AnimatedBackground'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/analytics', label: 'Analytics', icon: BarChart3, end: false },
  { to: '/studio', label: 'Studio', icon: Video, end: false },
  { to: '/comments', label: 'Comments', icon: MessageSquare, end: false },
  { to: '/upload', label: 'Upload', icon: Upload, end: false },
] as const

export default function Layout() {
  const location = useLocation()

  return (
    <div className="relative min-h-screen">
      <AnimatedBackground />

      <aside className="fixed left-0 top-0 z-20 flex h-screen w-64 flex-col border-r border-white/10 bg-slate-900/60 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-6 py-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-pink-500 to-cyan-500">
            <span className="text-lg font-bold text-white">G</span>
          </div>
          <span className="text-xl font-bold text-white">GWEN</span>
        </div>

        <nav className="flex flex-1 flex-col gap-1 px-4">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-xl px-4 py-3 text-slate-400 transition-all hover:bg-white/5 hover:text-white',
                  isActive
                    ? 'border-l-2 border-pink-500 bg-gradient-to-r from-pink-500/20 to-cyan-500/10 text-white shadow-[0_0_20px_rgba(236,72,153,0.25)]'
                    : 'border-l-2 border-transparent',
                ].join(' ')
              }
            >
              {({ isActive }) => (
                <motion.div
                  className="flex w-full items-center gap-3"
                  whileHover={{ x: 4 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                >
                  <Icon
                    className={`h-5 w-5 ${isActive ? 'text-pink-400' : ''}`}
                  />
                  <span className="font-medium">{label}</span>
                </motion.div>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-pink-500 to-purple-500">
              <span className="text-sm font-bold text-white">K</span>
            </div>
            <div>
              <p className="text-sm font-medium text-white">Kavya</p>
              <p className="text-xs text-slate-400">Free Plan</p>
            </div>
          </div>
        </div>
      </aside>

      <main className="relative z-10 ml-64 min-h-screen p-8">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}
