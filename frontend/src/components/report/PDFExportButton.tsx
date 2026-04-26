import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Download, Loader2, CheckCircle } from 'lucide-react'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import { useECGStore } from '@/store/useECGStore'
import { formatTimestamp } from '@/utils/formatters'

type ExportState = 'idle' | 'generating' | 'done' | 'error'

export function PDFExportButton() {
  const [state, setState] = useState<ExportState>('idle')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const report = useECGStore((s) => s.reportData)

  const handleExport = async () => {
    if (!report) return
    setState('generating')
    setErrorMsg(null)

    try {
      const reportEl = document.getElementById('report-content')
      if (!reportEl) throw new Error('Report content not found')

      const canvas = await html2canvas(reportEl, {
        scale: 2,
        backgroundColor: '#0a0e1a',
        useCORS: true,
        logging: false,
      })

      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      })

      const pageWidth = 210
      const pageHeight = 297
      const imgWidth = pageWidth
      const imgHeight = (canvas.height * imgWidth) / canvas.width

      // Header
      pdf.setFillColor(10, 14, 26)
      pdf.rect(0, 0, pageWidth, pageHeight, 'F')
      pdf.setTextColor(0, 212, 255)
      pdf.setFontSize(18)
      pdf.text('MedQuantum-NIN — ECG Analysis Report', pageWidth / 2, 15, { align: 'center' })
      pdf.setTextColor(136, 146, 176)
      pdf.setFontSize(10)
      pdf.text(`Generated: ${formatTimestamp(report.generatedAt)}`, pageWidth / 2, 22, { align: 'center' })
      pdf.text(`Analysis ID: ${report.analysisId}`, pageWidth / 2, 27, { align: 'center' })

      const yOffset = 32
      const availHeight = pageHeight - yOffset - 10

      if (imgHeight <= availHeight) {
        pdf.addImage(canvas.toDataURL('image/jpeg', 0.9), 'JPEG', 0, yOffset, imgWidth, imgHeight)
      } else {
        // Multi-page
        let heightLeft = imgHeight
        let position = yOffset

        pdf.addImage(canvas.toDataURL('image/jpeg', 0.9), 'JPEG', 0, position, imgWidth, imgHeight)
        heightLeft -= availHeight

        while (heightLeft > 0) {
          pdf.addPage()
          pdf.setFillColor(10, 14, 26)
          pdf.rect(0, 0, pageWidth, pageHeight, 'F')
          position = -(imgHeight - heightLeft) + yOffset
          pdf.addImage(canvas.toDataURL('image/jpeg', 0.9), 'JPEG', 0, position, imgWidth, imgHeight)
          heightLeft -= pageHeight
        }
      }

      // Footer
      const pageCount = pdf.getNumberOfPages()
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i)
        pdf.setFontSize(8)
        pdf.setTextColor(74, 85, 104)
        pdf.text(
          'MedQuantum-NIN • AI-Powered ECG Analysis • For Clinical Use Only',
          pageWidth / 2,
          pageHeight - 5,
          { align: 'center' }
        )
        pdf.text(`Page ${i} of ${pageCount}`, pageWidth - 15, pageHeight - 5)
      }

      pdf.save(`ecg-report-${report.analysisId}.pdf`)
      setState('done')
      setTimeout(() => setState('idle'), 3000)
    } catch (err) {
      console.error('PDF export failed', err)
      setErrorMsg(err instanceof Error ? err.message : 'Export failed')
      setState('error')
      setTimeout(() => setState('idle'), 4000)
    }
  }

  const buttonContent = {
    idle: { icon: <Download size={16} />, label: 'Export PDF', color: 'var(--accent-primary)' },
    generating: { icon: <Loader2 size={16} className="animate-spin" />, label: 'Generating…', color: 'var(--accent-warning)' },
    done: { icon: <CheckCircle size={16} />, label: 'Downloaded!', color: 'var(--accent-success)' },
    error: { icon: <Download size={16} />, label: errorMsg ?? 'Retry', color: 'var(--accent-danger)' },
  }[state]

  return (
    <motion.button
      onClick={handleExport}
      disabled={state === 'generating' || !report}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      style={{
        background: `${buttonContent.color}15`,
        border: `1px solid ${buttonContent.color}40`,
        color: buttonContent.color,
        boxShadow: state === 'idle' ? `0 0 12px ${buttonContent.color}20` : undefined,
      }}
    >
      {buttonContent.icon}
      {buttonContent.label}
    </motion.button>
  )
}
