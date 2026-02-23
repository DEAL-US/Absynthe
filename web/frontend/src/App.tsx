import { useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { DashboardPage } from '@/modules/dashboard/DashboardPage'
import { GraphBuilderPage } from '@/modules/graph-builder/GraphBuilderPage'
import { LabelInspectorPage } from '@/modules/label-inspector/LabelInspectorPage'
import { PerturbationLabPage } from '@/modules/perturbation-lab/PerturbationLabPage'
import { DatasetStudioPage } from '@/modules/dataset-studio/DatasetStudioPage'

type Theme = 'dark' | 'light'

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'dark'
  const stored = window.localStorage.getItem('absynthe-theme')
  return stored === 'light' ? 'light' : 'dark'
}

export default function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    root.classList.toggle('light', theme === 'light')
    window.localStorage.setItem('absynthe-theme', theme)
  }, [theme])

  return (
    <div className={`flex h-screen overflow-hidden bg-gray-950 app-theme-${theme}`}>
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header
          theme={theme}
          onToggleTheme={() => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))}
        />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/graph" element={<GraphBuilderPage />} />
            <Route path="/labels" element={<LabelInspectorPage />} />
            <Route path="/perturbation" element={<PerturbationLabPage />} />
            <Route path="/dataset" element={<DatasetStudioPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
