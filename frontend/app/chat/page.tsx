'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar, { type ViewType } from './components/Sidebar'
import { ThemeProvider } from './contexts/ThemeContext'
import ChatView from './views/ChatView'
import DocumentsListView from './views/DocumentsListView'
import DocumentDetailsView from './views/DocumentDetailsView'
import SettingsView from './views/SettingsView'
import ProfileView from './views/ProfileView'
import UpgradeView from './views/UpgradeView'
import DesignView from './views/DesignView'
import { apiClient } from '@/lib/api/client';

export default function ChatPage() {
  const router = useRouter()
  const [activeView, setActiveView] = useState<ViewType>('chat')
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)

  const handleViewChange = (view: ViewType, docId?: string) => {
    setActiveView(view)
    if (docId) setSelectedDocId(docId)
  }

  const handleLogout = () => {
  apiClient.logout()
  router.push('/auth/login')
}
  return (
    <ThemeProvider>
      <div className="flex h-screen bg-gradient-to-br from-[var(--bg-app-from)] via-[var(--bg-app-via)] to-[var(--bg-app-to)] overflow-hidden">
        {/* Sidebar */}
        <Sidebar activeView={activeView} onViewChange={handleViewChange} onLogout={handleLogout} />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {activeView === 'chat' && <ChatView />}
          {activeView === 'documents' && (
            <DocumentsListView onSelectDoc={id => handleViewChange('document-details', id)} />
          )}
          {activeView === 'document-details' && (
            <DocumentDetailsView docId={selectedDocId} onBack={() => setActiveView('documents')} />
          )}
          
          {activeView === 'settings' && <SettingsView />}
          {activeView === 'profile' && <ProfileView />}
          {activeView === 'upgrade' && <UpgradeView />}
          {activeView === 'design' && <DesignView />}
        </div>
      </div>
    </ThemeProvider>
  )
}