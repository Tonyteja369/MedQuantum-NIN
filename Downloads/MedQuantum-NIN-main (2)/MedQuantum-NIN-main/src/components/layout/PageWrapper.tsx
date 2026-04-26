import { motion } from 'framer-motion'
import { useECGStore } from '@/store/useECGStore'

interface PageWrapperProps {
  children: React.ReactNode
  className?: string
}

export function PageWrapper({ children, className = '' }: PageWrapperProps) {
  const collapsed = useECGStore((s) => s.sidebarCollapsed)
  const sidebarWidth = collapsed ? 64 : 240

  return (
    <motion.main
      animate={{ marginLeft: sidebarWidth }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={`min-h-screen pt-16 ${className}`}
      style={{ marginLeft: sidebarWidth }}
    >
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="h-full"
      >
        {children}
      </motion.div>
    </motion.main>
  )
}
