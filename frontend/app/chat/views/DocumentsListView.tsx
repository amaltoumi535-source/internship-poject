'use client'

import { useState, useEffect, useRef } from 'react'
import { FiUpload, FiFileText, FiSearch, FiMoreVertical, FiCheckCircle, FiLoader, FiAlertCircle } from 'react-icons/fi'
import { exportDocuments } from '../../../lib/api/reports'
import { apiClient } from '../../../lib/api/client'

interface Document {
  id: string
  name: string
  type: string
  uploadedAt: Date | null
}

function getFileType(filename: string): string {
  const ext = filename.split('.').pop()
  return ext ? ext.toUpperCase() : 'FILE'
}

interface DocumentsListViewProps {
  onSelectDoc: (id: string) => void
}

export default function DocumentsListView({ onSelectDoc }: DocumentsListViewProps) {
  const [search, setSearch] = useState('')
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openMenuId, setOpenMenuId] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    let cancelled = false

    async function loadDocuments() {
      setLoading(true)
      setError(null)
      try {
        const data = await exportDocuments('json', 1000, 0)
        if (cancelled) return
        const mapped: Document[] = data.rows.map(row => ({
          id: String(row.id),
          name: row.title ?? `Document ${row.id}`,
          type: getFileType(row.title ?? ''),
          uploadedAt: row.created_at ? new Date(row.created_at) : null,
        }))
        setDocuments(mapped)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load documents')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadDocuments()
    return () => {
      cancelled = true
    }
  }, [refreshKey])

  async function handleFileSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      await apiClient.uploadDocument(file)
      setRefreshKey(k => k + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const filtered = documents.filter(d => d.name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="flex-1 flex flex-col overflow-hidden" onClick={() => setOpenMenuId(null)}>
      {/* Header */}
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-[var(--text-primary)]">Documents</h1>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelected}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-medium rounded-xl transition-all shadow-lg shadow-blue-500/30 disabled:opacity-50"
        >
          {uploading ? <FiLoader className="w-4 h-4 animate-spin" /> : <FiUpload className="w-4 h-4" />}
          {uploading ? 'Uploading...' : 'Upload document'}
        </button>
      </div>

      {/* Search */}
      <div className="px-6 pt-4">
        <div className="relative max-w-md">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search documents..."
            className="w-full pl-9 pr-4 py-2.5 bg-[var(--surface-strong)] border border-[var(--border-strong)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50 text-sm"
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <FiLoader className="w-8 h-8 text-[var(--text-muted)] mx-auto mb-3 animate-spin" />
              <p className="text-[var(--text-secondary)]">Loading documents...</p>
            </div>
          </div>
        ) : error ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <FiAlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
              <p className="text-[var(--text-secondary)]">Couldn't load documents: {error}</p>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <FiFileText className="w-10 h-10 text-[var(--text-muted)] mx-auto mb-3" />
              <p className="text-[var(--text-secondary)]">
                {documents.length === 0 ? 'No documents yet' : 'No documents match your search'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map(doc => (
              <div
                key={doc.id}
                onClick={() => onSelectDoc(doc.id)}
                className="flex items-center gap-4 p-4 bg-[var(--surface-soft)] hover:bg-[var(--surface-strong)] border border-[var(--border-subtle)] rounded-xl cursor-pointer transition-all duration-200"
              >
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-lg flex items-center justify-center shrink-0">
                  <FiFileText className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate">{doc.name}</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {doc.type}{doc.uploadedAt ? ` · ${doc.uploadedAt.toLocaleDateString()}` : ''}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium text-emerald-400 bg-emerald-500/10 border-emerald-500/30">
                  <FiCheckCircle className="w-3.5 h-3.5" />
                  Indexed
                </div>
                <div className="relative">
                  <button
                    onClick={e => {
                      e.stopPropagation()
                      setOpenMenuId(openMenuId === doc.id ? null : doc.id)
                    }}
                    className="p-2 hover:bg-[var(--surface-strong)] rounded-lg transition-colors"
                  >
                    <FiMoreVertical className="w-4 h-4 text-[var(--text-muted)]" />
                  </button>
                  {openMenuId === doc.id && (
                    <div
                      onClick={e => e.stopPropagation()}
                      className="absolute right-0 top-full mt-1 w-40 bg-[var(--surface-strong)] border border-[var(--border-strong)] rounded-xl shadow-lg z-10 overflow-hidden"
                    >
                      <button
                        onClick={() => {
                          setOpenMenuId(null)
                          onSelectDoc(doc.id)
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--surface-hover-strong)]"
                      >
                        View details
                      </button>
                      <button
                        onClick={() => {
                          setOpenMenuId(null)
                          // handleDelete(doc.id) — wire once backend delete route exists
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/10"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}