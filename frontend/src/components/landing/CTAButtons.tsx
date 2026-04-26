import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Upload, BookOpen, ArrowRight } from 'lucide-react'

export function CTAButtons() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-wrap items-center justify-center gap-4">
      <motion.button
        onClick={() => navigate('/upload')}
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
        className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-base font-semibold transition-all duration-200"
        style={{
          background: 'linear-gradient(135deg, #00d4ff, #7c3aed)',
          color: '#fff',
          boxShadow: '0 0 24px rgba(0,212,255,0.35)',
        }}
      >
        <Upload size={18} />
        Analyze ECG Now
        <ArrowRight size={16} />
      </motion.button>

      <motion.a
        href="https://github.com/MedQuantum-NIN/MedQuantum-NIN"
        target="_blank"
        rel="noopener noreferrer"
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
        className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-base font-semibold transition-all duration-200 glass border border-[var(--border-primary)] text-[var(--text-primary)] hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)]"
      >
        <BookOpen size={18} />
        Read the Docs
      </motion.a>
    </div>
  )
}
