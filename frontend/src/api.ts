const BASE = '/api'

function getToken(): string | null {
  return localStorage.getItem('token')
}

export function setToken(token: string) {
  localStorage.setItem('token', token)
}

export function clearToken() {
  localStorage.removeItem('token')
}

export function isLoggedIn(): boolean {
  return !!getToken()
}

async function req<T>(url: string, init?: RequestInit): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${url}`, { ...init, headers })

  if (res.status === 401) {
    clearToken()
    window.location.href = '/login'
    throw new Error('Session expired')
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || 'Request failed')
  }
  return res.json()
}

async function reqUpload<T>(url: string, file: File): Promise<T> {
  const token = getToken()
  const form = new FormData()
  form.append('file', file)
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${url}`, { method: 'POST', headers, body: form })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || 'Upload failed')
  }
  return res.json()
}

export const api = {
  auth: {
    register: (data: any) => req<any>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: any) => req<any>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    me: () => req<any>('/auth/me'),
  },
  documents: {
    list: () => req<any[]>('/documents/'),
    get: (id: number) => req<any>(`/documents/${id}`),
    upload: (file: File) => reqUpload<any>('/documents/upload', file),
    delete: (id: number) => req<any>(`/documents/${id}`, { method: 'DELETE' }),
    search: (query: string) => req<any>(`/documents/search?q=${encodeURIComponent(query)}`),
  },
  proposals: {
    list: () => req<any[]>('/proposals/'),
    get: (id: number) => req<any>(`/proposals/${id}`),
    generate: (data: { client_name: string; client_request: string; language?: string }) => req<any>('/proposals/generate', { method: 'POST', body: JSON.stringify(data) }),
    chat: (id: number, message: string) => req<any>(`/proposals/${id}/chat`, { method: 'POST', body: JSON.stringify({ message }) }),
    update: (id: number, data: { proposal_content: string }) => req<any>(`/proposals/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id: number) => req<any>(`/proposals/${id}`, { method: 'DELETE' }),
    downloadUrl: (id: number) => `${BASE}/proposals/${id}/download?token=${encodeURIComponent(getToken() || '')}`,
    pdfUrl: (id: number) => `${BASE}/proposals/${id}/pdf?token=${encodeURIComponent(getToken() || '')}`,
  },
  org: {
    get: () => req<any>('/organization/'),
    update: (data: any) => req<any>('/organization/', { method: 'PUT', body: JSON.stringify(data) }),
  },
}
