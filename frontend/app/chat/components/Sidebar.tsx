'use client'

import { useState } from 'react'
import {
  FiMessageSquare,
  FiFileText,
  FiFolder,
  FiSettings,
  FiUser,
  FiZap,
  FiLayout,
  FiLogOut,
  FiMoreVertical,
} from 'react-icons/fi'

type ViewType =
  | 'chat'
  | 'documents'
  | 'document-details'
  | 'projects'
  | 'settings'
  | 'profile'
  | 'upgrade'
  | 'design'

interface SidebarProps {
  activeView: ViewType
  onViewChange: (view: ViewType) => void
  onLogout: () => void
  collapsed?: boolean
  onCollapse?: () => void
}

const NAV_ITEMS: { view: ViewType; label: string; icon: typeof FiMessageSquare }[] = [
  { view: 'chat', label: 'Chat', icon: FiMessageSquare },
  { view: 'documents', label: 'Documents', icon: FiFileText },
  { view: 'projects', label: 'Projects', icon: FiFolder },
  { view: 'design', label: 'Design', icon: FiLayout },
]

// 'document-details' is a sub-view of 'documents' and shares its nav highlight
const isActive = (item: ViewType, active: ViewType) =>
  item === active || (item === 'documents' && active === 'document-details')

export default function Sidebar({ activeView, onViewChange, onLogout, collapsed = false, onCollapse }: SidebarProps) {
  const [showProfileMenu, setShowProfileMenu] = useState(false)

  if (collapsed) return null

  return (
    <aside
      className="w-64 bg-[var(--surface)] backdrop-blur-xl border-r border-[var(--border-subtle)] flex flex-col transition-all duration-300 overflow-hidden shrink-0"
    >
      {/* Brand + collapse toggle */}
      <div className="p-4 border-b border-[var(--border-subtle)] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-sm shadow-indigo-600/20">
            <FiZap className="w-4 h-4 text-white" />
          </div>
          <h2 className="text-[15px] font-bold text-[var(--text-primary)]">Document Agent</h2>
        </div>
        {onCollapse && (
          <button
            onClick={onCollapse}
            className="p-2 hover:bg-[var(--surface-strong)] rounded-lg transition-colors"
            aria-label="Collapse sidebar"
          >
            <FiMoreVertical className="w-4 h-4 text-[var(--text-secondary)] rotate-90" />
          </button>
        )}
      </div>

      {/* Primary nav */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {NAV_ITEMS.map(({ view, label, icon: Icon }) => (
          <button
            key={view}
            onClick={() => onViewChange(view)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
              isActive(view, activeView)
                ? 'bg-indigo-50 border border-indigo-200 text-indigo-700'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-soft)] hover:text-[var(--text-primary)] border border-transparent'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </nav>

      {/* Upgrade nudge */}
      <div className="px-2 pb-2">
        <button
          onClick={() => onViewChange('upgrade')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
            activeView === 'upgrade'
              ? 'bg-indigo-50 border border-indigo-200 text-indigo-700'
              : 'bg-gradient-to-r from-indigo-50/60 to-amber-50/40 border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:from-indigo-50 hover:to-amber-50'
          }`}
        >
          <FiZap className="w-4 h-4" />
          Upgrade plan
        </button>
      </div>

      {/* Profile section */}
      <div className="border-t border-[var(--border-subtle)] p-3 relative">
        <button
          onClick={() => setShowProfileMenu(!showProfileMenu)}
          className="w-full flex items-center gap-3 p-2 hover:bg-[var(--surface-strong)] rounded-lg transition-colors"
        >
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm shrink-0">
            A
          </div>
          <div className="flex-1 text-left min-w-0">
            <p className="text-sm font-medium text-[var(--text-primary)] truncate">Amal</p>
            <p className="text-xs text-[var(--text-muted)] truncate">amal@example.com</p>
          </div>
          <FiMoreVertical className="w-4 h-4 text-[var(--text-muted)] shrink-0" />
        </button>

        {showProfileMenu && (
          <div className="absolute bottom-16 left-2 right-2 bg-[var(--surface-solid)] backdrop-blur-xl border border-[var(--border-subtle)] rounded-xl shadow-lg shadow-black/[0.06] z-50 overflow-hidden animate-fadeIn">
            <button
              onClick={() => {
                onViewChange('profile')
                setShowProfileMenu(false)
              }}
              className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--surface-strong)] text-sm text-[var(--text-secondary)] transition-colors text-left"
            >
              <FiUser className="w-4 h-4" />
              Profile
            </button>
            <button
              onClick={() => {
                onViewChange('settings')
                setShowProfileMenu(false)
              }}
              className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--surface-strong)] text-sm text-[var(--text-secondary)] transition-colors text-left"
            >
              <FiSettings className="w-4 h-4" />
              Settings
            </button>
            <button
              onClick={() => {
                onViewChange('upgrade')
                setShowProfileMenu(false)
              }}
              className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--surface-strong)] text-sm text-[var(--text-secondary)] transition-colors text-left"
            >
              <FiZap className="w-4 h-4" />
              Billing and plans
            </button>
            <hr className="my-1 border-[var(--border-subtle)]" />
            <button
              onClick={onLogout}
              className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-red-50 text-sm text-red-600 transition-colors text-left"
            >
              <FiLogOut className="w-4 h-4" />
              Log out
            </button>
          </div>
        )}
      </div>

    </aside>
  )
}

export { type ViewType }