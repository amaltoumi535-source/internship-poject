'use client'

import { useEffect, useState } from 'react'
import { FiPlus, FiFolder, FiFileText, FiMessageSquare, FiMoreVertical, FiLoader, FiAlertCircle } from 'react-icons/fi'
import { getProjects, createProject, Project } from '../../../lib/api/projects'

export default function ProjectsView() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  async function loadProjects() {
    setLoading(true)
    setError(null)
    try {
      const data = await getProjects()
      setProjects(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  async function handleNewProject() {
    const name = window.prompt('Project name:')
    if (!name || !name.trim()) return
    setCreating(true)
    try {
      await createProject({ name: name.trim() })
      await loadProjects()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-[var(--text-primary)]">Projects</h1>
        <button
          onClick={handleNewProject}
          disabled={creating}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-xl transition-all shadow-sm shadow-indigo-600/20"
        >
          {creating ? <FiLoader className="w-4 h-4 animate-spin" /> : <FiPlus className="w-4 h-4" />}
          New project
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <FiLoader className="w-8 h-8 text-[var(--text-muted)] mx-auto mb-3 animate-spin" />
              <p className="text-[var(--text-secondary)]">Loading projects...</p>
            </div>
          </div>
        ) : error ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <FiAlertCircle className="w-10 h-10 text-red-500 mx-auto mb-3" />
              <p className="text-[var(--text-secondary)]">Couldn't load projects: {error}</p>
            </div>
          </div>
        ) : projects.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <FiFolder className="w-5 h-5 text-indigo-500" />
              </div>
              <p className="text-[var(--text-secondary)]">No projects yet — create one to get started</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 animate-fadeIn">
            {projects.map(project => (
              <div
                key={project.id}
                className="bg-[var(--surface-soft)] hover:bg-[var(--surface-strong)] border border-[var(--border-subtle)] rounded-2xl p-5 cursor-pointer transition-all duration-200 hover:shadow-md hover:shadow-black/[0.04] hover:-translate-y-0.5"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-sm shadow-indigo-600/20">
                    <FiFolder className="w-5 h-5 text-white" />
                  </div>
                  <button onClick={e => e.stopPropagation()} className="p-1.5 hover:bg-[var(--surface-strong)] rounded-lg transition-colors">
                    <FiMoreVertical className="w-4 h-4 text-[var(--text-muted)]" />
                  </button>
                </div>
                <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1">{project.name}</h3>
                <p className="text-xs text-[var(--text-muted)] mb-4 line-clamp-2">{project.description ?? 'No description'}</p>
                <div className="flex items-center gap-4 text-xs text-[var(--text-muted)]">
                  <span className="flex items-center gap-1.5">
                    <FiFileText className="w-3.5 h-3.5" />
                    {project.doc_count} docs
                  </span>
                  <span className="flex items-center gap-1.5">
                    <FiMessageSquare className="w-3.5 h-3.5" />
                    {project.chat_count} chats
                  </span>
                  <span className="ml-auto">{new Date(project.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}