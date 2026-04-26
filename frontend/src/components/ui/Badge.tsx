import { clsx } from 'clsx'

type BadgeVariant = 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
type BadgeSize = 'sm' | 'md'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  size?: BadgeSize
  dot?: boolean
  className?: string
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-white/5 text-[var(--text-secondary)] border-white/10',
  primary: 'bg-[rgba(0,212,255,0.1)] text-[#00d4ff] border-[rgba(0,212,255,0.3)]',
  secondary: 'bg-[rgba(124,58,237,0.1)] text-[#7c3aed] border-[rgba(124,58,237,0.3)]',
  success: 'bg-[rgba(16,185,129,0.1)] text-[#10b981] border-[rgba(16,185,129,0.3)]',
  warning: 'bg-[rgba(251,191,36,0.1)] text-[#fbbf24] border-[rgba(251,191,36,0.3)]',
  danger: 'bg-[rgba(255,77,109,0.1)] text-[#ff4d6d] border-[rgba(255,77,109,0.3)]',
  info: 'bg-[rgba(99,179,237,0.1)] text-[#63b3ed] border-[rgba(99,179,237,0.3)]',
}

const dotColors: Record<BadgeVariant, string> = {
  default: 'bg-[var(--text-secondary)]',
  primary: 'bg-[#00d4ff]',
  secondary: 'bg-[#7c3aed]',
  success: 'bg-[#10b981]',
  warning: 'bg-[#fbbf24]',
  danger: 'bg-[#ff4d6d]',
  info: 'bg-[#63b3ed]',
}

export function Badge({ children, variant = 'default', size = 'md', dot = false, className }: BadgeProps) {
  const sizeClasses = size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-xs px-2.5 py-1'

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full border font-medium',
        sizeClasses,
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span className={clsx('inline-block w-1.5 h-1.5 rounded-full', dotColors[variant])} />
      )}
      {children}
    </span>
  )
}
