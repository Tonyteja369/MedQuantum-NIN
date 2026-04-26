import { useState, useCallback } from 'react'
import { useDropzone, type Accept } from 'react-dropzone'
import { useECGStore } from '@/store/useECGStore'
import { uploadECGFile } from '@/api/ecgApi'

const ACCEPTED_TYPES: Accept = {
  'application/octet-stream': ['.dat', '.hea', '.edf', '.csv'],
  'text/csv': ['.csv'],
  'text/plain': ['.hea'],
}

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50 MB

function isAcceptedFile(file: File): boolean {
  const name = file.name.toLowerCase()
  return (
    name.endsWith('.csv') ||
    name.endsWith('.dat') ||
    name.endsWith('.hea') ||
    name.endsWith('.edf')
  )
}

export function useFileUpload() {
  const [uploadProgress, setUploadProgress] = useState(0)
  const [fileId, setFileId] = useState<string | null>(null)

  const setUploadFile = useECGStore((s) => s.setUploadFile)
  const setUploadFileId = useECGStore((s) => s.setUploadFileId)
  const setUploadPreview = useECGStore((s) => s.setUploadPreview)
  const setUploadQuality = useECGStore((s) => s.setUploadQuality)
  const setUploadProcessing = useECGStore((s) => s.setUploadProcessing)
  const setUploadError = useECGStore((s) => s.setUploadError)
  const setUploadSlicingMessages = useECGStore((s) => s.setUploadSlicingMessages)
  const resetUpload = useECGStore((s) => s.resetUpload)

  const processFile = useCallback(
    async (file: File) => {
      console.log('[UPLOAD FILE]', { name: file.name, size: file.size, type: file.type })
      setUploadFile(file)
      setUploadFileId(null)
      setUploadProcessing(true)
      setUploadError(null)
      setUploadProgress(0)

      try {
        const uploadResp = await uploadECGFile(file, (pct) => {
          setUploadProgress(pct)
        })
        const id = uploadResp.fileId
        setFileId(id)
        setUploadFileId(id)

        console.log('[UPLOAD OK]', uploadResp)
        console.log('[STORE FILE SET]', { fileId: id, file: file.name })

        setUploadPreview(uploadResp.preview)
        setUploadQuality(uploadResp.quality)
        setUploadSlicingMessages(uploadResp.slicingMessages || [])
      } catch (err) {
        console.log('[ERROR STACK]', err)
        const message = err instanceof Error ? err.message : 'Upload failed'
        setUploadError(message)
      } finally {
        setUploadProcessing(false)
      }
    },
    [setUploadFile, setUploadFileId, setUploadPreview, setUploadQuality, setUploadProcessing, setUploadError, setUploadSlicingMessages]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop: (accepted) => {
      console.log('[STORE FILE SET]', { acceptedCount: accepted.length, first: accepted[0]?.name ?? null })
      if (accepted[0]) processFile(accepted[0])
    },
    validator: (file) => (isAcceptedFile(file) ? null : { code: 'invalid-type', message: 'Unsupported file type' }),
    accept: ACCEPTED_TYPES,
    maxSize: MAX_FILE_SIZE,
    maxFiles: 1,
    onDropRejected: (rejections) => {
      console.log('[ERROR STACK]', rejections)
      const msg = rejections[0]?.errors[0]?.message ?? 'File rejected'
      setUploadError(msg)
    },
  })

  const clearFile = useCallback(() => {
    resetUpload()
    setFileId(null)
    setUploadFileId(null)
    setUploadProgress(0)
  }, [resetUpload, setUploadFileId])

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
