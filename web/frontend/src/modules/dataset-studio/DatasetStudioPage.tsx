import { useEffect, useMemo, useState } from 'react'
import { Database, Download, FolderUp, Play, Plus, Trash2 } from 'lucide-react'
import { generateDataset } from '@/api/dataset'
import {
  getCompositions,
  getLabelingFunctions,
  getMotifs,
  getPerturbations,
} from '@/api/capabilities'
import type {
  CompositionSchema,
  LabelingFunctionConfig,
  LabelingFunctionSchema,
  MotifConfig,
  MotifSchema,
  ParamSchema,
  PerturbationConfig,
  PerturbationSchema,
  TaskStatus,
} from '@/api/types'
import { PageContainer, PagePanel } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Progress } from '@/components/ui/Progress'
import { Select } from '@/components/ui/Select'
import { Slider } from '@/components/ui/Slider'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Card, CardContent } from '@/components/ui/Card'
import { useGraphState } from '@/hooks/useGraphState'

function schemaDefaults(schema: { params: ParamSchema[] }): Record<string, unknown> {
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

export function DatasetStudioPage() {
  const {
    labelingFunctions: savedLabeling,
    perturbations: savedPerturbations,
    graphSource,
    uploadFolderPath,
    uploadFileCount,
  } = useGraphState()

  const isUploadMode = graphSource === 'upload' && !!uploadFolderPath

  const [motifSchemas, setMotifSchemas] = useState<MotifSchema[]>([])
  const [compositionSchemas, setCompositionSchemas] = useState<CompositionSchema[]>([])
  const [labelingSchemas, setLabelingSchemas] = useState<LabelingFunctionSchema[]>([])
  const [perturbationSchemas, setPerturbationSchemas] = useState<PerturbationSchema[]>([])

  const [numGraphs, setNumGraphs] = useState(20)
  const [motifs, setMotifs] = useState<MotifConfig[]>([{ type: 'cycle', params: [4] }, { type: 'house', params: [] }])
  const [composition, setComposition] = useState('sequential')
  const [compositionParams, setCompositionParams] = useState<Record<string, unknown>>({})
  const [extraV, setExtraV] = useState(0)
  const [extraE, setExtraE] = useState(0)
  const [labelingFunctions, setLabelingFunctions] = useState<LabelingFunctionConfig[]>(savedLabeling)
  const [perturbations, setPerturbations] = useState<PerturbationConfig[]>(savedPerturbations)
  const [maxPerturbIter, setMaxPerturbIter] = useState(10)
  const [outputDir, setOutputDir] = useState('datasets/output')
  const [iterationOrder, setIterationOrder] = useState('sequential')
  const [exhaustionPolicy, setExhaustionPolicy] = useState('stop')

  const [taskId, setTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [completedTasks, setCompletedTasks] = useState<TaskStatus[]>([])

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
    getCompositions().then(setCompositionSchemas).catch(() => {})
    getLabelingFunctions()
      .then((schemas) => {
        setLabelingSchemas(schemas)
        if (labelingFunctions.length === 0 && schemas.length > 0) {
          setLabelingFunctions([{ type: schemas[0].id, params: schemaDefaults(schemas[0]) }])
        }
      })
      .catch(() => {})
    getPerturbations()
      .then((schemas) => {
        setPerturbationSchemas(schemas)
        if (perturbations.length === 0 && schemas.length > 0) {
          setPerturbations([{ type: schemas[0].id, params: schemaDefaults(schemas[0]), count: 1 }])
        }
      })
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const compositionSchema = compositionSchemas.find((schema) => schema.id === composition)
  const labelSchemaMap = useMemo(
    () => Object.fromEntries(labelingSchemas.map((schema) => [schema.id, schema])),
    [labelingSchemas],
  )
  const perturbSchemaMap = useMemo(
    () => Object.fromEntries(perturbationSchemas.map((schema) => [schema.id, schema])),
    [perturbationSchemas],
  )

  const addMotif = (type: string) => {
    const schema = motifSchemas.find((s) => s.type === type)
    setMotifs((prev) => [...prev, { type, params: schema?.params.map((p) => p.default) ?? [] }])
  }

  const removeMotif = (idx: number) => {
    setMotifs((prev) => prev.filter((_, i) => i !== idx))
  }

  const addLabeling = (type: string) => {
    const schema = labelSchemaMap[type]
    setLabelingFunctions((prev) => [...prev, { type, params: schema ? schemaDefaults(schema) : {} }])
  }

  const updateLabelingParam = (idx: number, name: string, value: unknown) => {
    setLabelingFunctions((prev) =>
      prev.map((cfg, i) => (i === idx ? { ...cfg, params: { ...cfg.params, [name]: value } } : cfg)),
    )
  }

  const removeLabeling = (idx: number) => {
    setLabelingFunctions((prev) => prev.filter((_, i) => i !== idx))
  }

  const addPerturbation = (type: string) => {
    const schema = perturbSchemaMap[type]
    setPerturbations((prev) => [
      ...prev,
      { type, params: schema ? schemaDefaults(schema) : {}, count: 1 },
    ])
  }

  const updatePerturbParam = (idx: number, name: string, value: unknown) => {
    setPerturbations((prev) =>
      prev.map((cfg, i) => (i === idx ? { ...cfg, params: { ...cfg.params, [name]: value } } : cfg)),
    )
  }

  const updatePerturbCount = (idx: number, count: number) => {
    setPerturbations((prev) =>
      prev.map((cfg, i) => (i === idx ? { ...cfg, count } : cfg)),
    )
  }

  const removePerturbation = (idx: number) => {
    setPerturbations((prev) => prev.filter((_, i) => i !== idx))
  }

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      const { task_id } = await generateDataset(
        isUploadMode
          ? {
              num_graphs: numGraphs,
              folder_source: {
                folder_path: uploadFolderPath!,
                iteration_order: iterationOrder,
                exhaustion_policy: exhaustionPolicy,
              },
              labeling_functions: labelingFunctions,
              perturbations,
              max_perturbation_iterations: maxPerturbIter,
              output_dir: outputDir,
            }
          : {
              num_graphs: numGraphs,
              motifs,
              composition,
              composition_params: compositionParams,
              num_extra_vertices: extraV,
              num_extra_edges: extraE,
              labeling_functions: labelingFunctions,
              perturbations,
              max_perturbation_iterations: maxPerturbIter,
              output_dir: outputDir,
            },
      )
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
      <PagePanel className="w-80 shrink-0 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Dataset Config</p>
        <Slider label="Number of graphs" value={numGraphs} min={1} max={1000} step={1} onValueChange={setNumGraphs} />

        {isUploadMode ? (
          <div className="border-t border-white/10 pt-3 flex flex-col gap-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Graph Source</p>
            <div className="flex items-center gap-2 rounded-lg bg-brand-900/20 border border-brand-500/20 px-3 py-2.5">
              <FolderUp className="w-4 h-4 text-brand-400 shrink-0" />
              <div>
                <p className="text-xs text-brand-300 font-medium">Using {uploadFileCount} uploaded graphs</p>
              </div>
            </div>
            <Select
              label="Iteration Order"
              value={iterationOrder}
              onValueChange={setIterationOrder}
              options={[
                { value: 'sequential', label: 'Sequential' },
                { value: 'random', label: 'Random' },
              ]}
            />
            <Select
              label="Exhaustion Policy"
              value={exhaustionPolicy}
              onValueChange={setExhaustionPolicy}
              options={[
                { value: 'stop', label: 'Stop' },
                { value: 'cycle', label: 'Cycle' },
                { value: 'raise', label: 'Raise' },
              ]}
            />
          </div>
        ) : (
          <>
            <div className="border-t border-white/10 pt-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Motifs</p>
              <div className="flex flex-col gap-1.5 mb-2">
                {motifs.map((motif, idx) => (
                  <div key={`${motif.type}-${idx}`} className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2">
                    <Badge color="#6366f1">{motif.type}</Badge>
                    {motif.params.length > 0 && (
                      <span className="text-xs text-gray-500 font-mono">{motif.params.join(', ')}</span>
                    )}
                    <button onClick={() => removeMotif(idx)} className="ml-auto text-gray-600 hover:text-red-400 transition-colors text-xs">×</button>
                  </div>
                ))}
              </div>
              <div className="flex flex-wrap gap-1">
                {motifSchemas.map((schema) => (
                  <Button key={schema.type} variant="outline" size="sm" onClick={() => addMotif(schema.type)}>
                    + {schema.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="border-t border-white/10 pt-3 flex flex-col gap-2">
              <Select
                label="Composition"
                value={composition}
                onValueChange={(value) => {
                  setComposition(value)
                  setCompositionParams({})
                }}
                options={compositionSchemas.map((schema) => ({ value: schema.id, label: schema.label }))}
              />
              {compositionSchema?.params.map((param) => (
                <Input
                  key={param.name}
                  label={param.label}
                  type={param.type === 'string' ? 'text' : 'number'}
                  value={String(compositionParams[param.name] ?? param.default)}
                  onChange={(e) =>
                    setCompositionParams((prev) => ({
                      ...prev,
                      [param.name]: parseParamValue(param, e.target.value),
                    }))
                  }
                />
              ))}
              <Slider label="Extra vertices" value={extraV} min={0} max={20} onValueChange={setExtraV} />
              <Slider label="Extra edges" value={extraE} min={0} max={20} onValueChange={setExtraE} />
            </div>
          </>
        )}

        <div className="border-t border-white/10 pt-3 flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Labeling functions</p>
          {labelingFunctions.map((cfg, idx) => {
            const schema = labelSchemaMap[cfg.type]
            return (
              <Card key={`${cfg.type}-${idx}`} className="border-white/10">
                <CardContent className="p-2.5 flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <Badge color="#10b981">{schema?.label ?? cfg.type}</Badge>
                    <button onClick={() => removeLabeling(idx)} className="ml-auto text-gray-600 hover:text-red-400">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  {schema?.params.map((param) => (
                    <Input
                      key={`${cfg.type}-${idx}-${param.name}`}
                      label={param.label}
                      type={param.type === 'string' ? 'text' : 'number'}
                      value={String(cfg.params[param.name] ?? param.default)}
                      onChange={(e) =>
                        updateLabelingParam(idx, param.name, parseParamValue(param, e.target.value))
                      }
                    />
                  ))}
                </CardContent>
              </Card>
            )
          })}
          <div className="flex flex-wrap gap-1">
            {labelingSchemas.map((schema) => (
              <Button key={schema.id} variant="outline" size="sm" onClick={() => addLabeling(schema.id)}>
                <Plus className="w-3 h-3" />
                {schema.label}
              </Button>
            ))}
          </div>
        </div>

        <div className="border-t border-white/10 pt-3 flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Perturbations</p>
          {perturbations.map((cfg, idx) => {
            const schema = perturbSchemaMap[cfg.type]
            return (
              <Card key={`${cfg.type}-${idx}`} className="border-white/10">
                <CardContent className="p-2.5 flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <Badge color="#f59e0b">{schema?.label ?? cfg.type}</Badge>
                    <button onClick={() => removePerturbation(idx)} className="ml-auto text-gray-600 hover:text-red-400">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <Slider
                    label="Desired count"
                    value={cfg.count}
                    min={1}
                    max={10}
                    onValueChange={(value) => updatePerturbCount(idx, value)}
                  />
                  {schema?.params.map((param) => (
                    param.type === 'select' ? (
                      <Select
                        key={`${cfg.type}-${idx}-${param.name}`}
                        label={param.label}
                        value={String(cfg.params[param.name] ?? param.default)}
                        onValueChange={(value) => updatePerturbParam(idx, param.name, value)}
                        options={(param.options ?? []).map((opt) => ({ value: opt, label: opt }))}
                      />
                    ) : (
                      <Input
                        key={`${cfg.type}-${idx}-${param.name}`}
                        label={param.label}
                        type={param.type === 'string' ? 'text' : 'number'}
                        value={String(cfg.params[param.name] ?? param.default)}
                        onChange={(e) =>
                          updatePerturbParam(idx, param.name, parseParamValue(param, e.target.value))
                        }
                      />
                    )
                  ))}
                </CardContent>
              </Card>
            )
          })}
          <div className="flex flex-wrap gap-1">
            {perturbationSchemas.map((schema) => (
              <Button key={schema.id} variant="outline" size="sm" onClick={() => addPerturbation(schema.id)}>
                <Plus className="w-3 h-3" />
                {schema.label}
              </Button>
            ))}
          </div>
          <Slider
            label="Max perturbation iterations"
            value={maxPerturbIter}
            min={1}
            max={100}
            onValueChange={setMaxPerturbIter}
          />
        </div>

        <Input label="Output directory" value={outputDir} onChange={(e) => setOutputDir(e.target.value)} />
        {error && <p className="text-xs text-red-400 bg-red-900/20 rounded-lg p-2">{error}</p>}
        <Button onClick={handleStart} loading={loading} disabled={isRunning || (!isUploadMode && motifs.length === 0)} className="w-full">
          <Play className="w-4 h-4" />
          Generate Dataset
        </Button>
      </PagePanel>

      <div className="flex-1 min-w-0 flex flex-col gap-5 overflow-y-auto">
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
            <Progress value={taskStatus.current} max={taskStatus.total || numGraphs} label="Graphs generated" />
            {taskStatus.output_dir && <p className="text-xs text-gray-500 font-mono">{taskStatus.output_dir}</p>}
            {taskStatus.error && <p className="text-xs text-red-400">{taskStatus.error}</p>}
          </PagePanel>
        )}

        {!taskStatus && completedTasks.length === 0 && (
          <div className="flex flex-col items-center justify-center flex-1 gap-3 text-gray-600">
            <Database className="w-12 h-12 opacity-30" />
            <p className="text-sm">Configure and start a generation run</p>
          </div>
        )}

        {completedTasks.length > 0 && (
          <div className="flex flex-col gap-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Recent runs</p>
            {completedTasks.map((task) => (
              <Card key={task.task_id} className="border-white/10">
                <CardContent className="p-3 flex items-center gap-3">
                  <Badge
                    className={
                      task.status === 'completed'
                        ? 'bg-green-500/20 text-green-300 border-green-500/30'
                        : 'bg-red-500/20 text-red-300 border-red-500/30'
                    }
                  >
                    {task.status}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-300 font-mono truncate">{task.output_dir ?? task.task_id}</p>
                    <p className="text-xs text-gray-500">{task.current} / {task.total} graphs</p>
                  </div>
                  {task.status === 'completed' && task.output_dir && (
                    <Button variant="ghost" size="sm" title="Dataset generated">
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
