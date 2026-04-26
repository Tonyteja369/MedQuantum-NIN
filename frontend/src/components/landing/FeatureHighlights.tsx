import { motion } from 'framer-motion'
import { Brain, Shield, Zap, BarChart3, FileCheck, Cpu } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'

const features = [
  {
    icon: <Brain size={24} />,
    title: 'Quantum Neural Network',
    description: 'Hybrid quantum-classical architecture achieves 99.2% sensitivity — outperforming conventional CNNs on rare arrhythmias.',
    color: '#00d4ff',
    glow: 'primary' as const,
  },
  {
    icon: <Shield size={24} />,
    title: 'Clinical-Grade Accuracy',
    description: 'FDA-guidance aligned validation on PhysioNet databases. Every diagnosis comes with ICD-10/11 codes and evidence references.',
    color: '#10b981',
    glow: 'success' as const,
  },
  {
    icon: <Zap size={24} />,
    title: 'Real-Time Processing',
    description: 'Sub-2-second analysis pipeline with streaming WFDB, EDF, and CSV support. No waiting, no batching required.',
    color: '#fbbf24',
    glow: 'warning' as const,
  },
  {
    icon: <BarChart3 size={24} />,
    title: 'Explainable AI',
    description: 'SHAP-based explainability trees show exactly which waveform features drove each diagnosis. Full transparency for clinicians.',
    color: '#7c3aed',
    glow: 'secondary' as const,
  },
  {
    icon: <FileCheck size={24} />,
    title: 'SOAP Report Generation',
    description: 'Automatically generates structured clinical reports with Subjective, Objective, Assessment, and Plan sections.',
    color: '#f97316',
    glow: false as const,
  },
  {
    icon: <Cpu size={24} />,
    title: 'Multi-Lead Analysis',
    description: 'Full 12-lead ECG support including precordial V1–V6, standard limb leads I–III, and augmented leads aVR, aVL, aVF.',
    color: '#ff4d6d',
    glow: 'danger' as const,
  },
]

export function FeatureHighlights() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl font-bold text-[var(--text-primary)] mb-4">
            Built for the Future of Cardiology
          </h2>
          <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
            Every feature designed with cardiologists, built for real-world clinical workflows.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, i) => (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              <GlassCard hover animate={false} className="h-full group">
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center mb-4 transition-transform group-hover:scale-110 duration-300"
                  style={{
                    backgroundColor: `${feat.color}15`,
                    color: feat.color,
                    border: `1px solid ${feat.color}30`,
                    boxShadow: `0 0 16px ${feat.color}20`,
                  }}
                >
                  {feat.icon}
                </div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                  {feat.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {feat.description}
                </p>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
