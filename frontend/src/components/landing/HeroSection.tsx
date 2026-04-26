import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Activity, ArrowRight, Zap } from 'lucide-react'
import { CTAButtons } from './CTAButtons'

export function HeroSection() {
  const navigate = useNavigate()

  return (
    <section className="relative min-h-[90vh] flex flex-col items-center justify-center text-center px-6 py-20">
      {/* Badge */}
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="inline-flex items-center gap-2 mb-8 px-4 py-2 rounded-full glass border border-[rgba(0,212,255,0.2)] text-sm text-[var(--accent-primary)]"
      >
        <Zap size={14} className="animate-pulse" />
        <span>Quantum-Enhanced AI • v2.1 Now Available</span>
        <ArrowRight size={12} />
      </motion.div>

      {/* Headline */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-5xl md:text-7xl font-extrabold leading-tight mb-6"
      >
        <span className="text-[var(--text-primary)]">AI-Powered </span>
        <span className="text-gradient">ECG Analysis</span>
        <br />
        <span className="text-[var(--text-primary)]">for Modern Medicine</span>
      </motion.h1>

      {/* Sub */}
      <motion.p
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="max-w-2xl mx-auto text-lg text-[var(--text-secondary)] mb-10 leading-relaxed"
      >
        MedQuantum-NIN combines quantum computing with deep learning to deliver
        clinical-grade cardiac diagnostics with full explainability in under 2 seconds.
      </motion.p>

      {/* Stats row */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex flex-wrap items-center justify-center gap-8 mb-12"
      >
        {[
          { value: '99.2%', label: 'Sensitivity' },
          { value: '<2s', label: 'Analysis Time' },
          { value: '14', label: 'Lead Support' },
          { value: '50+', label: 'Conditions Detected' },
        ].map((stat) => (
          <div key={stat.label} className="text-center">
            <div className="text-3xl font-bold text-[var(--accent-primary)] font-mono">
              {stat.value}
            </div>
            <div className="text-sm text-[var(--text-muted)] mt-0.5">{stat.label}</div>
          </div>
        ))}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <CTAButtons />
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center pt-2"
        >
          <div className="w-1 h-2 bg-[var(--accent-primary)] rounded-full" />
        </motion.div>
      </motion.div>
    </section>
  )
}
