import { PageWrapper } from '@/components/layout/PageWrapper'
import { ECGAnimatedBackground } from '@/components/landing/ECGAnimatedBackground'
import { HeroSection } from '@/components/landing/HeroSection'
import { FeatureHighlights } from '@/components/landing/FeatureHighlights'
import { GitHubStarSection } from '@/components/landing/GitHubStarSection'

export default function LandingPage() {
  return (
    <PageWrapper>
      <div className="relative overflow-hidden">
        {/* Animated ECG background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <ECGAnimatedBackground />
          {/* Gradient overlays */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[var(--bg-primary)]" />
          <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-[var(--bg-primary)] to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10">
          <HeroSection />
          <FeatureHighlights />
          <GitHubStarSection />

          {/* Footer */}
          <footer className="py-12 px-6 text-center border-t border-[var(--border-secondary)]">
            <p className="text-sm text-[var(--text-muted)]">
              © {new Date().getFullYear()} MedQuantum-NIN. MIT License.{' '}
              <a
                href="https://github.com/MedQuantum-NIN/MedQuantum-NIN"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--accent-primary)] hover:underline"
              >
                GitHub
              </a>
            </p>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              For research and clinical decision support. Not a substitute for professional medical judgment.
            </p>
          </footer>
        </div>
      </div>
    </PageWrapper>
  )
}
