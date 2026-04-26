import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Upload,
  BarChart2,
  FileText,
  ChevronLeft,
  ChevronRight,
  Heart,
  GitFork,
  Settings,
  Home,
} from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { Tooltip } from '@/components/ui/Tooltip'
import { clsx } from 'clsx'
import { useEffect, useState } from 'react'

interface NavItem {
  path: string
  label: string
  icon: React.ReactNode
  exact?: boolean
}

const navItems: NavItem[] = [
  { path: '/', label: 'Home', icon: <Home size={18} />, exact: true },
  { path: '/upload', label: 'Upload ECG', icon: <Upload size={18} /> },
  { path: '/analysis', label: 'Analysis', icon: <BarChart2 size={18} /> },
  { path: '/report', label: 'Report', icon: <FileText size={18} /> },
]

export function Sidebar() {
  const collapsed = useECGStore((s) => s.sidebarCollapsed)
  const toggleSidebar = useECGStore((s) => s.toggleSidebar)
  const location = useLocation()
  const [starCount, setStarCount] = useState<number | null>(null)

  useEffect(() => {
    fetch('https://api.github.com/repos/MedQuantum-NIN/MedQuantum-NIN')
      .then((r) => r.json())
      .then((d) => {
        if (typeof d.stargazers_count === 'number') setStarCount(d.stargazers_count)
      })
      .catch(() => {})
  }, [])

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-full z-40 flex flex-col glass border-r border-[var(--border-primary)] overflow-hidden"
    >
      {/* Logo */}
      <div
        className={clsx(
          'flex items-center h-16 px-4 border-b border-[var(--border-primary)] flex-shrink-0',
          collapsed ? 'justify-center' : 'justify-between'
        )}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="relative flex-shrink-0">
            <Heart
              size={24}
              className="text-[var(--accent-primary)] animate-heartbeat"
              fill="currentColor"
            />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.2 }}
                className="min-w-0"
              >
                <p className="text-sm font-bold text-[var(--text-primary)] leading-none">
                  MedQuantum
                </p>
                <p className="text-xs text-[var(--accent-primary)] font-mono mt-0.5">NIN</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto overflow-x-hidden">
        {navItems.map((item) => {
          const isActive = item.exact
            ? location.pathname === item.path
            : location.pathname.startsWith(item.path) && item.path !== '/'

          const content = (
            <NavLink
              key={item.path}
              to={item.path}
              className={clsx(
                'flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200',
                collapsed ? 'justify-center' : '',
                isActive
                  ? 'bg-[rgba(0,212,255,0.1)] text-[var(--accent-primary)] border border-[rgba(0,212,255,0.2)]'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5'
              )}
            >
              <span className={clsx('flex-shrink-0', isActive && 'text-[var(--accent-primary)]')}>
                {item.icon}
              </span>
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -4 }}
                    transition={{ duration: 0.15 }}
                    className="whitespace-nowrap overflow-hidden"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
              {isActive && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute left-0 w-0.5 h-8 bg-[var(--accent-primary)] rounded-full"
                  style={{ borderRadius: '0 2px 2px 0' }}
                />
              )}
            </NavLink>
          )

          return collapsed ? (
            <Tooltip key={item.path} content={item.label} placement="right">
              <div className="relative">{content}</div>
            </Tooltip>
          ) : (
            <div key={item.path} className="relative">{content}</div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-2 py-3 border-t border-[var(--border-primary)] space-y-1">
        {/* GitHub */}
        <a
          href="https://github.com/MedQuantum-NIN/MedQuantum-NIN"
          target="_blank"
          rel="noopener noreferrer"
          className={clsx(
            'flex items-center gap-3 rounded-md px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5 transition-all',
            collapsed ? 'justify-center' : ''
          )}
        >
          <GitFork size={16} className="flex-shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-1 whitespace-nowrap"
              >
                <span>GitHub</span>
                {starCount !== null && (
                  <span className="ml-auto text-xs bg-white/10 px-1.5 py-0.5 rounded font-mono">
                    ★ {starCount >= 1000 ? `${(starCount / 1000).toFixed(1)}k` : starCount}
                  </span>
                )}
              </motion.span>
            )}
          </AnimatePresence>
        </a>

        {/* Settings */}
        <button
          className={clsx(
            'w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5 transition-all',
            collapsed ? 'justify-center' : ''
          )}
        >
          <Settings size={16} className="flex-shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                Settings
              </motion.span>
            )}
          </AnimatePresence>
        </button>

        {/* Collapse toggle */}
        <button
          onClick={toggleSidebar}
          className={clsx(
            'w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-primary)] hover:bg-white/5 transition-all',
            collapsed ? 'justify-center' : ''
          )}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          <AnimatePresence>
            {!collapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                Collapse
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  )
}
