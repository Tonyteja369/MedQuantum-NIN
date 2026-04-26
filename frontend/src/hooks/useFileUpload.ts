import { useState, useCallback } from 'react'
import { useDropzone, type Accept } from 'react-dropzone'
import { useECGStore } from '@/store/useECGStore'
import { uploadECGFile } from '@/api/ecgApi'

const ACCEPTED_TYPES: Accept = {
  'application/octet-stream': ['.dat', '.hea', '.mat', '.edf', '.csv'],
  'text/csv': ['.csv'],
  'text/plain': ['.hea'],
}

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50 MB

export function useFileUpload() {
  const [uploadProgress, setUploadProgress] = useState(0)
  const [fileId, setFileId] = useState<string | null>(null)

  const setUploadFile = useECGStore((s) => s.setUploadFile)
  const setUploadPreview = useECGStore((s) => s.setUploadPreview)
  const setUploadQuality = useECGStore((s) => s.setUploadQuality)
  const setUploadProcessing = useECGStore((s) => s.setUploadProcessing)
  const setUploadError = useECGStore((s) => s.setUploadError)
  const resetUpload = useECGStore((s) => s.resetUpload)

  const processFile = useCallback(
    async (file: File) => {
      setUploadFile(file)
      setUploadProcessing(true)
      setUploadError(null)
      setUploadProgress(0)

      try {
        console.debug(`[FileUpload] Processing: ${file.name} (${file.size} bytes)`)
        const result = await uploadECGFile(file, (pct) => {
          setUploadProgress(pct)
        })

        console.debug(
          `[FileUpload] Upload OK: id=${result.signalId}, ` +
          `leads=${result.signals.length}, ` +
          `first5=${result.signals[0]?.data.slice(0, 5).map(v => v.toFixed(3)).join(', ')}`
        )

        setFileId(result.signalId)
        // Waveform data comes directly from upload — no second round-trip needed
        setUploadPreview(result.signals)
        setUploadQuality(result.quality)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed'
        console.error('[FileUpload] Error:', message)
        setUploadError(message)
      } finally {
        setUploadProcessing(false)
      }
    },
    [setUploadFile, setUploadPreview, setUploadQuality, setUploadProcessing, setUploadError]
  )


  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop: (accepted) => {
      if (accepted[0]) processFile(accepted[0])
    },
    accept: ACCEPTED_TYPES,
    maxSize: MAX_FILE_SIZE,
    maxFiles: 1,
    onDropRejected: (rejections) => {
      const msg = rejections[0]?.errors[0]?.message ?? 'File rejected'
      setUploadError(msg)
    },
  })

  const clearFile = useCallback(() => {
    resetUpload()
    setFileId(null)
    setUploadProgress(0)
  }, [resetUpload])

  return {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    uploadProgress,
    fileId,
    clearFile,
    processFile,
  }
}
