import { motion } from 'framer-motion'
import { Sun, Moon } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

export function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme()

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-14 h-7 rounded-full p-0.5 transition-colors focus-visible:outline-none"
      style={{
        backgroundColor: isDark ? 'rgba(0,212,255,0.15)' : 'rgba(251,191,36,0.15)',
        border: `1px solid ${isDark ? 'rgba(0,212,255,0.3)' : 'rgba(251,191,36,0.3)'}`,
      }}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      whileTap={{ scale: 0.95 }}
    >
      {/* Track icons */}
      <div className="absolute inset-0 flex items-center justify-between px-1.5 pointer-events-none">
        <Sun size={12} className="text-[#fbbf24] opacity-60" />
        <Moon size={12} className="text-[#00d4ff] opacity-60" />
      </div>

      {/* Thumb */}
      <motion.div
        className="relative z-10 w-6 h-6 rounded-full flex items-center justify-center shadow-md"
        style={{
          backgroundColor: isDark ? '#00d4ff' : '#fbbf24',
        }}
        animate={{ x: isDark ? 28 : 0 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      >
        {isDark ? (
          <Moon size={12} className="text-[#0a0e1a]" />
        ) : (
          <Sun size={12} className="text-[#0a0e1a]" />
        )}
      </motion.div>
    </motion.button>
  )
}
