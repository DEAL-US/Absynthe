import { api } from './client'
import type { GraphGenerateRequest, GraphGenerateResponse, GraphUploadResponse } from './types'

export const generateGraph = (req: GraphGenerateRequest) =>
  api.post<GraphGenerateResponse>('/graph/generate', req)

export const getGraph = (graphId: string) =>
  api.get<{ graph_id: string; elements: unknown[] }>(`/graph/${graphId}`)

export const uploadGraphs = async (files: File[]): Promise<GraphUploadResponse> => {
  const formData = new FormData()
  for (const file of files) formData.append('files', file)
  const res = await fetch('/api/graph/upload', { method: 'POST', body: formData })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail.detail ?? res.statusText)
  }
  return res.json()
}
