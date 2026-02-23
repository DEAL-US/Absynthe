import { create } from 'zustand'
import type { CytoscapeElement, LabelDistribution, PerturbationResponse } from '@/api/types'

interface GraphState {
  // Currently active graph
  graphId: string | null
  elements: CytoscapeElement[]
  labelDistribution: LabelDistribution | null
  // Perturbation result (before + after)
  perturbationResult: PerturbationResponse | null
  // Actions
  setGraph: (id: string, elements: CytoscapeElement[]) => void
  setLabels: (elements: CytoscapeElement[], dist: LabelDistribution) => void
  setPerturbationResult: (result: PerturbationResponse) => void
  clearPerturbation: () => void
  reset: () => void
}

export const useGraphState = create<GraphState>((set) => ({
  graphId: null,
  elements: [],
  labelDistribution: null,
  perturbationResult: null,

  setGraph: (id, elements) =>
    set({ graphId: id, elements, labelDistribution: null, perturbationResult: null }),

  setLabels: (elements, dist) =>
    set({ elements, labelDistribution: dist }),

  setPerturbationResult: (result) =>
    set({ perturbationResult: result }),

  clearPerturbation: () =>
    set({ perturbationResult: null }),

  reset: () =>
    set({ graphId: null, elements: [], labelDistribution: null, perturbationResult: null }),
}))
