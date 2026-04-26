import { motion } from 'framer-motion'
import { Star, GitFork, Eye } from 'lucide-react'
import { useEffect, useState } from 'react'

interface RepoStats {
  stars: number
  forks: number
  watchers: number
}

export function GitHubStarSection() {
  const [stats, setStats] = useState<RepoStats>({ stars: 0, forks: 0, watchers: 0 })

  useEffect(() => {
    fetch('https://api.github.com/repos/MedQuantum-NIN/MedQuantum-NIN')
      .then((r) => r.json())
      .then((d) => {
        if (d.stargazers_count != null) {
          setStats({
            stars: d.stargazers_count,
            forks: d.forks_count,
            watchers: d.watchers_count,
          })
        }
      })
      .catch(() => {})
  }, [])

  return (
    <section className="py-16 px-6">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="glass rounded-xl border border-[rgba(255,255,255,0.08)] p-8 text-center"
          style={{ boxShadow: '0 0 40px rgba(0,212,255,0.08)' }}
        >
          <div className="text-4xl mb-4">⭐</div>
          <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-3">
            Open Source & Free Forever
          </h2>
          <p className="text-[var(--text-secondary)] mb-8 max-w-lg mx-auto">
            MedQuantum-NIN is MIT licensed. Star us on GitHub to support the project and
            get notified of new model releases and features.
          </p>

          <div className="flex flex-wrap justify-center gap-6 mb-8">
            {[
              { icon: <Star size={18} />, value: stats.stars, label: 'Stars' },
              { icon: <GitFork size={18} />, value: stats.forks, label: 'Forks' },
              { icon: <Eye size={18} />, value: stats.watchers, label: 'Watching' },
            ].map((s) => (
              <div
                key={s.label}
                className="flex items-center gap-2 px-4 py-2 glass rounded-lg border border-[var(--border-primary)]"
              >
                <span className="text-[var(--accent-primary)]">{s.icon}</span>
                <span className="font-mono font-bold text-[var(--text-primary)]">
                  {s.value.toLocaleString()}
                </span>
                <span className="text-sm text-[var(--text-muted)]">{s.label}</span>
              </div>
            ))}
          </div>

          <a
            href="https://github.com/MedQuantum-NIN/MedQuantum-NIN"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-semibold text-sm transition-all duration-200 hover:scale-105 active:scale-95"
            style={{
              background: 'linear-gradient(135deg, rgba(0,212,255,0.2), rgba(124,58,237,0.2))',
              border: '1px solid rgba(0,212,255,0.3)',
              color: 'var(--accent-primary)',
            }}
          >
            <Star size={16} />
            Star on GitHub
          </a>
        </motion.div>
      </div>
    </section>
  )
}
