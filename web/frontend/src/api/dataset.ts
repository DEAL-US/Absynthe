import { api } from './client'
import type { DatasetGenerateRequest, TaskStatus } from './types'

export const generateDataset = (req: DatasetGenerateRequest) =>
  api.post<{ task_id: string }>('/dataset/generate', req)

export const getDatasetStatus = (taskId: string) =>
  api.get<TaskStatus>(`/dataset/status/${taskId}`)

export const listDatasetGraphs = (outputDir: string) => {
  const encoded = btoa(outputDir).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
  return api.get<unknown[]>(`/dataset/${encoded}/graphs`)
}
