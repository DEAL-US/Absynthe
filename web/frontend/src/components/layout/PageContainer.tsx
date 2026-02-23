import * as React from 'react'
import { cn } from '@/lib/utils'

interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Two-column mode splits the content area 50/50 */
  split?: boolean
}

export function PageContainer({ className, children, split, ...props }: PageContainerProps) {
  return (
    <div
      className={cn(
        'h-full p-6',
        split ? 'flex gap-5 overflow-hidden' : 'flex flex-col gap-5 overflow-auto',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function PagePanel({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'flex flex-col gap-4 rounded-2xl border border-white/10 bg-gray-900/50 p-5',
        className,
      )}
      {...props}
    />
  )
}
