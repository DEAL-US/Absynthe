import * as ProgressPrimitive from '@radix-ui/react-progress'
import * as React from 'react'
import { cn } from '@/lib/utils'

interface ProgressProps {
  value: number
  max?: number
  className?: string
  label?: string
}

export function Progress({ value, max = 100, className, label }: ProgressProps) {
  const pct = Math.min(100, Math.round((value / max) * 100))
  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {label && (
        <div className="flex justify-between text-xs text-gray-400">
          <span>{label}</span>
          <span className="font-mono tabular-nums">{value} / {max}</span>
        </div>
      )}
      <ProgressPrimitive.Root
        className="relative h-2 w-full overflow-hidden rounded-full bg-white/10"
        value={pct}
      >
        <ProgressPrimitive.Indicator
          className="h-full bg-gradient-to-r from-brand-600 to-brand-400 transition-all duration-300 ease-out"
          style={{ transform: `translateX(-${100 - pct}%)` }}
        />
      </ProgressPrimitive.Root>
    </div>
  )
}
