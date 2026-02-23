import { X } from 'lucide-react'
import { getLabelColor } from '@/lib/color-map'

interface GraphInfoPanelProps {
  nodeId: string
  data: Record<string, unknown>
  onClose: () => void
}

const SHOW_ATTRS = [
  'label',
  'motif',
  'motif_id',
  'expected_ground_truth',
  'observed_ground_truth',
]

export function GraphInfoPanel({ nodeId, data, onClose }: GraphInfoPanelProps) {
  const label = (data.label as string) || 'unknown'
  const color = getLabelColor(label)

  return (
    <div className="absolute bottom-4 right-4 z-10 w-60 rounded-xl border border-white/15 bg-gray-900/95 backdrop-blur-sm shadow-2xl p-4 animate-fade-in">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color.bg }} />
          <span className="text-sm font-semibold text-gray-100">Node {nodeId}</span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-300 transition-colors"
          aria-label="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex flex-col gap-1.5">
        {SHOW_ATTRS.filter((k) => data[k] !== undefined && data[k] !== '').map((k) => (
          <div key={k} className="flex items-start justify-between gap-2">
            <span className="text-xs text-gray-500 shrink-0">{k.replace(/_/g, ' ')}</span>
            <span className="text-xs text-gray-200 text-right break-all font-mono">
              {String(data[k])}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
