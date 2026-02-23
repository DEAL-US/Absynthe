import { useEffect, useState } from 'react'
import { GripVertical, Plus, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getCompositions, getMotifs } from '@/api/capabilities'
import { generateGraph } from '@/api/graph'
import type { CompositionSchema, MotifConfig, MotifSchema } from '@/api/types'
import { GraphCanvas } from '@/components/graph/GraphCanvas'
import { GraphInfoPanel } from '@/components/graph/GraphInfoPanel'
import { PageContainer, PagePanel } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Slider } from '@/components/ui/Slider'
import { useGraphState } from '@/hooks/useGraphState'

export function GraphBuilderPage() {
  const navigate = useNavigate()
  const { setGraph, elements, graphId } = useGraphState()

  const [motifSchemas, setMotifSchemas] = useState<MotifSchema[]>([])
  const [compSchemas, setCompSchemas] = useState<CompositionSchema[]>([])
  const [motifs, setMotifs] = useState<MotifConfig[]>([{ type: 'cycle', params: [4] }, { type: 'house', params: [] }])
  const [composition, setComposition] = useState('sequential')
  const [compParams, setCompParams] = useState<Record<string, number | string>>({})
  const [extraVertices, setExtraVertices] = useState(0)
  const [extraEdges, setExtraEdges] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<{ id: string; data: Record<string, unknown> } | null>(null)

  useEffect(() => {
    getMotifs().then(setMotifSchemas).catch(() => {})
    getCompositions().then(setCompSchemas).catch(() => {})
  }, [])

  const selectedCompSchema = compSchemas.find((c) => c.id === composition)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await generateGraph({
        motifs,
        composition,
        composition_params: compParams,
        num_extra_vertices: extraVertices,
        num_extra_edges: extraEdges,
      })
      setGraph(res.graph_id, res.elements)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const addMotif = (type: string) => {
    const schema = motifSchemas.find((m) => m.type === type)
    const params = schema?.params.map((p) => p.default as number) ?? []
    setMotifs((prev) => [...prev, { type, params }])
  }

  const updateMotifParam = (idx: number, paramIdx: number, value: number | string) => {
    setMotifs((prev) =>
      prev.map((m, i) => {
        if (i !== idx) return m
        const newParams = [...m.params]
        newParams[paramIdx] = value
        return { ...m, params: newParams }
      }),
    )
  }

  const removeMotif = (idx: number) => setMotifs((prev) => prev.filter((_, i) => i !== idx))

  const parseParam = (type: string, value: string): number | string => {
    if (type === 'int') return Number.parseInt(value || '0', 10)
    if (type === 'float') return Number.parseFloat(value || '0')
    return value
  }

  return (
    <PageContainer split>
      {/* ── Left: Config ──────────────────────────────────── */}
      <PagePanel className="w-72 shrink-0 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Motifs</p>

        {/* Motif list */}
        <div className="flex flex-col gap-2">
          {motifs.map((m, idx) => {
            const schema = motifSchemas.find((s) => s.type === m.type)
            return (
              <Card key={idx} className="border-white/10">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <GripVertical className="w-4 h-4 text-gray-600 shrink-0" />
                    <Badge color="#6366f1">{m.type}</Badge>
                    <button
                      onClick={() => removeMotif(idx)}
                      className="ml-auto text-gray-600 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  {schema?.params.map((p, pi) => (
                    <div key={p.name} className="mt-2">
                      <Slider
                        label={p.label}
                        value={(m.params[pi] as number) ?? (p.default as number)}
                        min={p.min ?? 1}
                        max={(p.max as number) ?? 20}
                        onValueChange={(v) => updateMotifParam(idx, pi, v)}
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Add motif */}
        {motifSchemas.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {motifSchemas.map((s) => (
              <Button key={s.type} variant="outline" size="sm" onClick={() => addMotif(s.type)}>
                <Plus className="w-3 h-3" />
                {s.label}
              </Button>
            ))}
          </div>
        )}

        <div className="border-t border-white/10 pt-4 flex flex-col gap-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Composition</p>
          <Select
            value={composition}
            onValueChange={(v) => { setComposition(v); setCompParams({}) }}
            options={compSchemas.map((c) => ({ value: c.id, label: c.label }))}
            label="Pattern"
          />
          {selectedCompSchema?.params.map((p) => (
            <Input
              key={p.name}
              label={p.label}
              type={p.type === 'string' ? 'text' : 'number'}
              value={String(compParams[p.name] ?? p.default)}
              onChange={(e) =>
                setCompParams((prev) => ({
                  ...prev,
                  [p.name]: parseParam(p.type, e.target.value),
                }))
              }
            />
          ))}
        </div>

        <div className="border-t border-white/10 pt-4 flex flex-col gap-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Extras</p>
          <Slider
            label="Extra vertices"
            value={extraVertices}
            min={0}
            max={20}
            onValueChange={setExtraVertices}
          />
          <Slider
            label="Extra edges"
            value={extraEdges}
            min={0}
            max={20}
            onValueChange={setExtraEdges}
          />
        </div>

        {error && <p className="text-xs text-red-400 bg-red-900/20 rounded-lg p-2">{error}</p>}

        <Button onClick={handleGenerate} loading={loading} className="w-full">
          Generate Graph
        </Button>

        {graphId && (
          <Button variant="outline" onClick={() => navigate('/labels')} className="w-full">
            Assign Labels →
          </Button>
        )}
      </PagePanel>

      {/* ── Right: Graph canvas ────────────────────────────── */}
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
