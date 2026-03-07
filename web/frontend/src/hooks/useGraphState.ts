import { create } from 'zustand'
import type {
  CytoscapeElement,
  LabelDistribution,
  LabelingFunctionConfig,
  PerturbationConfig,
  PerturbationResponse,
} from '@/api/types'

interface GraphState {
  graphId: string | null
  elements: CytoscapeElement[]
  labelDistribution: LabelDistribution | null
  labelingFunctions: LabelingFunctionConfig[]
  perturbations: PerturbationConfig[]
  perturbationResult: PerturbationResponse | null
  graphSource: 'motif' | 'upload'
  uploadFolderPath: string | null
  uploadFileCount: number
  setGraph: (id: string, elements: CytoscapeElement[]) => void
  setUploadedGraph: (id: string, elements: CytoscapeElement[], folderPath: string | null, fileCount: number) => void
  setLabelingFunctions: (configs: LabelingFunctionConfig[]) => void
  setPerturbations: (configs: PerturbationConfig[]) => void
  setLabels: (
    elements: CytoscapeElement[],
    dist: LabelDistribution,
    labelingFunctions?: LabelingFunctionConfig[],
  ) => void
  setPerturbationResult: (
    result: PerturbationResponse,
    perturbations?: PerturbationConfig[],
  ) => void
  clearPerturbation: () => void
  reset: () => void
}

const DEFAULT_LABELING_FUNCTIONS: LabelingFunctionConfig[] = [
  { type: 'motif_labeling', params: {} },
]

const DEFAULT_PERTURBATIONS: PerturbationConfig[] = [
  {
    type: 'remove_nodes',
    params: { num_nodes: 1, strategy: 'random' },
    count: 1,
  },
]

export const useGraphState = create<GraphState>((set) => ({
  graphId: null,
  elements: [],
  labelDistribution: null,
  labelingFunctions: DEFAULT_LABELING_FUNCTIONS,
  perturbations: DEFAULT_PERTURBATIONS,
  perturbationResult: null,
  graphSource: 'motif',
  uploadFolderPath: null,
  uploadFileCount: 0,

  setGraph: (id, elements) =>
    set({
      graphId: id,
      elements,
      labelDistribution: null,
      perturbationResult: null,
      graphSource: 'motif',
      uploadFolderPath: null,
      uploadFileCount: 0,
    }),

  setUploadedGraph: (id, elements, folderPath, fileCount) =>
    set({
      graphId: id,
      elements,
      labelDistribution: null,
      perturbationResult: null,
      graphSource: 'upload',
      uploadFolderPath: folderPath,
      uploadFileCount: fileCount,
    }),

  setLabelingFunctions: (configs) =>
    set({ labelingFunctions: configs }),

  setPerturbations: (configs) =>
    set({ perturbations: configs }),

  setLabels: (elements, dist, labelingFunctions) =>
    set((state) => ({
      elements,
      labelDistribution: dist,
      labelingFunctions: labelingFunctions ?? state.labelingFunctions,
    })),

  setPerturbationResult: (result, perturbations) =>
    set((state) => ({
      perturbationResult: result,
      perturbations: perturbations ?? state.perturbations,
    })),

  clearPerturbation: () =>
    set({ perturbationResult: null }),

  reset: () =>
    set({
      graphId: null,
      elements: [],
      labelDistribution: null,
      labelingFunctions: DEFAULT_LABELING_FUNCTIONS,
      perturbations: DEFAULT_PERTURBATIONS,
      perturbationResult: null,
      graphSource: 'motif',
      uploadFolderPath: null,
      uploadFileCount: 0,
    }),
}))
