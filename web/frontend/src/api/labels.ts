import { api } from './client'
import type { LabelAssignRequest, LabeledGraphResponse } from './types'

export const assignLabels = (req: LabelAssignRequest) =>
  api.post<LabeledGraphResponse>('/labels/assign', req)

export const reassignLabels = (req: LabelAssignRequest) =>
  api.post<LabeledGraphResponse>('/labels/reassign', req)
