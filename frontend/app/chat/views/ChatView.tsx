'use client'

import { useState, useEffect, useRef } from 'react'
import { FiSend, FiPlus, FiTrash2, FiMessageSquare } from 'react-icons/fi'
import { apiClient } from '@/lib/api/client'

interface Chat {
  id: number
  title: string
  created_at: string
}

interface Message {
  id: number
  type: 'user' | 'assistant'
  content: string
  timestamp: string
}

export default function ChatView() {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChat, setCurrentChat] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadChats()
  }, [])

  useEffect(() => {
    if (currentChat) {
      loadMessages(currentChat)
    }
  }, [currentChat])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const loadChats = async () => {
    try {
      const data = await apiClient.listChats()
      setChats(data.chats)
      if (data.chats.length > 0 && !currentChat) {
        setCurrentChat(data.chats[0].id)
      }
    } catch (err) {
      console.error('Failed to load chats', err)
    }
  }

  const loadMessages = async (chatId: number) => {
    try {
      const data = await apiClient.getChatMessages(chatId)
      setMessages(data.messages)
    } catch (err) {
      console.error('Failed to load messages', err)
    }
  }

  const handleNewChat = async () => {
    try {
      const data = await apiClient.createNewChat()
      const newChat = { id: data.chat_id, title: data.title, created_at: new Date().toISOString() }
      setChats([newChat, ...chats])
      setCurrentChat(data.chat_id)
      setMessages([])
      setInput('')
    } catch (err) {
      setError('Failed to create new chat')
    }
  }

  const handleDeleteChat = async (chatId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Delete this chat?')) {
      try {
        await apiClient.deleteChat(chatId)
        if (currentChat === chatId) {
          setCurrentChat(null)
          setMessages([])
        }
        await loadChats()
      } catch (err) {
        setError('Failed to delete chat')
      }
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !currentChat) return

    setLoading(true)
    setError('')

    try {
      const response = await apiClient.chat(input, currentChat)
      setInput('')
      await loadMessages(currentChat)

      const chat = chats.find(c => c.id === currentChat)
      if (chat?.title === 'New Chat') {
        const title = input.substring(0, 50)
        await apiClient.updateChatTitle(currentChat, title)
        await loadChats()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 bg-[var(--surface)] border-r border-[var(--border-subtle)] flex flex-col shrink-0">
        <button
          onClick={handleNewChat}
          className="m-3 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl flex items-center justify-center gap-2 text-sm font-medium transition-all shadow-sm shadow-indigo-600/20"
        >
          <FiPlus className="w-4 h-4" />
          New chat
        </button>

        <div className="flex-1 overflow-y-auto px-2 pb-2">
          {chats.length === 0 ? (
            <div className="text-center py-10 px-4">
              <FiMessageSquare className="w-7 h-7 text-[var(--text-muted)] mx-auto mb-2" />
              <p className="text-[var(--text-muted)] text-sm">No chats yet</p>
            </div>
          ) : (
            <div className="space-y-1">
              {chats.map((chat) => (
                <div key={chat.id} className="flex items-center gap-1 group">
                  <button
                    onClick={() => setCurrentChat(chat.id)}
                    className={`flex-1 min-w-0 text-left px-3 py-2.5 rounded-xl transition-all ${
                      currentChat === chat.id
                        ? 'bg-indigo-50 border border-indigo-200'
                        : 'border border-transparent hover:bg-[var(--surface-soft)]'
                    }`}
                  >
                    <p className={`truncate text-sm font-medium ${currentChat === chat.id ? 'text-indigo-700' : 'text-[var(--text-primary)]'}`}>
                      {chat.title}
                    </p>
                    <p className="text-xs text-[var(--text-muted)]">
                      {new Date(chat.created_at).toLocaleDateString()}
                    </p>
                  </button>
                  <button
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    className="p-2 text-[var(--text-muted)] hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100 shrink-0"
                    title="Delete chat"
                  >
                    <FiTrash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {!currentChat ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center mb-3">
                <FiMessageSquare className="w-5 h-5 text-indigo-500" />
              </div>
              <p className="text-[var(--text-secondary)] text-sm">Select or create a chat to start</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center mb-3">
                <FiMessageSquare className="w-5 h-5 text-indigo-500" />
              </div>
              <p className="text-[var(--text-secondary)] text-sm">Ask a question about your documents to get started</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex animate-fadeIn ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-lg px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                    msg.type === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-sm'
                      : 'bg-[var(--surface-strong)] text-[var(--text-primary)] rounded-bl-sm border border-[var(--border-subtle)]'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  <p className={`text-[11px] mt-1.5 ${msg.type === 'user' ? 'text-indigo-100' : 'text-[var(--text-muted)]'}`}>
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start animate-fadeIn">
              <div className="bg-[var(--surface-strong)] border border-[var(--border-subtle)] px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex gap-1.5">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 mx-6 mb-2 rounded-xl text-sm">
            {error}
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-[var(--border-subtle)] bg-[var(--surface)]">
          <div className="flex gap-2 max-w-3xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={!currentChat || loading}
              className="flex-1 px-4 py-2.5 bg-stone-50 text-[var(--text-primary)] rounded-xl border border-[var(--border-strong)] placeholder-[var(--text-muted)] focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 disabled:opacity-50 transition-all text-sm"
            />
            <button
              type="submit"
              disabled={!currentChat || loading || !input.trim()}
              className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-sm shadow-indigo-600/20"
            >
              <FiSend className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}