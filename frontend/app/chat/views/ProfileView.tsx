'use client'

import { useState } from 'react'
import { FiEdit2, FiMail, FiCalendar, FiFileText, FiMessageSquare } from 'react-icons/fi'

export default function ProfileView() {
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState('Amal')
  const [email] = useState('amal@example.com')

  const stats = [
    { label: 'Documents processed', value: 24, icon: FiFileText },
    { label: 'Conversations', value: 12, icon: FiMessageSquare },
  ]

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4">
        <h1 className="text-xl font-bold text-[var(--text-primary)]">Profile</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-6 max-w-2xl space-y-6 animate-fadeIn">
        <section className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-6 flex items-center gap-5">
          <div className="w-16 h-16 bg-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-2xl shrink-0 shadow-sm shadow-indigo-600/20">
            {name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            {editing ? (
              <input
                value={name}
                onChange={e => setName(e.target.value)}
                className="bg-[var(--surface-strong)] border border-[var(--border-strong)] rounded-lg px-3 py-1.5 text-[var(--text-primary)] text-lg font-semibold focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              />
            ) : (
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">{name}</h2>
            )}
            <p className="text-sm text-[var(--text-muted)] flex items-center gap-1.5 mt-1">
              <FiMail className="w-3.5 h-3.5" />
              {email}
            </p>
            <p className="text-xs text-[var(--text-muted)] flex items-center gap-1.5 mt-1">
              <FiCalendar className="w-3.5 h-3.5" />
              Member since Aug 2026
            </p>
          </div>
          <button
            onClick={() => setEditing(!editing)}
            className="flex items-center gap-2 px-3 py-2 bg-[var(--surface-strong)] hover:bg-[var(--surface-hover-strong)] border border-[var(--border-strong)] rounded-xl text-sm text-[var(--text-secondary)] transition-all shrink-0"
          >
            <FiEdit2 className="w-4 h-4" />
            {editing ? 'Save' : 'Edit'}
          </button>
        </section>

        <section className="grid grid-cols-2 gap-4">
          {stats.map(stat => (
            <div key={stat.label} className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5 text-center transition-all hover:bg-[var(--surface-strong)]">
              <div className="w-9 h-9 bg-indigo-50 rounded-xl flex items-center justify-center mx-auto mb-2">
                <stat.icon className="w-4 h-4 text-indigo-500" />
              </div>
              <p className="text-2xl font-bold text-[var(--text-primary)]">{stat.value}</p>
              <p className="text-xs text-[var(--text-muted)] mt-1">{stat.label}</p>
            </div>
          ))}
        </section>

        <section className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
          <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-3">Field of study</h3>
          <p className="text-sm text-[var(--text-secondary)]">Business Intelligence — ISG Sousse</p>
        </section>
      </div>
    </div>
  )
}