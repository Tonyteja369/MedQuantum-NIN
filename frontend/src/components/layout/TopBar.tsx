import { Activity, Bell, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import { ThemeToggle } from './ThemeToggle'
import { useECGStore } from '@/store/useECGStore'
import { StatusDot } from '@/components/ui/StatusDot'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/upload': 'Upload ECG',
  '/analysis': 'ECG Analysis',
  '/report': 'Clinical Report',
}

const ECG_PATH = 'M0,32 L8,32 L12,12 L16,52 L20,24 L24,40 L28,32 L80,32'

export function TopBar() {
  const collapsed = useECGStore((s) => s.sidebarCollapsed)
  const location = useLocation()
  const title = pageTitles[location.pathname] ?? 'MedQuantum-NIN'

  const sidebarWidth = collapsed ? 64 : 240

  return (
    <motion.header
      animate={{ left: sidebarWidth }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed top-0 right-0 z-30 h-16 glass border-b border-[var(--border-primary)] flex items-center px-6 gap-4"
      style={{ left: sidebarWidth }}
    >
      {/* Live ECG mini animation */}
      <div className="hidden sm:flex items-center gap-2 mr-2">
        <svg
          width="80"
          height="32"
          viewBox="0 0 80 32"
          className="overflow-visible opacity-70"
        >
          <motion.path
            d={ECG_PATH}
            fill="none"
            stroke="var(--accent-primary)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeDasharray="200"
            animate={{ strokeDashoffset: [200, 0, -200] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
          />
        </svg>
        <StatusDot status="online" pulse size="sm" />
      </div>

      {/* Page title */}
      <div className="flex-1 min-w-0">
        <h1 className="text-base font-semibold text-[var(--text-primary)] truncate">{title}</h1>
        <p className="text-xs text-[var(--text-muted)] font-mono hidden sm:block">
          MedQuantum-NIN • Quantum ECG Analysis
        </p>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-2">
        {/* Search (decorative) */}
        <button className="p-2 rounded-md text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5 transition-colors">
          <Search size={16} />
        </button>

        {/* Notifications */}
        <button className="relative p-2 rounded-md text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5 transition-colors">
          <Bell size={16} />
          <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-[var(--accent-danger)] rounded-full" />
        </button>

        <ThemeToggle />

        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center text-xs font-bold text-white cursor-pointer">
          <Activity size={14} />
        </div>
      </div>
    </motion.header>
  )
}
