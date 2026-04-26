import React from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: Parameters<typeof clsx>) {
  return twMerge(clsx(inputs))
}

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  hover?: boolean
  glow?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | false
  padding?: 'none' | 'sm' | 'md' | 'lg'
  animate?: boolean
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, hover = false, glow = false, padding = 'md', animate = true, className, ...props }, ref) => {
    const paddingClasses = {
      none: '',
      sm: 'p-3',
      md: 'p-5',
      lg: 'p-8',
    }

    const glowStyles: Record<string, string> = {
      primary: '0 0 20px rgba(0,212,255,0.2)',
      secondary: '0 0 20px rgba(124,58,237,0.2)',
      danger: '0 0 20px rgba(255,77,109,0.2)',
      success: '0 0 20px rgba(16,185,129,0.2)',
      warning: '0 0 20px rgba(251,191,36,0.2)',
    }

    const content = (
      <div
        ref={ref}
        className={cn(
          'glass rounded-lg border transition-all duration-300',
          paddingClasses[padding],
          hover && 'cursor-pointer hover:border-white/15 hover:bg-white/5',
          className
        )}
        style={glow ? { boxShadow: glowStyles[glow] } : undefined}
        {...props}
      >
        {children}
      </div>
    )

    if (!animate) return content

    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      >
        {content}
      </motion.div>
    )
  }
)

GlassCard.displayName = 'GlassCard'
