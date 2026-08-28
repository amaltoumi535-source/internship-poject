'use client'

import { useEffect, useState } from 'react'
import { FiArrowLeft, FiDownload, FiTrash2, FiFileText, FiHash, FiAlignLeft, FiAlertCircle, FiLoader } from 'react-icons/fi'
import { getDocReport, DocReport } from '../../../lib/api/reports'

interface DocumentDetailsViewProps {
  docId: string | null
  onBack: () => void
}

export default function DocumentDetailsView({ docId, onBack }: DocumentDetailsViewProps) {
  const [doc, setDoc] = useState<DocReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="p-2 hover:bg-[var(--surface-strong)] rounded-lg transition-colors">
            <FiArrowLeft className="w-5 h-5 text-[var(--text-secondary)]" />
          </button>
          <div>
            <h1 className="text-lg font-bold text-[var(--text-primary)] truncate max-w-md">
              {doc?.title ?? (docId ? `Document ${docId}` : 'Document')}
            </h1>
            <p className="text-xs text-[var(--text-muted)]">Document ID: {docId ?? '—'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-3 py-2 bg-[var(--surface-strong)] hover:bg-[var(--surface-hover-strong)] border border-[var(--border-strong)] rounded-xl text-sm text-[var(--text-secondary)] transition-all">
            <FiDownload className="w-4 h-4" />
            Download
          </button>
          <button className="flex items-center gap-2 px-3 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-xl text-sm text-red-400 transition-all">
            <FiTrash2 className="w-4 h-4" />
            Delete
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
            <FiAlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
            <p className="text-[var(--text-secondary)]">Couldn't load document: {error}</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Preview placeholder */}
          <div className="lg:col-span-2 bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl flex flex-col items-center justify-center min-h-[400px] p-8">
            <div className="p-6 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-2xl mb-4">
              <FiFileText className="w-12 h-12 text-blue-400" />
            </div>
            <p className="text-[var(--text-secondary)] text-sm text-center">
              Preview rendering isn't wired up yet — this panel will show the actual document once file storage is connected.
            </p>
          </div>

          {/* Metadata + snippets */}
          <div className="space-y-4">
            <div className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-3">Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiHash className="w-4 h-4 shrink-0" />
                  {doc?.chunk_count ?? 0} chunk{doc?.chunk_count === 1 ? '' : 's'}
                </div>
                <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                  <FiAlignLeft className="w-4 h-4 shrink-0" />
                  ~{Math.round(doc?.avg_chunk_length ?? 0)} chars avg per chunk
                </div>
              </div>
            </div>

            <div className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-3">Sample Snippets</h3>
              {doc?.sample_snippets && doc.sample_snippets.length > 0 ? (
                <div className="space-y-3">
                  {doc.sample_snippets.map((snippet, i) => (
                    <p key={i} className="text-sm text-[var(--text-secondary)] leading-relaxed border-l-2 border-[var(--border-subtle)] pl-3">
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