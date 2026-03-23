import { api } from './client'
import type {
  CompositionSchema,
  DistributionSchema,
  LabelingFunctionSchema,
  MotifSchema,
  PerturbationSchema,
  StrategySchema,
} from './types'

export const getMotifs = () => api.get<MotifSchema[]>('/motifs')
export const getStrategies = () => api.get<StrategySchema[]>('/strategies')
export const getCompositions = () => api.get<CompositionSchema[]>('/compositions')
export const getLabelingFunctions = () => api.get<LabelingFunctionSchema[]>('/labeling-functions')
export const getPerturbations = () => api.get<PerturbationSchema[]>('/perturbations')
export const getDistributions = () => api.get<DistributionSchema[]>('/distributions')
