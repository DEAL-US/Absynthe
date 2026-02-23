import { Moon, Sun } from 'lucide-react'
import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/Button'

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/':             { title: 'Dashboard',          subtitle: 'Overview of your Absynthe workspace' },
  '/graph':        { title: 'Graph Builder',       subtitle: 'Generate composite graphs from motifs' },
  '/labels':       { title: 'Label Inspector',     subtitle: 'Assign and visualise ground-truth labels' },
  '/perturbation': { title: 'Perturbation Lab',    subtitle: 'Apply structural perturbations and observe label changes' },
  '/dataset':      { title: 'Dataset Studio',      subtitle: 'Batch-generate and manage benchmark datasets' },
}

export function Header() {
  const { pathname } = useLocation()
  const info = PAGE_TITLES[pathname] ?? { title: 'Absynthe', subtitle: '' }
  const [dark, setDark] = useState(true)

  const toggleDark = () => {
    setDark((d) => {
      const next = !d
      document.documentElement.classList.toggle('dark', next)
      return next
    })
  }

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-gray-900/40 backdrop-blur-sm shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-gray-100">{info.title}</h1>
        <p className="text-xs text-gray-500 mt-0.5">{info.subtitle}</p>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={toggleDark} title="Toggle dark mode">
          {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>
      </div>
    </header>
  )
}
