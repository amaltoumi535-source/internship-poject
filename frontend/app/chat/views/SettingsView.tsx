'use client'

import { useState } from 'react'
import { FiBell, FiEye, FiCpu, FiKey } from 'react-icons/fi'

interface ToggleRowProps {
  label: string
  description: string
  checked: boolean
  onChange: (v: boolean) => void
}

function ToggleRow({ label, description, checked, onChange }: ToggleRowProps) {
  return (
    <div className="flex items-center justify-between py-4">
      <div>
        <p className="text-sm font-medium text-[var(--text-primary)]">{label}</p>
        <p className="text-xs text-[var(--text-muted)] mt-0.5">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${checked ? 'bg-blue-600' : 'bg-[var(--surface-strong)]'}`}
      >
        <span
          className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0.5'
          }`}
        />
      </button>
    </div>
  )
}

export default function SettingsView() {
  const [emailNotifs, setEmailNotifs] = useState(true)
  const [processingAlerts, setProcessingAlerts] = useState(true)
  const [darkMode, setDarkMode] = useState(true)
  const [autoOcr, setAutoOcr] = useState(true)

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4">
        <h1 className="text-xl font-bold text-[var(--text-primary)]">Settings</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-6 max-w-2xl space-y-6">
        <section className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-1">
            <FiBell className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide">Notifications</h3>
          </div>
          <div className="divide-y divide-[var(--border-subtle)]">
            <ToggleRow
              label="Email notifications"
              description="Get notified by email about account activity"
              checked={emailNotifs}
              onChange={setEmailNotifs}
            />
            <ToggleRow
              label="Processing alerts"
              description="Alert me when a document finishes processing or fails"
              checked={processingAlerts}
              onChange={setProcessingAlerts}
            />
          </div>
        </section>

        <section className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-1">
            <FiEye className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide">Appearance</h3>
          </div>
          <div className="divide-y divide-[var(--border-subtle)]">
            <ToggleRow
              label="Dark mode"
              description="Use the dark theme across the app"
              checked={darkMode}
              onChange={setDarkMode}
            />
          </div>
        </section>

        <section className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-1">
            <FiCpu className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide">Document pipeline</h3>
          </div>
          <div className="divide-y divide-[var(--border-subtle)]">
            <ToggleRow
              label="Auto-OCR on upload"
              description="Automatically run OCR on scanned or image-based documents"
              checked={autoOcr}
              onChange={setAutoOcr}
            />
          </div>
        </section>

        <section className="bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <FiKey className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide">API access</h3>
          </div>
          <p className="text-xs text-[var(--text-muted)] mb-3">
            API keys will appear here once backend auth is connected.
          </p>
          <button
            disabled
            className="px-4 py-2 bg-[var(--surface-soft)] border border-[var(--border-subtle)] rounded-xl text-sm text-[var(--text-muted)] cursor-not-allowed"
          >
            Generate API key
          </button>
        </section>
      </div>
    </div>
  )
}