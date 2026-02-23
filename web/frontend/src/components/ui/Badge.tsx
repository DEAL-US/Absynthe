import * as React from 'react'
import { cn } from '@/lib/utils'

type BadgeVariant = 'default' | 'outline' | 'dot'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  color?: string // hex colour
}

export function Badge({ className, variant = 'default', color, children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium',
        variant === 'default' && 'bg-brand-600/30 text-brand-300 border border-brand-500/30',
        variant === 'outline' && 'border border-white/20 text-gray-300',
        variant === 'dot' && 'bg-transparent text-gray-300',
        className,
      )}
      style={color ? { backgroundColor: `${color}22`, color, borderColor: `${color}44`, border: '1px solid' } : undefined}
      {...props}
    >
      {variant === 'dot' && (
        <span
          className="inline-block w-1.5 h-1.5 rounded-full"
          style={color ? { backgroundColor: color } : { backgroundColor: 'currentColor' }}
        />
      )}
      {children}
    </span>
  )
}
