import { api } from './client'
import type { CompositionSchema, MotifSchema, StrategySchema } from './types'

export const getMotifs = () => api.get<MotifSchema[]>('/motifs')
export const getStrategies = () => api.get<StrategySchema[]>('/strategies')
export const getCompositions = () => api.get<CompositionSchema[]>('/compositions')
