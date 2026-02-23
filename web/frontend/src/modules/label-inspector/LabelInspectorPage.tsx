import { useEffect, useState } from 'react'
import { ArrowRight, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getMotifs } from '@/api/capabilities'
import { assignLabels } from '@/api/labels'
import type { MotifSchema } from '@/api/types'
import { GraphCanvas } from '@/components/graph/GraphCanvas'
import { GraphInfoPanel } from '@/components/graph/GraphInfoPanel'
import { GraphLegend } from '@/components/graph/GraphLegend'
import { PageContainer, PagePanel } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { getLabelColor } from '@/lib/color-map'
import { useGraphState } from '@/hooks/useGraphState'

export function LabelInspectorPage() {
  const navigate = useNavigate()
  const { graphId, elements, labelDistribution, setLabels } = useGraphState()
  const [motifSchemas, setMotifSchemas] = useState<MotifSchema[]>([])
  // Each entry tracks its name, order position, and whether it's enabled
  const [motifEntries, setMotifEntries] = useState<{ name: string; enabled: boolean }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<{ id: string; data: Record<string, unknown> } | null>(null)

  useEffect(() => {
    getMotifs().then((schemas) => {
      setMotifSchemas(schemas)
      setMotifEntries(schemas.map((s) => ({ name: s.type, enabled: true })))
    }).catch(() => {})
  }, [])

  // Only pass enabled motifs to the backend, in the displayed order
  const activeMotifOrder = motifEntries.filter((e) => e.enabled).map((e) => e.name)

  const handleAssign = async () => {
    if (!graphId) return
    setLoading(true)
    setError(null)
    try {
      const res = await assignLabels({
        graph_id: graphId,
        motif_order: activeMotifOrder.length ? activeMotifOrder : undefined,
      })
      setLabels(res.elements, res.label_distribution)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const toggleEnabled = (i: number) => {
    setMotifEntries((prev) =>
      prev.map((entry, j) => (j === i ? { ...entry, enabled: !entry.enabled } : entry)),
    )
  }

  const moveUp = (i: number) => {
    if (i === 0) return
    setMotifEntries((prev) => {
      const next = [...prev]
      ;[next[i - 1], next[i]] = [next[i], next[i - 1]]
      return next
    })
  }

  const moveDown = (i: number) => {
    setMotifEntries((prev) => {
      if (i === prev.length - 1) return prev
      const next = [...prev]
      ;[next[i], next[i + 1]] = [next[i + 1], next[i]]
      return next
    })
  }

  return (
    <PageContainer split>
      <PagePanel className="w-64 shrink-0 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Labeling priority</p>
        <p className="text-xs text-gray-500 leading-relaxed">
          Motifs are applied bottom-to-top. Higher items overwrite lower ones.
          Disable a motif to exclude it from labeling.
        </p>

        <div className="flex flex-col gap-1.5">
          {motifEntries.map((entry, i) => {
            const color = getLabelColor(entry.name)
            return (
              <Card
                key={entry.name}
                className={`border-white/10 transition-opacity ${entry.enabled ? '' : 'opacity-40'}`}
              >
                <CardContent className="p-2.5 flex items-center gap-2">
                  {/* Enable / disable checkbox */}
                  <label className="relative inline-flex items-center cursor-pointer shrink-0">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={entry.enabled}
                      onChange={() => toggleEnabled(i)}
                    />
                    <div
                      className="w-4 h-4 rounded border-2 transition-colors peer-checked:border-transparent peer-checked:bg-current flex items-center justify-center"
                      style={{
                        borderColor: entry.enabled ? 'transparent' : color.bg + '66',
                        backgroundColor: entry.enabled ? color.bg : 'transparent',
                      }}
                    >
                      {entry.enabled && (
                        <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </label>

                  <span className="text-xs text-gray-600 font-mono w-4">{i + 1}</span>
                  <Badge variant="dot" color={color.text}>{entry.name}</Badge>

                  <div className="ml-auto flex gap-0.5">
                    <button
                      onClick={() => moveUp(i)}
                      disabled={i === 0}
                      className="text-gray-600 hover:text-gray-300 disabled:opacity-30 px-1 text-xs transition-colors"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => moveDown(i)}
                      disabled={i === motifEntries.length - 1}
                      className="text-gray-600 hover:text-gray-300 disabled:opacity-30 px-1 text-xs transition-colors"
                    >
                      ↓
                    </button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Summary of active labels */}
        <p className="text-xs text-gray-500">
          {activeMotifOrder.length} of {motifEntries.length} labelers active
        </p>

        {!graphId && (
          <p className="text-xs text-amber-400 bg-amber-900/20 rounded-lg p-2">
            No graph loaded. Go to Graph Builder first.
          </p>
        )}
        {error && <p className="text-xs text-red-400 bg-red-900/20 rounded-lg p-2">{error}</p>}

        <Button onClick={handleAssign} loading={loading} disabled={!graphId} className="w-full">
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
