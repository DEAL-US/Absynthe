import { useEffect, useState } from 'react'
import { FlaskConical } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getStrategies } from '@/api/capabilities'
import { applyPerturbation } from '@/api/perturbation'
import type { PerturbationResponse, StrategySchema } from '@/api/types'
import { GraphDiffView } from '@/components/graph/GraphDiffView'
import { PageContainer, PagePanel } from '@/components/layout/PageContainer'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Slider } from '@/components/ui/Slider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { useGraphState } from '@/hooks/useGraphState'

export function PerturbationLabPage() {
  const navigate = useNavigate()
  const { graphId, elements, setPerturbationResult, perturbationResult } = useGraphState()

  const [strategies, setStrategies] = useState<StrategySchema[]>([])
  const [strategy, setStrategy] = useState('random')
  const [numNodes, setNumNodes] = useState(1)
  const [maxIter, setMaxIter] = useState(10)
  const [edgeEnabled, setEdgeEnabled] = useState(false)
  const [pRemove, setPRemove] = useState(0.0)
  const [pAdd, setPAdd] = useState(0.0)
  const [edgePos, setEdgePos] = useState('after')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getStrategies().then(setStrategies).catch(() => {})
  }, [])

  const handleApply = async () => {
    if (!graphId) return
    setLoading(true)
    setError(null)
    try {
      const res = await applyPerturbation({
        graph_id: graphId,
        num_nodes_to_remove: numNodes,
        strategy,
        strategy_params: {},
        max_iterations: maxIter,
        edge_perturb_params: edgeEnabled ? { p_remove: pRemove, p_add: pAdd } : undefined,
        edge_perturb_position: edgePos,
      })
      setPerturbationResult(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageContainer split>
      {/* Config panel */}
      <PagePanel className="w-64 shrink-0 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Perturbation</p>

        <Select
          label="Strategy"
          value={strategy}
          onValueChange={setStrategy}
          options={strategies.map((s) => ({ value: s.id, label: s.label }))}
        />

        <Slider
          label="Nodes to remove"
          value={numNodes}
          min={1}
          max={10}
          onValueChange={setNumNodes}
        />

        <Slider
          label="Max iterations"
          value={maxIter}
          min={1}
          max={50}
          onValueChange={setMaxIter}
        />

        {/* Edge perturbation toggle */}
        <div className="border-t border-white/10 pt-4 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Edge perturbation</p>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={edgeEnabled}
                onChange={(e) => setEdgeEnabled(e.target.checked)}
              />
              <div className="w-9 h-5 bg-white/10 rounded-full peer peer-checked:bg-brand-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4" />
            </label>
          </div>

          {edgeEnabled && (
            <>
              <Slider label="Remove prob." value={pRemove} min={0} max={1} step={0.05} onValueChange={setPRemove} />
              <Slider label="Add prob." value={pAdd} min={0} max={1} step={0.05} onValueChange={setPAdd} />
              <Select
                label="Apply when"
                value={edgePos}
                onValueChange={setEdgePos}
                options={[
                  { value: 'before', label: 'Before node removal' },
                  { value: 'after', label: 'After node removal' },
                ]}
              />
            </>
          )}
        </div>

        {!graphId && (
          <p className="text-xs text-amber-400 bg-amber-900/20 rounded-lg p-2">
            No graph loaded. Generate a graph first.
          </p>
        )}
        {error && <p className="text-xs text-red-400 bg-red-900/20 rounded-lg p-2">{error}</p>}

        {perturbationResult && !perturbationResult.success && (
          <p className="text-xs text-amber-400 bg-amber-900/20 rounded-lg p-2">
            {perturbationResult.message}
          </p>
        )}

        <Button onClick={handleApply} loading={loading} disabled={!graphId} className="w-full">
          <FlaskConical className="w-4 h-4" />
          Apply Perturbation
        </Button>

        {perturbationResult?.success && (
          <Button variant="outline" onClick={() => navigate('/dataset')} className="w-full">
            Dataset Studio →
          </Button>
        )}
      </PagePanel>

      {/* Results panel */}
      <div className="flex-1 min-w-0 overflow-hidden">
        {perturbationResult ? (
          <GraphDiffView
            originalElements={perturbationResult.original_elements}
            perturbedElements={perturbationResult.perturbed_elements}
            removedNodes={perturbationResult.removed_nodes}
            changedNodes={perturbationResult.changed_nodes}
            edgePerturbInfo={perturbationResult.edge_perturb_info}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-gray-600">
            <FlaskConical className="w-12 h-12 opacity-30" />
            <p className="text-sm">Configure and apply a perturbation to see the diff view</p>
          </div>
        )}
      </div>
    </PageContainer>
  )
}
