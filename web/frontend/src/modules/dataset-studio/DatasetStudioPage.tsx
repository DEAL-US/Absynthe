import { useEffect, useRef, useState } from 'react'
import { Database, Download, Play } from 'lucide-react'
import { generateDataset } from '@/api/dataset'
import { getMotifs, getStrategies } from '@/api/capabilities'
import type { MotifConfig, MotifSchema, StrategySchema, TaskStatus } from '@/api/types'
import { PageContainer, PagePanel } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Progress } from '@/components/ui/Progress'
import { Select } from '@/components/ui/Select'
import { Slider } from '@/components/ui/Slider'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Card, CardContent } from '@/components/ui/Card'

export function DatasetStudioPage() {
  const [motifSchemas, setMotifSchemas] = useState<MotifSchema[]>([])
  const [stratSchemas, setStratSchemas] = useState<StrategySchema[]>([])

  // Config
  const [numGraphs, setNumGraphs] = useState(20)
  const [motifs, setMotifs] = useState<MotifConfig[]>([{ type: 'cycle', params: [4] }, { type: 'house', params: [] }])
  const [extraV, setExtraV] = useState(0)
  const [extraE, setExtraE] = useState(0)
  const [pertEnabled, setPertEnabled] = useState(true)
  const [strategy, setStrategy] = useState('random')
  const [numNodes, setNumNodes] = useState(1)
  const [maxIter, setMaxIter] = useState(10)
  const [outputDir, setOutputDir] = useState('datasets/output')

  // Task tracking
  const [taskId, setTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [completedTasks, setCompletedTasks] = useState<TaskStatus[]>([])

  // WebSocket URL — only active when task is running
  const wsUrl = taskId && taskStatus?.status === 'running'
    ? `/ws/dataset/${taskId}`
    : null

  useWebSocket<TaskStatus>({
    url: wsUrl,
    onMessage: (data) => {
      setTaskStatus(data)
      if (data.status === 'completed' || data.status === 'failed') {
        setCompletedTasks((prev) => [data, ...prev.slice(0, 9)])
        setTaskId(null)
        setLoading(false)
      }
    },
  })

  useEffect(() => {
    getMotifs().then(setMotifSchemas).catch(() => {})
    getStrategies().then(setStratSchemas).catch(() => {})
  }, [])

  const addMotif = (type: string) => setMotifs((p) => [...p, { type, params: [] }])
  const removeMotif = (i: number) => setMotifs((p) => p.filter((_, j) => j !== i))

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      const { task_id } = await generateDataset({
        num_graphs: numGraphs,
        motifs,
        num_extra_vertices: extraV,
        num_extra_edges: extraE,
        output_dir: outputDir,
        perturbation_params: pertEnabled
          ? { num_nodes_to_remove: numNodes, strategy, strategy_params: {}, max_iterations: maxIter, edge_perturb_position: 'after' }
          : undefined,
      })
      setTaskId(task_id)
      setTaskStatus({ task_id, status: 'pending', current: 0, total: numGraphs })
    } catch (e) {
      setError((e as Error).message)
      setLoading(false)
    }
  }

  const isRunning = taskStatus?.status === 'running' || taskStatus?.status === 'pending'

  return (
    <PageContainer split>
      {/* Config */}
      <PagePanel className="w-72 shrink-0 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Dataset Config</p>

        <Slider label="Number of graphs" value={numGraphs} min={1} max={1000} step={1} onValueChange={setNumGraphs} />

        <div className="border-t border-white/10 pt-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Motifs</p>
          <div className="flex flex-col gap-1.5 mb-2">
            {motifs.map((m, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2">
                <Badge color="#6366f1">{m.type}</Badge>
                {m.params.length > 0 && (
                  <span className="text-xs text-gray-500 font-mono">{m.params.join(', ')}</span>
                )}
                <button onClick={() => removeMotif(i)} className="ml-auto text-gray-600 hover:text-red-400 transition-colors text-xs">×</button>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap gap-1">
            {motifSchemas.map((s) => (
              <Button key={s.type} variant="outline" size="sm" onClick={() => addMotif(s.type)}>
                + {s.label}
              </Button>
            ))}
          </div>
        </div>

        <div className="border-t border-white/10 pt-3 flex flex-col gap-2">
          <Slider label="Extra vertices" value={extraV} min={0} max={20} onValueChange={setExtraV} />
          <Slider label="Extra edges" value={extraE} min={0} max={20} onValueChange={setExtraE} />
        </div>

        {/* Perturbation toggle */}
        <div className="border-t border-white/10 pt-3 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Perturbation</p>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" checked={pertEnabled} onChange={(e) => setPertEnabled(e.target.checked)} />
              <div className="w-9 h-5 bg-white/10 rounded-full peer peer-checked:bg-brand-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4" />
            </label>
          </div>
          {pertEnabled && (
            <>
              <Select label="Strategy" value={strategy} onValueChange={setStrategy} options={stratSchemas.map((s) => ({ value: s.id, label: s.label }))} />
              <Slider label="Nodes to remove" value={numNodes} min={1} max={10} onValueChange={setNumNodes} />
              <Slider label="Max iterations" value={maxIter} min={1} max={50} onValueChange={setMaxIter} />
            </>
          )}
        </div>

        <Input label="Output directory" value={outputDir} onChange={(e) => setOutputDir(e.target.value)} />

        {error && <p className="text-xs text-red-400 bg-red-900/20 rounded-lg p-2">{error}</p>}

        <Button onClick={handleStart} loading={loading} disabled={isRunning || motifs.length === 0} className="w-full">
          <Play className="w-4 h-4" />
          Generate Dataset
        </Button>
      </PagePanel>

      {/* Status + history */}
      <div className="flex-1 min-w-0 flex flex-col gap-5 overflow-y-auto">
        {/* Active task */}
        {taskStatus && (
          <PagePanel>
            <div className="flex items-center gap-2 mb-1">
              <Database className="w-4 h-4 text-brand-400" />
              <p className="text-sm font-semibold text-gray-200">Generation in progress</p>
              <Badge
                className={
                  taskStatus.status === 'completed'
                    ? 'bg-green-500/20 text-green-300 border-green-500/30'
                    : taskStatus.status === 'failed'
                    ? 'bg-red-500/20 text-red-300 border-red-500/30'
                    : 'bg-brand-600/20 text-brand-300 border-brand-500/30'
                }
              >
                {taskStatus.status}
              </Badge>
            </div>
            <Progress
              value={taskStatus.current}
              max={taskStatus.total || numGraphs}
              label="Graphs generated"
            />
            {taskStatus.output_dir && (
              <p className="text-xs text-gray-500 font-mono">{taskStatus.output_dir}</p>
            )}
            {taskStatus.error && (
              <p className="text-xs text-red-400">{taskStatus.error}</p>
            )}
          </PagePanel>
        )}

        {/* No active task placeholder */}
        {!taskStatus && completedTasks.length === 0 && (
          <div className="flex flex-col items-center justify-center flex-1 gap-3 text-gray-600">
            <Database className="w-12 h-12 opacity-30" />
            <p className="text-sm">Configure and start a generation run</p>
          </div>
        )}

        {/* Completed tasks */}
        {completedTasks.length > 0 && (
          <div className="flex flex-col gap-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Recent runs</p>
            {completedTasks.map((t) => (
              <Card key={t.task_id} className="border-white/10">
                <CardContent className="p-3 flex items-center gap-3">
                  <Badge
                    className={
                      t.status === 'completed'
                        ? 'bg-green-500/20 text-green-300 border-green-500/30'
                        : 'bg-red-500/20 text-red-300 border-red-500/30'
                    }
                  >
                    {t.status}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-300 font-mono truncate">{t.output_dir ?? t.task_id}</p>
                    <p className="text-xs text-gray-500">{t.current} / {t.total} graphs</p>
                  </div>
                  {t.status === 'completed' && t.output_dir && (
                    <Button variant="ghost" size="sm" title="Open folder">
                      <Download className="w-3.5 h-3.5" />
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </PageContainer>
  )
}
