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

type NodePosition = { x: number; y: number }

interface GraphCanvasProps {
  elements: CytoscapeElement[]
  labelStylesheet?: Stylesheet[]
  onNodeClick?: (nodeId: string, data: Record<string, unknown>) => void
  onCyInit?: (cy: Core) => void
  className?: string
  toolbar?: boolean
  defaultLayout?: LayoutName
  extraClasses?: Record<string, string>
  fixedPositions?: Record<string, NodePosition>
  adjustNewNodes?: boolean
  onPositionsReady?: (positions: Record<string, NodePosition>) => void
}

function buildLabelStyles(elements: CytoscapeElement[]): Stylesheet[] {
  const labels = new Set<string>()
  for (const el of elements) {
    if (el.group === 'nodes') {
      const lbl =
        (el.data.label as string) ||
        (el.data.observed_ground_truth as string) ||
        ''
      if (lbl) labels.add(lbl)
    }
  }
  return Array.from(labels).map((label) => {
    const c = getLabelColor(label)
    return {
      selector: `node[label = "${label}"], node[observed_ground_truth = "${label}"]`,
      style: { 'background-color': c.bg, 'border-color': c.border },
    } as Stylesheet
  })
}

function collectNodePositions(cy: Core): Record<string, NodePosition> {
  const positions: Record<string, NodePosition> = {}
  cy.nodes().forEach((node) => {
    const pos = node.position()
    positions[node.id()] = { x: pos.x, y: pos.y }
  })
  return positions
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
  fixedPositions,
  adjustNewNodes = false,
  onPositionsReady,
}: GraphCanvasProps) {
  const cyRef = useRef<Core | null>(null)
  const [layout, setLayout] = useState<LayoutName>(defaultLayout)

  const elementsKey = useMemo(() => {
    const nodeIds = elements
      .filter((e) => e.group === 'nodes')
      .map((e) => e.data.id)
      .sort()
      .join(',')
    const fixedCount = fixedPositions ? Object.keys(fixedPositions).length : 0
    return `${nodeIds}|${fixedCount}|${adjustNewNodes ? 'adj' : 'static'}`
  }, [elements, fixedPositions, adjustNewNodes])

  const mergedElements: CytoscapeElement[] = elements.map((el) => {
    let next = el
    if (extraClasses && el.group === 'nodes') {
      const extra = extraClasses[el.data.id] ?? ''
      if (extra) {
        next = { ...next, classes: [next.classes ?? '', extra].filter(Boolean).join(' ') }
      }
    }
    if (fixedPositions && next.group === 'nodes') {
      const pos = fixedPositions[next.data.id]
      if (pos) {
        next = { ...next, position: pos }
      }
    }
    return next
  })

  const stylesheet: Stylesheet[] = [
    ...BASE_STYLESHEET,
    ...buildLabelStyles(elements),
    ...(labelStylesheet ?? []),
  ]

  const effectiveLayout = fixedPositions
    ? ({ name: 'preset', fit: false, padding: 24, animate: false } as const)
    : LAYOUTS[layout]

  const handleCy = useCallback(
    (cy: Core) => {
      cyRef.current = cy
      onCyInit?.(cy)

      cy.on('tap', 'node', (evt) => {
        const node = evt.target
        onNodeClick?.(node.id(), node.data() as Record<string, unknown>)
      })

      let published = false
      const publish = () => {
        if (published) return
        published = true
        onPositionsReady?.(collectNodePositions(cy))
      }

      if (fixedPositions && adjustNewNodes) {
        const lockedIds: string[] = []
        cy.nodes().forEach((node) => {
          if (fixedPositions[node.id()]) {
            node.lock()
            lockedIds.push(node.id())
          }
        })

        const hasNewNodes = cy.nodes().toArray().some((node) => !fixedPositions[node.id()])
        if (hasNewNodes) {
          const layoutOptions = {
            ...LAYOUTS[defaultLayout],
            fit: false,
            padding: 24,
            animate: false,
            randomize: false,
          }
          const relayout = cy.layout(layoutOptions as never)
          relayout.on('layoutstop', () => {
            lockedIds.forEach((id) => cy.$id(id).unlock())
            publish()
          })
          relayout.run()
          // Fallback in case the layout event is missed by the wrapper lifecycle.
          setTimeout(() => {
            lockedIds.forEach((id) => cy.$id(id).unlock())
            publish()
          }, 300)
        } else {
          lockedIds.forEach((id) => cy.$id(id).unlock())
          publish()
        }
      } else {
        cy.one('layoutstop', publish)
        // Fallback for initial layout race: sometimes layoutstop happens before listener binding.
        setTimeout(publish, 300)
      }
    },
    [onCyInit, onNodeClick, onPositionsReady, fixedPositions, adjustNewNodes, defaultLayout],
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
            layout={effectiveLayout as never}
            style={{ width: '100%', height: '100%' }}
            cy={handleCy}
          />
        )}
      </div>
    </div>
  )
}
