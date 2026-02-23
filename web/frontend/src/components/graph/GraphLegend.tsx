import { Badge } from '@/components/ui/Badge'
import { getLabelColor } from '@/lib/color-map'

interface GraphLegendProps {
  counts: Record<string, number>
  title?: string
}

export function GraphLegend({ counts, title = 'Label distribution' }: GraphLegendProps) {
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1])
  const total = sorted.reduce((s, [, v]) => s + v, 0)

  if (sorted.length === 0) return null

  return (
    <div className="flex flex-col gap-2.5">
      {title && <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">{title}</p>}
      <div className="flex flex-col gap-1.5">
        {sorted.map(([label, count]) => {
          const color = getLabelColor(label)
          const pct = total > 0 ? Math.round((count / total) * 100) : 0
          return (
            <div key={label} className="flex items-center gap-2">
              <Badge variant="dot" color={color.text}>
                {label}
              </Badge>
              <div className="flex-1 h-1 rounded-full bg-white/10 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: color.bg }}
                />
              </div>
              <span className="text-xs text-gray-400 font-mono tabular-nums w-8 text-right">
                {count}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
