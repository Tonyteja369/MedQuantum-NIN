import { useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, FileCheck, AlertCircle } from 'lucide-react'
import { useFileUpload } from '@/hooks/useFileUpload'
import { useECGStore } from '@/store/useECGStore'
import { formatFileSize } from '@/utils/formatters'
import { Spinner } from '@/components/ui/Spinner'

export function DropZone() {
  const { getRootProps, getInputProps, isDragActive, isDragReject, uploadProgress, clearFile } =
    useFileUpload()
  const { file, isProcessing, error, slicingMessages } = useECGStore((s) => s.uploadState)

  const borderColor = isDragReject
    ? 'rgba(255,77,109,0.6)'
    : isDragActive
    ? 'rgba(0,212,255,0.6)'
    : file
    ? 'rgba(16,185,129,0.4)'
    : 'rgba(255,255,255,0.08)'

  const bgColor = isDragReject
    ? 'rgba(255,77,109,0.05)'
    : isDragActive
    ? 'rgba(0,212,255,0.05)'
    : 'rgba(255,255,255,0.02)'

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className="relative rounded-xl border-2 border-dashed transition-all duration-300 cursor-pointer"
        style={{ borderColor, backgroundColor: bgColor }}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center justify-center py-14 px-8 text-center">
          <AnimatePresence mode="wait">
            {isProcessing ? (
              <motion.div
                key="processing"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-4"
              >
                <Spinner size="lg" label={
                  uploadProgress < 30 ? "Uploading file..." :
                  uploadProgress < 60 ? "Parsing ECG signal..." :
                  uploadProgress < 90 ? "Processing waveform..." :
                  "Finalizing..."
                } />
                <div className="w-48 bg-white/5 rounded-full h-1.5 overflow-hidden">
                  <motion.div
                    className="h-full bg-[var(--accent-primary)] rounded-full"
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
                <p className="text-xs text-[var(--text-muted)]">{uploadProgress}%</p>
              </motion.div>
            ) : file ? (
              <motion.div
                key="file"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-3"
              >
                <FileCheck size={40} className="text-[var(--accent-success)]" />
                <div>
                  <p className="font-semibold text-[var(--text-primary)]">{file.name}</p>
                  <p className="text-sm text-[var(--text-muted)]">{formatFileSize(file.size)}</p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); clearFile() }}
                  className="flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--accent-danger)] transition-colors"
                >
                  <X size={12} /> Remove file
                </button>
              </motion.div>
            ) : (
              <motion.div
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-4"
              >
                <motion.div
                  animate={isDragActive ? { scale: 1.15 } : { scale: 1 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
                  className="w-16 h-16 rounded-2xl flex items-center justify-center"
                  style={{
                    background: 'rgba(0,212,255,0.08)',
                    border: '1px solid rgba(0,212,255,0.2)',
                    boxShadow: isDragActive ? '0 0 24px rgba(0,212,255,0.3)' : undefined,
                  }}
                >
                  <Upload size={28} className="text-[var(--accent-primary)]" />
                </motion.div>
                <div>
                  <p className="text-base font-semibold text-[var(--text-primary)]">
                    {isDragActive ? 'Drop your ECG file here' : 'Upload ECG File'}
                  </p>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">
                    Drag & drop or click to browse
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-2">
                    Supports WFDB (.dat/.hea), EDF, CSV • Max 50MB
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 p-3 rounded-lg text-sm"
            style={{ background: 'rgba(255,77,109,0.1)', border: '1px solid rgba(255,77,109,0.3)', color: '#ff4d6d' }}
          >
            <AlertCircle size={14} className="flex-shrink-0" />
            {error}
          </motion.div>
        )}
        
        {slicingMessages && slicingMessages.length > 0 && (
          <AnimatePresence>
            {slicingMessages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2 p-3 rounded-lg text-sm"
                style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00d4ff' }}
              >
                <AlertCircle size={14} className="flex-shrink-0" />
                {message}
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </AnimatePresence>
    </div>
  )
}
