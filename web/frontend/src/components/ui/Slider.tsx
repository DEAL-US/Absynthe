import * as SliderPrimitive from '@radix-ui/react-slider'
import * as React from 'react'
import { cn } from '@/lib/utils'

interface SliderProps {
  label?: string
  value: number
  min?: number
  max?: number
  step?: number
  onValueChange: (v: number) => void
  className?: string
}

export function Slider({ label, value, min = 0, max = 100, step = 1, onValueChange, className }: SliderProps) {
  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-gray-400">{label}</label>
          <span className="text-xs font-mono text-gray-300 tabular-nums">{value}</span>
        </div>
      )}
      <SliderPrimitive.Root
        className="relative flex w-full touch-none select-none items-center cursor-pointer"
        min={min}
        max={max}
        step={step}
        value={[value]}
        onValueChange={([v]) => onValueChange(v)}
      >
        <SliderPrimitive.Track className="relative h-1.5 w-full grow overflow-hidden rounded-full bg-white/15">
          <SliderPrimitive.Range className="absolute h-full bg-brand-500" />
        </SliderPrimitive.Track>
        <SliderPrimitive.Thumb
          className={cn(
            'block h-4 w-4 rounded-full border-2 border-brand-500 bg-gray-950',
            'ring-offset-gray-950 transition-colors focus-visible:outline-none',
            'focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2',
            'disabled:pointer-events-none disabled:opacity-50',
          )}
        />
      </SliderPrimitive.Root>
    </div>
  )
}
