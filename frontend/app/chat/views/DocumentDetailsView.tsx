'use client'

import { useEffect, useState } from 'react'
import { FiArrowLeft, FiDownload, FiTrash2, FiFileText, FiHash, FiAlignLeft, FiAlertCircle, FiLoader, FiCalendar, FiHardDrive, FiFile, FiBookOpen } from 'react-icons/fi'
import { getDocReport, DocReport } from '../../../lib/api/reports'
import { apiClient } from '../../../lib/api/client'

interface DocumentDetailsViewProps {
  docId: string | null
  onBack: () => void
}

function formatBytes(bytes: number | null): string {
  if (bytes === null || bytes === undefined) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function DocumentDetailsView({ docId, onBack }: DocumentDetailsViewProps) {
  const [doc, setDoc] = useState<DocReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  useEffect(() => {
    if (!docId) {
      setLoading(false)
      setError('No document selected')
      return
    }

    let cancelled = false
    async function loadDoc() {
      setLoading(true)
      setError(null)
      try {
        const data = await getDocReport(Number(docId), 5)
        if (!cancelled) setDoc(data)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load document')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadDoc()
    return () => {
      cancelled = true
    }
  }, [docId])

  // Load the preview blob once we know the doc is a PDF — separate effect
  // so it only fires after `doc` (and its mime type) is known.
  useEffect(() => {
    if (!docId || !doc) return

    const isPdf = doc.mime === 'application/pdf' || doc.title?.toLowerCase().endsWith('.pdf')
    if (!isPdf) return

    let cancelled = false
    let objectUrl: string | null = null

    async function loadPreview() {
      setPreviewLoading(true)
      try {
        const url = await apiClient.getDocumentFileBlobUrl(docId!)
        if (cancelled) {
          URL.revokeObjectURL(url)
          return
        }
        objectUrl = url
        setPreviewUrl(url)
      } catch {
        if (!cancelled) setPreviewUrl(null)
      } finally {
        if (!cancelled) setPreviewLoading(false)
      }
    }

    loadPreview()
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [docId, doc])

  async function handleDelete() {
    if (!docId) return
    if (!confirm('Delete this document? This cannot be undone.')) return
    setDeleting(true)
    try {
      await apiClient.deleteDocument(docId)
      onBack()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
      setDeleting(false)
    }
  }

  async function handleDownload() {
    if (!docId || !doc) return
    setDownloading(true)
    try {
      await apiClient.downloadDocumentFile(docId, doc.title ?? `document_${docId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed')
    } finally {
      setDownloading(false)
    }
  }

  const isPdf = doc?.mime === 'application/pdf' || doc?.title?.toLowerCase().endsWith('.pdf')

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4 min-w-0">
          <button onClick={onBack} className="p-2 hover:bg-[var(--surface-strong)] rounded-lg transition-colors shrink-0">
            <FiArrowLeft className="w-5 h-5 text-[var(--text-secondary)]" />
          </button>
          <div className="min-w-0">
            <h1 className="text-lg font-bold text-[var(--text-primary)] truncate max-w-md">
              {doc?.title ?? (docId ? `Document ${docId}` : 'Document')}
            </h1>
            <p className="text-xs text-[var(--text-muted)]">Document ID: {docId ?? '—'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleDownload}
            disabled={!docId || downloading}
            className="flex items-center gap-2 px-3 py-2 bg-[var(--surface-strong)] hover:bg-[var(--surface-hover-strong)] border border-[var(--border-strong)] rounded-xl text-sm text-[var(--text-secondary)] transition-all disabled:opacity-50"
          >
            {downloading ? <FiLoader className="w-4 h-4 animate-spin" /> : <FiDownload className="w-4 h-4" />}
            {downloading ? 'Downloading...' : 'Download'}
          </button>
          <button
            onClick={handleDelete}
            disabled={!docId || deleting}
            className="flex items-center gap-2 px-3 py-2 bg-red-50 hover:bg-red-100 border border-red-200 rounded-xl text-sm text-red-600 transition-all disabled:opacity-50"
          >
            {deleting ? <FiLoader className="w-4 h-4 animate-spin" /> : <FiTrash2 className="w-4 h-4" />}
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <FiLoader className="w-8 h-8 text-[var(--text-muted)] mx-auto mb-3 animate-spin" />
            <p className="text-[var(--text-secondary)]">Loading document...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <FiAlertCircle className="w-10 h-10 text-red-500 mx-auto mb-3" />
            <p className="text-[var(--text-secondary)]">Couldn't load document: {error}</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
          {/* Preview */}
          <div className="lg:col-span-2 bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl overflow-hidden min-h-[400px]">
            {isPdf && previewLoading ? (
              <div className="flex items-center justify-center h-full min-h-[400px]">
                <FiLoader className="w-6 h-6 text-[var(--text-muted)] animate-spin" />
              </div>
            ) : isPdf && previewUrl ? (
              <iframe src={previewUrl} title="Document preview" className="w-full h-full min-h-[500px] border-0" />
            ) : (
              <div className="flex flex-col items-center justify-center h-full min-h-[400px] p-8">
                <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center mb-4">
                  <FiFileText className="w-7 h-7 text-indigo-500" />
                </div>
                <p className="text-[var(--text-secondary)] text-sm text-center">
                  Inline preview isn't available for this file type.
                </p>
              </div>
            )}
          </div>

          {/* Metadata + snippets */}
          <div className="space-y-4">
            <div className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
              <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-3">Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiCalendar className="w-4 h-4 shrink-0 text-indigo-500" />
                  {doc?.created_at ? new Date(doc.created_at).toLocaleDateString() : 'Unknown date'}
                </div>
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiHardDrive className="w-4 h-4 shrink-0 text-indigo-500" />
                  {formatBytes(doc?.size_bytes ?? null)}
                </div>
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiFile className="w-4 h-4 shrink-0 text-indigo-500" />
                  {doc?.mime ?? 'Unknown type'}
                </div>
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiBookOpen className="w-4 h-4 shrink-0 text-indigo-500" />
                  {doc?.page_count != null ? `${doc.page_count} page${doc.page_count === 1 ? '' : 's'}` : 'Page count unavailable'}
                </div>
              </div>
            </div>

            <div className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
              <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-3">Indexing</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiHash className="w-4 h-4 shrink-0 text-indigo-500" />
                  {doc?.chunk_count ?? 0} chunk{doc?.chunk_count === 1 ? '' : 's'}
                </div>
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiAlignLeft className="w-4 h-4 shrink-0 text-indigo-500" />
                  ~{Math.round(doc?.avg_chunk_length ?? 0)} chars avg per chunk
                </div>
              </div>
            </div>

            <div className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
              <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-3">Sample snippets</h3>
              {doc?.sample_snippets && doc.sample_snippets.length > 0 ? (
                <div className="space-y-3">
                  {doc.sample_snippets.map((snippet, i) => (
                    <p key={i} className="text-sm text-[var(--text-secondary)] leading-relaxed border-l-2 border-indigo-200 pl-3">
                      {snippet}
                    </p>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-[var(--text-muted)]">No snippets available.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}