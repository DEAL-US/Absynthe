import { NavLink } from 'react-router-dom'
import { BarChart3, Database, FlaskConical, LayoutDashboard, Network, Tag } from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/',             icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/graph',        icon: Network,         label: 'Graph Builder' },
  { to: '/labels',       icon: Tag,             label: 'Label Inspector' },
  { to: '/perturbation', icon: FlaskConical,    label: 'Perturbation Lab' },
  { to: '/dataset',      icon: Database,        label: 'Dataset Studio' },
]

export function Sidebar() {
  return (
    <aside className="flex flex-col w-[220px] shrink-0 border-r border-gray-200 dark:border-white/10 bg-white dark:bg-gray-900/60 backdrop-blur-sm">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-gray-200 dark:border-white/10">
        <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-brand-600 shadow-lg shadow-brand-900/60">
          <BarChart3 className="w-4 h-4 text-white" />
        </div>
        <span className="text-sm font-semibold tracking-tight text-gray-900 dark:text-gray-100">
          Graphtender
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        <p className="px-2 mb-2 text-[10px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-600">
          Pipeline
        </p>
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-brand-600/15 dark:bg-brand-600/20 text-brand-700 dark:text-brand-300 border border-brand-500/30'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-white/8',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  className={cn(
                    'w-4 h-4 shrink-0 transition-colors',
                    isActive ? 'text-brand-600 dark:text-brand-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300',
                  )}
                />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-gray-200 dark:border-white/10">
        <p className="text-[10px] text-gray-400 dark:text-gray-600">Synthetic Graph Dataset Generator</p>
      </div>
    </aside>
  )
}
