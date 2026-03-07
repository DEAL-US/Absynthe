import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Database, FlaskConical, Network, Tag } from 'lucide-react'
import {
  getCompositions,
  getLabelingFunctions,
  getMotifs,
  getPerturbations,
} from '@/api/capabilities'
import type { MotifSchema } from '@/api/types'
import { PageContainer } from '@/components/layout/PageContainer'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { getLabelColor } from '@/lib/color-map'
import { useGraphState } from '@/hooks/useGraphState'

const PIPELINE_STEPS = [
  {
    to: '/graph',
    icon: Network,
    title: 'Graph Builder',
    description: 'Generate composite graphs from motifs with configurable composition patterns.',
    color: 'from-indigo-500/20 to-violet-500/20',
    border: 'border-indigo-500/20',
  },
  {
    to: '/labels',
    icon: Tag,
    title: 'Label Inspector',
    description: 'Assign ground-truth labels by detecting motif subgraph isomorphisms.',
    color: 'from-emerald-500/20 to-teal-500/20',
    border: 'border-emerald-500/20',
  },
  {
    to: '/perturbation',
    icon: FlaskConical,
    title: 'Perturbation Lab',
    description: 'Remove nodes / perturb edges and observe which labels change.',
    color: 'from-orange-500/20 to-amber-500/20',
    border: 'border-orange-500/20',
  },
  {
    to: '/dataset',
    icon: Database,
    title: 'Dataset Studio',
    description: 'Batch-generate hundreds of labelled perturbation examples in one click.',
    color: 'from-pink-500/20 to-rose-500/20',
    border: 'border-pink-500/20',
  },
]

export function DashboardPage() {
  const navigate = useNavigate()
  const { graphId } = useGraphState()
  const [motifs, setMotifs] = useState<MotifSchema[]>([])
  const [labelerCount, setLabelerCount] = useState(0)
  const [perturbCount, setPerturbCount] = useState(0)
  const [compCount, setCompCount] = useState(0)

  useEffect(() => {
    getMotifs().then(setMotifs).catch(() => {})
    getLabelingFunctions().then((s) => setLabelerCount(s.length)).catch(() => {})
    getPerturbations().then((s) => setPerturbCount(s.length)).catch(() => {})
    getCompositions().then((c) => setCompCount(c.length)).catch(() => {})
  }, [])

  return (
    <PageContainer className="overflow-y-auto">
      {/* Hero */}
      <div className="rounded-2xl border border-brand-500/20 bg-gradient-to-br from-brand-900/40 to-violet-900/20 p-8">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Graphtender</h2>
        <p className="text-gray-400 max-w-xl leading-relaxed">
          A framework for generating benchmarks that test GNN explainability techniques.
          Build graphs, assign motif-based ground-truth labels, apply perturbations, and
          generate datasets — all through an interactive pipeline.
        </p>
        <Button className="mt-5" onClick={() => navigate('/graph')}>
          Start building <ArrowRight className="w-4 h-4" />
        </Button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-5 gap-4">
        {[
          { label: 'Motif types', value: motifs.length || '—' },
          { label: 'Label functions', value: labelerCount || '—' },
          { label: 'Perturbations', value: perturbCount || '—' },
          { label: 'Compositions', value: compCount || '—' },
          { label: 'Loaded graph', value: graphId ? 'Yes' : 'None' },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="rounded-xl border border-white/10 bg-white/5 p-4"
          >
            <p className="text-2xl font-bold text-gray-100 tabular-nums">{value}</p>
            <p className="text-xs text-gray-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Pipeline cards */}
      <div className="grid grid-cols-2 gap-4">
        {PIPELINE_STEPS.map(({ to, icon: Icon, title, description, color, border }) => (
          <Card
            key={to}
            className={`cursor-pointer border ${border} bg-gradient-to-br ${color} hover:scale-[1.01] transition-transform duration-150`}
            onClick={() => navigate(to)}
          >
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center shrink-0">
                  <Icon className="w-4 h-4 text-gray-200" />
                </div>
                <CardTitle>{title}</CardTitle>
              </div>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-200 -ml-2">
                Open <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Available motifs */}
      {motifs.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">
            Available motifs
          </p>
          <div className="flex flex-wrap gap-2">
            {motifs.map((m) => {
              const color = getLabelColor(m.type)
              return (
                <div
                  key={m.type}
                  className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 hover:bg-white/10 transition-colors cursor-pointer"
                  onClick={() => navigate('/graph')}
                >
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: color.bg }} />
                  <span className="text-sm font-medium text-gray-300">{m.label}</span>
                  {m.params.length > 0 && (
                    <span className="text-xs text-gray-600">{m.description}</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </PageContainer>
  )
}
