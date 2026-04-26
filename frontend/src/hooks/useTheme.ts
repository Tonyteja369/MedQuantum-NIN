import { useEffect } from 'react'
import { useECGStore } from '@/store/useECGStore'
import type { Theme } from '@/types/ecg.types'

export function useTheme() {
  const theme = useECGStore((s) => s.theme)
  const setTheme = useECGStore((s) => s.setTheme)
  const toggleTheme = useECGStore((s) => s.toggleTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  const applyTheme = (t: Theme) => {
    setTheme(t)
    document.documentElement.setAttribute('data-theme', t)
  }

  return { theme, setTheme: applyTheme, toggleTheme, isDark: theme === 'dark' }
}
