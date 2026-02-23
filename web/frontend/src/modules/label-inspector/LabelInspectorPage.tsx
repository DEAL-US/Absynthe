import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, Plus, RefreshCw, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { assignLabels } from '@/api/labels'
import { getLabelingFunctions } from '@/api/capabilities'
import type {
  LabelingFunctionConfig,
  LabelingFunctionSchema,
  ParamSchema,
} from '@/api/types'
import { GraphCanvas } from '@/components/graph/GraphCanvas'
import { GraphInfoPanel } from '@/components/graph/GraphInfoPanel'
import { GraphLegend } from '@/components/graph/GraphLegend'
import { PageContainer, PagePanel } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { useGraphState } from '@/hooks/useGraphState'

function schemaDefaults(schema: LabelingFunctionSchema): Record<string, unknown> {
  const defaults: Record<string, unknown> = {}
  for (const param of schema.params) {
    defaults[param.name] = param.default
  }
  return defaults
}

function parseParamValue(param: ParamSchema, raw: string): string | number {
  if (param.type === 'int') return Number.parseInt(raw || '0', 10)
  if (param.type === 'float') return Number.parseFloat(raw || '0')
  return raw
}

export function LabelInspectorPage() {
  const navigate = useNavigate()
  const {
    graphId,
    elements,
    labelDistribution,
    setLabels,
    labelingFunctions: savedLabelingFunctions,
    setLabelingFunctions,
  } = useGraphState()

  const [schemas, setSchemas] = useState<LabelingFunctionSchema[]>([])
  const [configs, setConfigs] = useState<LabelingFunctionConfig[]>(savedLabelingFunctions)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<{ id: string; data: Record<string, unknown> } | null>(null)

  useEffect(() => {
    getLabelingFunctions()
      .then((loaded) => {
        setSchemas(loaded)
        if (configs.length === 0 && loaded.length > 0) {
          setConfigs([{ type: loaded[0].id, params: schemaDefaults(loaded[0]) }])
        }
      })
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const schemaMap = useMemo(
    () => Object.fromEntries(schemas.map((schema) => [schema.id, schema])),
    [schemas],
  )

  const addConfig = (type: string) => {
    const schema = schemaMap[type]
    setConfigs((prev) => [...prev, { type, params: schema ? schemaDefaults(schema) : {} }])
  }

  const removeConfig = (idx: number) => {
    setConfigs((prev) => prev.filter((_, i) => i !== idx))
  }

  const moveConfig = (idx: number, direction: -1 | 1) => {
    setConfigs((prev) => {
      const next = idx + direction
      if (next < 0 || next >= prev.length) return prev
      const copy = [...prev]
      ;[copy[idx], copy[next]] = [copy[next], copy[idx]]
      return copy
    })
  }

  const updateParam = (idx: number, name: string, value: unknown) => {
    setConfigs((prev) =>
      prev.map((cfg, i) => (i === idx ? { ...cfg, params: { ...cfg.params, [name]: value } } : cfg)),
    )
  }

  const handleAssign = async () => {
    if (!graphId || configs.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const res = await assignLabels({
        graph_id: graphId,
        labeling_functions: configs,
      })
      setLabelingFunctions(configs)
      setLabels(res.elements, res.label_distribution, configs)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageContainer split>
      <PagePanel className="w-72 shrink-0 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Labeling functions</p>
        <p className="text-xs text-gray-500 leading-relaxed">
          Add and order labeling modules. Later modules overwrite earlier labels.
        </p>

        <div className="flex flex-col gap-2">
          {configs.map((cfg, idx) => {
            const schema = schemaMap[cfg.type]
            return (
              <Card key={`${cfg.type}-${idx}`} className="border-white/10">
                <CardContent className="p-3 flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-600 font-mono w-4">{idx + 1}</span>
                    <Badge color="#10b981">{schema?.label ?? cfg.type}</Badge>
                    <div className="ml-auto flex items-center gap-1">
                      <button
                        onClick={() => moveConfig(idx, -1)}
                        disabled={idx === 0}
                        className="text-gray-600 hover:text-gray-300 disabled:opacity-30 text-xs px-1"
                      >
                        ↑
                      </button>
                      <button
                        onClick={() => moveConfig(idx, 1)}
                        disabled={idx === configs.length - 1}
                        className="text-gray-600 hover:text-gray-300 disabled:opacity-30 text-xs px-1"
                      >
                        ↓
                      </button>
                      <button
                        onClick={() => removeConfig(idx)}
                        className="text-gray-600 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                  {schema?.params.map((param) => (
                    <div key={`${cfg.type}-${idx}-${param.name}`}>
                      {param.type === 'select' ? (
                        <Select
                          label={param.label}
                          value={String(cfg.params[param.name] ?? param.default)}
                          onValueChange={(value) => updateParam(idx, param.name, value)}
                          options={(param.options ?? []).map((opt) => ({ value: opt, label: opt }))}
                        />
                      ) : (
                        <Input
                          label={param.label}
                          type={param.type === 'string' ? 'text' : 'number'}
                          value={String(cfg.params[param.name] ?? param.default)}
                          onChange={(e) =>
                            updateParam(
                              idx,
                              param.name,
                              parseParamValue(param, e.target.value),
                            )
                          }
                        />
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            )
          })}
        </div>

        {schemas.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {schemas.map((schema) => (
              <Button key={schema.id} variant="outline" size="sm" onClick={() => addConfig(schema.id)}>
                <Plus className="w-3 h-3" />
                {schema.label}
              </Button>
            ))}
          </div>
        )}

        {!graphId && (
          <p className="text-xs text-amber-400 bg-amber-900/20 rounded-lg p-2">
            No graph loaded. Go to Graph Builder first.
          </p>
        )}
        {error && <p className="text-xs text-red-400 bg-red-900/20 rounded-lg p-2">{error}</p>}

        <Button
          onClick={handleAssign}
          loading={loading}
          disabled={!graphId || configs.length === 0}
          className="w-full"
        >
          <RefreshCw className="w-4 h-4" />
          Assign Labels
        </Button>

        {labelDistribution && (
          <>
            <div className="border-t border-white/10 pt-4">
              <GraphLegend counts={labelDistribution.counts} />
            </div>
            <Button variant="outline" onClick={() => navigate('/perturbation')} className="w-full">
              Perturbation Lab <ArrowRight className="w-4 h-4" />
            </Button>
          </>
        )}
      </PagePanel>

      <div className="flex-1 min-w-0 relative rounded-2xl border border-white/10 overflow-hidden">
        <GraphCanvas
          elements={elements}
          toolbar
          onNodeClick={(id, data) => setSelectedNode({ id, data: data as Record<string, unknown> })}
          className="h-full"
        />
        {selectedNode && (
          <GraphInfoPanel
            nodeId={selectedNode.id}
            data={selectedNode.data}
            onClose={() => setSelectedNode(null)}
          />
        )}
      </div>
    </PageContainer>
  )
}
