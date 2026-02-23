import { api } from './client'
import type { GraphGenerateRequest, GraphGenerateResponse } from './types'

export const generateGraph = (req: GraphGenerateRequest) =>
  api.post<GraphGenerateResponse>('/graph/generate', req)

export const getGraph = (graphId: string) =>
  api.get<{ graph_id: string; elements: unknown[] }>(`/graph/${graphId}`)
