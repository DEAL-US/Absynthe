import { api } from './client'
import type { PerturbationRequest, PerturbationResponse } from './types'

export const applyPerturbation = (req: PerturbationRequest) =>
  api.post<PerturbationResponse>('/perturbation/apply', req)
