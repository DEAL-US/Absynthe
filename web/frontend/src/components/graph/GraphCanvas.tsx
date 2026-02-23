import CytoscapeComponent from 'react-cytoscapejs'
import type { Core, Stylesheet } from 'cytoscape'
import { useRef, useCallback, useMemo, useState } from 'react'
import {
  Maximize2, RefreshCw, ZoomIn, ZoomOut, Download,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { BASE_STYLESHEET, LAYOUTS, type LayoutName } from '@/lib/cytoscape-utils'
import { getLabelColor } from '@/lib/color-map'
import type { CytoscapeElement } from '@/api/types'

interface GraphCanvasProps {
  elements: CytoscapeElement[]
  /** Extra per-label Cytoscape stylesheet entries */
  labelStylesheet?: Stylesheet[]
  /** Called when user clicks a node */
  onNodeClick?: (nodeId: string, data: Record<string, unknown>) => void
  onCyInit?: (cy: Core) => void
  className?: string
  /** Show the toolbar */
  toolbar?: boolean
  /** Override layout name */
  defaultLayout?: LayoutName
  /** Extra element classes to merge onto existing elements */
  extraClasses?: Record<string, string>
}

/** Build dynamic label-colour stylesheet entries from the elements. */
function buildLabelStyles(elements: CytoscapeElement[]): Stylesheet[] {
  const labels = new Set<string>()
  for (const el of elements) {
    if (el.group === 'nodes') {
      const lbl = (el.data.label as string) || (el.data.expected_ground_truth as string) || ''
      if (lbl) labels.add(lbl)
    }
  }
  return Array.from(labels).map((label) => {
    const c = getLabelColor(label)
    return {
      selector: `node[label = "${label}"], node[expected_ground_truth = "${label}"]`,
      style: { 'background-color': c.bg, 'border-color': c.border },
    } as Stylesheet
  })
}

const LAYOUT_OPTIONS = Object.keys(LAYOUTS).map((k) => ({ value: k, label: k }))

export function GraphCanvas({
  elements,
  labelStylesheet,
  onNodeClick,
  onCyInit,
  className = '',
  toolbar = true,
  defaultLayout = 'cose-bilkent',
  extraClasses,
}: GraphCanvasProps) {
  const cyRef = useRef<Core | null>(null)
  const [layout, setLayout] = useState<LayoutName>(defaultLayout)

  // Stable key that changes when the element set changes, forcing a full re-mount + layout
  const elementsKey = useMemo(() => {
    const nodeIds = elements
      .filter((e) => e.group === 'nodes')
      .map((e) => e.data.id)
      .sort()
      .join(',')
    return nodeIds
  }, [elements])

  // Merge extra classes into the elements array
  const mergedElements = extraClasses
    ? elements.map((el) => {
        if (el.group === 'nodes') {
          const extra = extraClasses[el.data.id] ?? ''
          if (extra) return { ...el, classes: [el.classes ?? '', extra].filter(Boolean).join(' ') }
        }
        return el
      })
    : elements

  const stylesheet: Stylesheet[] = [
    ...BASE_STYLESHEET,
    ...buildLabelStyles(elements),
    ...(labelStylesheet ?? []),
  ]

  const handleCy = useCallback(
    (cy: Core) => {
      cyRef.current = cy
      onCyInit?.(cy)

      cy.on('tap', 'node', (evt) => {
        const node = evt.target
        onNodeClick?.(node.id(), node.data() as Record<string, unknown>)
      })
    },
    [onNodeClick, onCyInit],
  )

  const applyLayout = (name: LayoutName) => {
    setLayout(name)
    cyRef.current?.layout(LAYOUTS[name] as never).run()
  }

  const fitView = () => cyRef.current?.fit(undefined, 24)
  const zoomIn = () => cyRef.current?.zoom((cyRef.current.zoom() ?? 1) * 1.25)
  const zoomOut = () => cyRef.current?.zoom((cyRef.current.zoom() ?? 1) * 0.8)

  const exportPng = () => {
    if (!cyRef.current) return
    const png = cyRef.current.png({ bg: '#0f172a', scale: 2 })
    const a = document.createElement('a')
    a.href = png
    a.download = 'graph.png'
    a.click()
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {toolbar && (
        <div className="flex items-center gap-2 px-3 py-2 border-b border-white/10 bg-gray-900/60 rounded-t-xl">
          <Select
            value={layout}
            onValueChange={(v) => applyLayout(v as LayoutName)}
            options={LAYOUT_OPTIONS}
            className="w-44"
          />
          <div className="flex items-center gap-1 ml-auto">
            <Button variant="ghost" size="icon" onClick={zoomIn} title="Zoom in">
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={zoomOut} title="Zoom out">
              <ZoomOut className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={fitView} title="Fit view">
              <Maximize2 className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => applyLayout(layout)}
              title="Re-run layout"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={exportPng} title="Export PNG">
              <Download className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      <div className="flex-1 min-h-0 rounded-b-xl overflow-hidden bg-gray-950/80">
        {elements.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-600 text-sm select-none">
            No graph loaded
          </div>
        ) : (
          <CytoscapeComponent
            key={elementsKey}
            elements={mergedElements as never}
            stylesheet={stylesheet}
            layout={LAYOUTS[layout] as never}
            style={{ width: '100%', height: '100%' }}
            cy={handleCy}
          />
        )}
      </div>
    </div>
  )
}
