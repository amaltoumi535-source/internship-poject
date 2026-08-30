'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export type ThemeMode = 'dark' | 'light'

export interface AccentColor {
  name: string
  from: string // gradient start (hex)
  to: string // gradient end (hex)
}

export const ACCENT_PRESETS: AccentColor[] = [
  { name: 'Indigo', from: '#6366f1', to: '#4f46e5' },
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

const DEFAULT_MODE: ThemeMode = 'light'
const DEFAULT_ACCENT = ACCENT_PRESETS[0]
const STORAGE_KEY = 'agent-theme-prefs'

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

export const PALETTES: Record<ThemeMode, Record<string, string>> = {
  light: {
    '--bg-app-from': '#faf7f2',
    '--bg-app-via': '#f5f1e9',
    '--bg-app-to': '#faf7f2',
    '--surface': 'rgba(255,255,255,0.7)',
    '--surface-solid': 'rgba(255,255,255,0.98)',
    '--surface-soft': 'rgba(15,23,42,0.03)',
    '--surface-strong': 'rgba(15,23,42,0.05)',
    '--surface-hover': 'rgba(15,23,42,0.05)',
    '--surface-hover-strong': 'rgba(15,23,42,0.09)',
    '--border-subtle': 'rgba(15,23,42,0.08)',
    '--border-strong': 'rgba(15,23,42,0.14)',
    '--text-primary': '#1c1a17',
    '--text-secondary': '#57534e',
    '--text-muted': '#8a8580',
  },
  dark: {
    '--bg-app-from': '#17151f',
    '--bg-app-via': '#1e1b29',
    '--bg-app-to': '#17151f',
    '--surface': 'rgba(40,36,54,0.5)',
    '--surface-solid': 'rgba(40,36,54,0.96)',
    '--surface-soft': 'rgba(255,255,255,0.04)',
    '--surface-strong': 'rgba(255,255,255,0.08)',
    '--surface-hover': 'rgba(255,255,255,0.08)',
    '--surface-hover-strong': 'rgba(255,255,255,0.14)',
    '--border-subtle': 'rgba(255,255,255,0.1)',
    '--border-strong': 'rgba(255,255,255,0.18)',
    '--text-primary': '#f5f3ef',
    '--text-secondary': '#c9c4bc',
    '--text-muted': '#948e85',
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