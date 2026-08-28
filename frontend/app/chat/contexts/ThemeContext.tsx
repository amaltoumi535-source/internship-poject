'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export type ThemeMode = 'dark' | 'light'

export interface AccentColor {
  name: string
  from: string // gradient start (hex)
  to: string // gradient end (hex)
}

export const ACCENT_PRESETS: AccentColor[] = [
  { name: 'Blue / Purple', from: '#3b82f6', to: '#9333ea' },
  { name: 'Emerald / Teal', from: '#10b981', to: '#0d9488' },
  { name: 'Amber / Orange', from: '#f59e0b', to: '#ea580c' },
  { name: 'Rose / Fuchsia', from: '#f43f5e', to: '#c026d3' },
  { name: 'Cyan / Blue', from: '#06b6d4', to: '#2563eb' },
]

interface ThemeContextValue {
  mode: ThemeMode
  setMode: (mode: ThemeMode) => void
  accent: AccentColor
  setAccent: (accent: AccentColor) => void
  reset: () => void
}

const DEFAULT_MODE: ThemeMode = 'dark'
const DEFAULT_ACCENT = ACCENT_PRESETS[0]
const STORAGE_KEY = 'agent-theme-prefs'

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

export const PALETTES: Record<ThemeMode, Record<string, string>> = {
  dark: {
    '--bg-app-from': '#0f172a',
    '--bg-app-via': '#1e293b',
    '--bg-app-to': '#0f172a',
    '--surface': 'rgba(30,41,59,0.5)',
    '--surface-solid': 'rgba(30,41,59,0.95)',
    '--surface-soft': 'rgba(255,255,255,0.05)',
    '--surface-strong': 'rgba(255,255,255,0.1)',
    '--surface-hover': 'rgba(255,255,255,0.1)',
    '--surface-hover-strong': 'rgba(255,255,255,0.2)',
    '--border-subtle': 'rgba(255,255,255,0.1)',
    '--border-strong': 'rgba(255,255,255,0.2)',
    '--text-primary': '#f8fafc',
    '--text-secondary': '#cbd5e1',
    '--text-muted': '#94a3b8',
  },
  light: {
    '--bg-app-from': '#f8fafc',
    '--bg-app-via': '#eef2f7',
    '--bg-app-to': '#f8fafc',
    '--surface': 'rgba(255,255,255,0.75)',
    '--surface-solid': 'rgba(255,255,255,0.98)',
    '--surface-soft': 'rgba(15,23,42,0.035)',
    '--surface-strong': 'rgba(15,23,42,0.06)',
    '--surface-hover': 'rgba(15,23,42,0.06)',
    '--surface-hover-strong': 'rgba(15,23,42,0.1)',
    '--border-subtle': 'rgba(15,23,42,0.1)',
    '--border-strong': 'rgba(15,23,42,0.16)',
    '--text-primary': '#0f172a',
    '--text-secondary': '#475569',
    '--text-muted': '#64748b',
  },
}

function applyToDocument(mode: ThemeMode, accent: AccentColor) {
  const root = document.documentElement
  root.style.setProperty('--accent-from', accent.from)
  root.style.setProperty('--accent-to', accent.to)
  for (const [key, value] of Object.entries(PALETTES[mode])) {
    root.style.setProperty(key, value)
  }
  root.classList.toggle('light', mode === 'light')
  root.classList.toggle('dark', mode === 'dark')
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(DEFAULT_MODE)
  const [accent, setAccentState] = useState<AccentColor>(DEFAULT_ACCENT)
  const [hydrated, setHydrated] = useState(false)

  // Load saved prefs on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved) as { mode: ThemeMode; accent: AccentColor }
        setModeState(parsed.mode ?? DEFAULT_MODE)
        setAccentState(parsed.accent ?? DEFAULT_ACCENT)
      }
    } catch {
      // ignore malformed storage
    }
    setHydrated(true)
  }, [])

  // Apply + persist whenever prefs change
  useEffect(() => {
    if (!hydrated) return
    applyToDocument(mode, accent)
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, accent }))
  }, [mode, accent, hydrated])

  const setMode = (m: ThemeMode) => setModeState(m)
  const setAccent = (a: AccentColor) => setAccentState(a)
  const reset = () => {
    setModeState(DEFAULT_MODE)
    setAccentState(DEFAULT_ACCENT)
  }

  return (
    <ThemeContext.Provider value={{ mode, setMode, accent, setAccent, reset }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within a ThemeProvider')
  return ctx
}