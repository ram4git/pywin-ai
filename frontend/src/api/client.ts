import type { Script, GenerateResponse, ExecuteResponse, ExecutionEvent } from './types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || resp.statusText)
  }
  return resp.json()
}

export const api = {
  scripts: {
    list: () => request<Script[]>('/scripts'),
    get: (id: string) => request<Script>(`/scripts/${id}`),
    create: (data: { name: string; prompt: string; plan?: unknown[]; generated_code?: string }) =>
      request<Script>('/scripts', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Partial<{ name: string; prompt: string; plan: unknown[]; generated_code: string }>) =>
      request<Script>(`/scripts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    remove: (id: string) => fetch(`${BASE}/scripts/${id}`, { method: 'DELETE' }),
  },
  generate: {
    plan: (prompt: string) => request<GenerateResponse>('/generate', { method: 'POST', body: JSON.stringify({ prompt }) }),
    refine: (data: { prompt: string; current_plan: unknown[]; failure: { step: number; error: string }; annotations: string[] }) =>
      request<GenerateResponse>('/generate/refine', { method: 'POST', body: JSON.stringify(data) }),
  },
  execute: {
    start: (data: { plan: unknown[]; prompt: string; script_id?: string }) =>
      request<ExecuteResponse>('/execute', { method: 'POST', body: JSON.stringify(data) }),
    stop: (id: string) => request<{ status: string }>(`/execute/${id}/stop`, { method: 'POST' }),
    stream: (id: string, onEvent: (e: ExecutionEvent) => void) => {
      const src = new EventSource(`${BASE}/execute/${id}/stream`)
      const handle = (e: MessageEvent) => { try { onEvent(JSON.parse(e.data)) } catch {} }
      for (const t of ['step_update', 'execution_complete', 'execution_failed', 'heartbeat'])
        src.addEventListener(t, handle)
      src.onerror = () => src.close()
      return () => src.close()
    },
  },
}
