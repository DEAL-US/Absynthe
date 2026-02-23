// Mirrors the Pydantic models on the backend

export interface CytoscapeElementData {
  id: string
  label?: string
  motif?: string
  motif_id?: string
  expected_ground_truth?: string
  observed_ground_truth?: string
  source?: string
  target?: string
  [key: string]: unknown
}

export interface CytoscapeElement {
  group: 'nodes' | 'edges'
  data: CytoscapeElementData
  classes?: string
}

// Capabilities
export interface MotifParam {
  name: string
  label: string
  type: 'int' | 'float' | 'string' | 'select'
  default: number | string
  min?: number
  max?: number
  options?: string[]
}

export interface MotifSchema {
  type: string
  label: string
  description: string
  params: MotifParam[]
}

export interface StrategySchema {
  id: string
  label: string
  description: string
  params: MotifParam[]
}

export interface CompositionSchema {
  id: string
  label: string
  description: string
  params: MotifParam[]
}

// Graph generation
export interface MotifConfig {
  type: string
  params: (number | string)[]
}

export interface GraphGenerateRequest {
  motifs: MotifConfig[]
  composition: string
  composition_params: Record<string, unknown>
  num_extra_vertices: number
  num_extra_edges: number
  seed?: number
}

export interface GraphStats {
  num_nodes: number
  num_edges: number
  motif_counts: Record<string, number>
}

export interface GraphGenerateResponse {
  graph_id: string
  elements: CytoscapeElement[]
  stats: GraphStats
}

// Labels
export interface LabelAssignRequest {
  graph_id: string
  motif_order?: string[]
}

export interface LabelDistribution {
  counts: Record<string, number>
}

export interface LabeledGraphResponse {
  graph_id: string
  elements: CytoscapeElement[]
  label_distribution: LabelDistribution
}

// Perturbation
export interface EdgePerturbParams {
  p_remove: number
  p_add: number
  add_num?: number
}

export interface PerturbationRequest {
  graph_id: string
  num_nodes_to_remove: number
  strategy: string
  strategy_params: Record<string, unknown>
  max_iterations: number
  edge_perturb_params?: EdgePerturbParams
  edge_perturb_position: string
}

export interface ChangedNode {
  node_id: string
  old_label: string
  new_label: string
}

export interface EdgeChange {
  source: string
  target: string
}

export interface EdgePerturbInfo {
  removed_edges: EdgeChange[]
  added_edges: EdgeChange[]
}

export interface PerturbationResponse {
  original_graph_id: string
  perturbed_graph_id: string
  original_elements: CytoscapeElement[]
  perturbed_elements: CytoscapeElement[]
  removed_nodes: string[]
  changed_nodes: ChangedNode[]
  edge_perturb_info: Record<string, EdgePerturbInfo>
  success: boolean
  message: string
}

// Dataset
export interface DatasetPerturbParams {
  num_nodes_to_remove: number
  strategy: string
  strategy_params: Record<string, unknown>
  max_iterations: number
  edge_perturb_params?: EdgePerturbParams
  edge_perturb_position: string
}

export interface DatasetGenerateRequest {
  num_graphs: number
  motifs: MotifConfig[]
  num_extra_vertices: number
  num_extra_edges: number
  perturbation_params?: DatasetPerturbParams
  output_dir: string
}

export interface TaskStatus {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  current: number
  total: number
  output_dir?: string
  error?: string
}
