'use client'

import { useState, useEffect } from 'react'
import { FiSend, FiPlus, FiX, FiTrash2 } from 'react-icons/fi'
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

  // Load chats on mount
  useEffect(() => {
    loadChats()
  }, [])

  // Load messages when chat changes
  useEffect(() => {
    if (currentChat) {
      loadMessages(currentChat)
    }
  }, [currentChat])

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
      
      // Update chat title if it's still "New Chat"
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
    <div className="flex h-full bg-slate-900">
      {/* Sidebar */}
      <div className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
        <button
          onClick={handleNewChat}
          className="m-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center justify-center gap-2 transition"
        >
          <FiPlus className="w-5 h-5" />
          New Chat
        </button>

        <div className="flex-1 overflow-y-auto">
          <div className="space-y-2 p-2">
            {chats.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-4">No chats yet</p>
            ) : (
              chats.map((chat) => (
                <div key={chat.id} className="flex items-center gap-1 px-2 py-1 group">
                  <button
                    onClick={() => setCurrentChat(chat.id)}
                    className={`flex-1 text-left px-3 py-2 rounded-lg transition ${
                      currentChat === chat.id
                        ? 'bg-green-600 text-white'
                        : 'text-gray-300 hover:bg-slate-700'
                    }`}
                  >
                    <p className="truncate text-sm font-medium">{chat.title}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(chat.created_at).toLocaleDateString()}
                    </p>
                  </button>
                  <button
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    className="p-2 text-red-400 hover:bg-red-600/20 rounded transition opacity-0 group-hover:opacity-100"
                    title="Delete chat"
                  >
                    <FiTrash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!currentChat ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              <p>Select or create a chat to start</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              <p>Start a conversation!</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-slate-700 text-gray-100 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 text-gray-100 px-4 py-2 rounded-lg">
                <p className="text-sm">Agent is thinking...</p>
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-2 mx-4 mb-2 rounded">
            {error}
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={!currentChat || loading}
              className="flex-1 px-4 py-2 bg-slate-800 text-white rounded border border-slate-700 focus:outline-none focus:border-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!currentChat || loading}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition flex items-center gap-2"
            >
              {loading ? '...' : <FiSend className="w-5 h-5" />}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}