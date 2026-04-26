import { motion } from 'framer-motion'
import { clsx } from 'clsx'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: string
  className?: string
  label?: string
}

const sizeMap = {
  sm: 16,
  md: 24,
  lg: 40,
  xl: 64,
}

export function Spinner({ size = 'md', color = 'var(--accent-primary)', className, label }: SpinnerProps) {
  const px = sizeMap[size]
  const stroke = size === 'sm' ? 2 : size === 'xl' ? 4 : 3

  return (
    <div className={clsx('flex flex-col items-center gap-3', className)}>
      <motion.svg
        width={px}
        height={px}
        viewBox="0 0 24 24"
        fill="none"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={stroke}
        />
        <path
          d="M12 2 A10 10 0 0 1 22 12"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
        />
      </motion.svg>
      {label && (
        <span className="text-sm text-[var(--text-secondary)] animate-pulse">{label}</span>
      )}
    </div>
  )
}

export function ECGSpinner({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-16 h-16">
        <motion.svg
          width="64"
          height="64"
          viewBox="0 0 64 64"
          className="absolute inset-0"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <circle cx="32" cy="32" r="28" stroke="rgba(0,212,255,0.1)" strokeWidth="3" fill="none" />
          <path d="M32 4 A28 28 0 0 1 60 32" stroke="#00d4ff" strokeWidth="3" strokeLinecap="round" fill="none" />
        </motion.svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="w-2 h-2 rounded-full bg-[#00d4ff]"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ duration: 1.4, repeat: Infinity }}
          />
        </div>
      </div>
      {label && (
        <p className="text-sm text-[var(--text-secondary)] animate-pulse font-medium">{label}</p>
      )}
    </div>
  )
}
