export class APIClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  private authToken: string | null = null

  constructor() {
    if (typeof window !== 'undefined') {
      this.authToken = localStorage.getItem('auth_token')
    }
  }

  private getAuthHeader() {
    const token = localStorage.getItem('auth_token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  }

  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseURL}${path}`, {
      headers: this.getAuthHeader(),
    })
    if (!res.ok) throw new Error(`Request failed: ${res.status}`)
    return res.json()
  }

  async signup(email: string, password: string, fullName: string) {
    const res = await fetch(`${this.baseURL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, fullName }),
    })
    if (!res.ok) throw new Error('Signup failed')
    return res.json()
  }

  async verifyEmail(email: string, code: string) {
    const res = await fetch(`${this.baseURL}/api/auth/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail || 'Verification failed')
    }
    const data = await res.json()
    localStorage.setItem('auth_token', data.access_token)
    return data
  }

  async resendVerification(email: string) {
    const res = await fetch(`${this.baseURL}/api/auth/resend-verification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!res.ok) throw new Error('Failed to resend link')
    return res.json()
  }

  async signin(email: string, password: string) {
    const res = await fetch(`${this.baseURL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) throw new Error('Signin failed')
    const data = await res.json()
    localStorage.setItem('auth_token', data.access_token)
    return data
  }

  async forgotPassword(email: string) {
    const res = await fetch(`${this.baseURL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!res.ok) throw new Error('Request failed')
    return res.json()
  }

  async resetPassword(email: string, code: string, newPassword: string) {
    const res = await fetch(`${this.baseURL}/api/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code, new_password: newPassword }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail || 'Reset failed')
    }
    return res.json()
  }

  async createNewChat() {
    const res = await fetch(`${this.baseURL}/api/chats/new`, {
      method: 'POST',
      headers: this.getAuthHeader(),
    })
    if (!res.ok) throw new Error('Failed to create chat')
    return res.json()
  }

  async listChats() {
    const res = await fetch(`${this.baseURL}/api/chats/list`, {
      headers: this.getAuthHeader(),
    })
    if (!res.ok) throw new Error('Failed to list chats')
    return res.json()
  }

  async getChatMessages(chatId: number) {
    const res = await fetch(`${this.baseURL}/api/chats/${chatId}/messages`, {
      headers: this.getAuthHeader(),
    })
    if (!res.ok) throw new Error('Failed to get messages')
    return res.json()
  }

  async updateChatTitle(chatId: number, title: string) {
    const res = await fetch(`${this.baseURL}/api/chats/${chatId}/title`, {
      method: 'PUT',
      headers: this.getAuthHeader(),
      body: JSON.stringify({ title }),
    })
    if (!res.ok) throw new Error('Failed to update title')
    return res.json()
  }

  async deleteChat(chatId: number) {
    const res = await fetch(`${this.baseURL}/api/chats/${chatId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    })
    if (!res.ok) throw new Error('Failed to delete chat')
    return res.json()
  }

  async chat(message: string, chatId: number) {
    const res = await fetch(`${this.baseURL}/chat/`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify({ message, chat_id: chatId }),
    })
    if (!res.ok) throw new Error('Chat failed')
    return res.json()
  }

  async uploadDocument(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${this.baseURL}/ingest/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` },
      body: formData,
    })
    if (!res.ok) throw new Error('Upload failed')
    return res.json()
  }

  async deleteDocument(documentId: string | number) {
    const res = await fetch(`${this.baseURL}/ingest/${documentId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    })
    if (!res.ok) throw new Error('Delete failed')
    return res.json()
  }

  async getDocumentFileBlobUrl(documentId: string | number): Promise<string> {
    const res = await fetch(`${this.baseURL}/ingest/${documentId}/file`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` },
    })
    if (!res.ok) throw new Error('Failed to load file')
    const blob = await res.blob()
    return URL.createObjectURL(blob)
  }

  async downloadDocumentFile(documentId: string | number, filename: string) {
    const url = await this.getDocumentFileBlobUrl(documentId)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  async logout() {
    localStorage.removeItem('auth_token')
  }

  isAuthenticated() {
    return !!localStorage.getItem('auth_token')
  }
}

export const apiClient = new APIClient()