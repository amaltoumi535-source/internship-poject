'use client'

import { useEffect, useState } from 'react'
import { FiSun, FiMoon, FiCheck, FiRotateCcw, FiSend, FiCheckCircle } from 'react-icons/fi'
import { useTheme, ACCENT_PRESETS, PALETTES, type AccentColor, type ThemeMode } from '../contexts/ThemeContext'

function isValidHex(value: string) {
  return /^#[0-9a-fA-F]{6}$/.test(value)
}

export default function DesignView() {
  const { mode, setMode, accent, setAccent, reset } = useTheme()

  const [draftMode, setDraftMode] = useState<ThemeMode>(mode)
  const [draftAccent, setDraftAccent] = useState<AccentColor>(accent)
  const [customFrom, setCustomFrom] = useState(accent.from)
  const [customTo, setCustomTo] = useState(accent.to)
  const [justApplied, setJustApplied] = useState(false)

  useEffect(() => {
    setDraftMode(mode)
    setDraftAccent(accent)
    setCustomFrom(accent.from)
    setCustomTo(accent.to)
  }, [mode, accent])

  const hasChanges = draftMode !== mode || draftAccent.from !== accent.from || draftAccent.to !== accent.to

  const applyCustom = () => {
    if (!isValidHex(customFrom) || !isValidHex(customTo)) return
    setDraftAccent({ name: 'Custom', from: customFrom, to: customTo })
  }

  const handleApply = () => {
    setMode(draftMode)
    setAccent(draftAccent)
    setJustApplied(true)
    setTimeout(() => setJustApplied(false), 2000)
  }

  const handleReset = () => {
    reset()
  }

  const isPresetActive = (preset: AccentColor) => preset.name === draftAccent.name
  const previewPalette = PALETTES[draftMode]

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-[var(--text-primary)]">Customize your agent</h1>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            Preview your changes, then click apply to update the whole agent.
          </p>
        </div>
        <button
          onClick={handleApply}
          disabled={!hasChanges}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all shrink-0 ${
            hasChanges
              ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm shadow-indigo-600/20'
              : 'bg-[var(--surface-strong)] text-[var(--text-muted)] cursor-not-allowed'
          }`}
        >
          {justApplied ? (
            <>
              <FiCheckCircle className="w-4 h-4" />
              Applied
            </>
          ) : (
            'Apply'
          )}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
        {/* Controls */}
        <div className="lg:col-span-2 space-y-6">
          {/* Mode */}
          <section className="bg-[var(--surface)] border border-[var(--border-subtle)] rounded-2xl p-5">
            <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-4">Appearance</h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setDraftMode('light')}
                className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
                  draftMode === 'light'
                    ? 'bg-indigo-50 border-indigo-300'
                    : 'bg-[var(--surface-soft)] border-[var(--border-subtle)] hover:bg-[var(--surface-hover)]'
                }`}
              >
                <FiSun className="w-5 h-5 text-amber-500" />
                <div className="text-left">
                  <p className="text-sm font-medium text-[var(--text-primary)]">Light</p>
                  <p className="text-xs text-[var(--text-muted)]">Bright and clean</p>
                </div>
                {draftMode === 'light' && <FiCheck className="w-4 h-4 text-indigo-500 ml-auto" />}
              </button>
              <button
                onClick={() => setDraftMode('dark')}
                className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
                  draftMode === 'dark'
                    ? 'bg-indigo-50 border-indigo-300'
                    : 'bg-[var(--surface-soft)] border-[var(--border-subtle)] hover:bg-[var(--surface-hover)]'
                }`}
              >
                <FiMoon className="w-5 h-5 text-indigo-500" />
                <div className="text-left">
                  <p className="text-sm font-medium text-[var(--text-primary)]">Dark</p>
                  <p className="text-xs text-[var(--text-muted)]">Easy on the eyes</p>
                </div>
                {draftMode === 'dark' && <FiCheck className="w-4 h-4 text-indigo-500 ml-auto" />}
              </button>
            </div>
          </section>

          {/* Accent presets */}
          <section className="bg-[var(--surface)] border border-[var(--border-subtle)] rounded-2xl p-5">
            <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-4">Accent color</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {ACCENT_PRESETS.map(preset => (
                <button
                  key={preset.name}
                  onClick={() => setDraftAccent(preset)}
                  className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                    isPresetActive(preset)
                      ? 'border-indigo-300 bg-[var(--surface-strong)]'
                      : 'border-[var(--border-subtle)] bg-[var(--surface-soft)] hover:bg-[var(--surface-hover)]'
                  }`}
                >
                  <span
                    className="w-6 h-6 rounded-full shrink-0"
                    style={{ background: `linear-gradient(135deg, ${preset.from}, ${preset.to})` }}
                  />
                  <span className="text-xs text-[var(--text-secondary)] text-left flex-1">{preset.name}</span>
                  {isPresetActive(preset) && <FiCheck className="w-4 h-4 text-[var(--text-secondary)] shrink-0" />}
                </button>
              ))}
            </div>
          </section>

          {/* Custom color */}
          <section className="bg-[var(--surface)] border border-[var(--border-subtle)] rounded-2xl p-5">
            <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-4">Custom gradient</h3>
            <div className="flex items-end gap-4 flex-wrap">
              <div>
                <label className="text-xs text-[var(--text-muted)] block mb-1.5">Start</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={isValidHex(customFrom) ? customFrom : '#6366f1'}
                    onChange={e => setCustomFrom(e.target.value)}
                    className="w-9 h-9 rounded-lg border border-[var(--border-strong)] bg-transparent cursor-pointer"
                  />
                  <input
                    type="text"
                    value={customFrom}
                    onChange={e => setCustomFrom(e.target.value)}
                    className="w-24 px-2 py-1.5 bg-[var(--surface-strong)] border border-[var(--border-strong)] rounded-lg text-xs text-[var(--text-primary)]"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-[var(--text-muted)] block mb-1.5">End</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={isValidHex(customTo) ? customTo : '#4f46e5'}
                    onChange={e => setCustomTo(e.target.value)}
                    className="w-9 h-9 rounded-lg border border-[var(--border-strong)] bg-transparent cursor-pointer"
                  />
                  <input
                    type="text"
                    value={customTo}
                    onChange={e => setCustomTo(e.target.value)}
                    className="w-24 px-2 py-1.5 bg-[var(--surface-strong)] border border-[var(--border-strong)] rounded-lg text-xs text-[var(--text-primary)]"
                  />
                </div>
              </div>
              <button
                onClick={applyCustom}
                disabled={!isValidHex(customFrom) || !isValidHex(customTo)}
                className="px-4 py-2 bg-[var(--surface-strong)] hover:bg-[var(--surface-hover-strong)] disabled:opacity-40 disabled:cursor-not-allowed border border-[var(--border-strong)] rounded-xl text-sm text-[var(--text-primary)] transition-all"
              >
                Use these colors
              </button>
            </div>
          </section>

          <div className="flex items-center justify-between">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
            >
              <FiRotateCcw className="w-3.5 h-3.5" />
              Reset to default
            </button>
            {hasChanges && (
              <p className="text-xs text-amber-600">You have unapplied changes</p>
            )}
          </div>
        </div>

        {/* Live preview */}
        <div className="bg-[var(--surface)] border border-[var(--border-subtle)] rounded-2xl p-5 h-fit sticky top-0">
          <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-4">Preview</h3>
          <div
            className="rounded-xl border overflow-hidden"
            style={{ borderColor: previewPalette['--border-subtle'], background: previewPalette['--bg-app-from'] }}
          >
            <div
              className="px-4 py-3 text-sm font-semibold text-white"
              style={{ background: `linear-gradient(90deg, ${draftAccent.from}, ${draftAccent.to})` }}
            >
              Document Agent
            </div>
            <div className="p-4 space-y-3">
              <div className="flex justify-start">
                <div
                  className="px-3 py-2 rounded-2xl rounded-bl-none text-xs max-w-[80%] border"
                  style={{
                    background: previewPalette['--surface-strong'],
                    borderColor: previewPalette['--border-subtle'],
                    color: previewPalette['--text-primary'],
                  }}
                >
                  How can I help you today?
                </div>
              </div>
              <div className="flex justify-end">
                <div
                  className="text-white px-3 py-2 rounded-2xl rounded-br-none text-xs max-w-[80%]"
                  style={{ background: `linear-gradient(90deg, ${draftAccent.from}, ${draftAccent.to})` }}
                >
                  Summarize this contract for me
                </div>
              </div>
              <div className="flex gap-2 pt-1">
                <div
                  className="flex-1 px-3 py-2 rounded-lg text-xs border"
                  style={{
                    background: previewPalette['--surface-strong'],
                    borderColor: previewPalette['--border-strong'],
                    color: previewPalette['--text-muted'],
                  }}
                >
                  Message AI Agent...
                </div>
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  style={{ background: `linear-gradient(135deg, ${draftAccent.from}, ${draftAccent.to})` }}
                >
                  <FiSend className="w-3.5 h-3.5 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}