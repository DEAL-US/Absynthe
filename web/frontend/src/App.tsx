import { Route, Routes } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { DashboardPage } from '@/modules/dashboard/DashboardPage'
import { GraphBuilderPage } from '@/modules/graph-builder/GraphBuilderPage'
import { LabelInspectorPage } from '@/modules/label-inspector/LabelInspectorPage'
import { PerturbationLabPage } from '@/modules/perturbation-lab/PerturbationLabPage'
import { DatasetStudioPage } from '@/modules/dataset-studio/DatasetStudioPage'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
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
