import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Sidebar } from '@/components/layout/Sidebar'
import { TopBar } from '@/components/layout/TopBar'
import LandingPage from '@/pages/LandingPage'
import UploadDashboard from '@/pages/UploadDashboard'
import AnalysisDashboard from '@/pages/AnalysisDashboard'
import ReportPage from '@/pages/ReportPage'
import { useTheme } from '@/hooks/useTheme'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
})

function DemoNavigationHandler() {
  const navigate = useNavigate()

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent<string>).detail
      if (detail) navigate(detail)
    }
    window.addEventListener('demo-navigate', handler)
    return () => window.removeEventListener('demo-navigate', handler)
  }, [navigate])

  return null
}

function AppLayout() {
  const location = useLocation()
  useTheme()

  return (
    <div className="flex min-h-screen bg-[var(--bg-primary)]">
      <Sidebar />
      <TopBar />
      <DemoNavigationHandler />
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/upload" element={<UploadDashboard />} />
          <Route path="/analysis" element={<AnalysisDashboard />} />
          <Route path="/report" element={<ReportPage />} />
        </Routes>
      </AnimatePresence>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
