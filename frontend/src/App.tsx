import { useState } from 'react'
import { Wand2, Library } from 'lucide-react'
import CreatePage from './pages/CreatePage'
import LibraryPage from './pages/LibraryPage'

const TABS = [
  { id: 'create' as const, label: 'Create', icon: Wand2 },
  { id: 'library' as const, label: 'Library', icon: Library },
]

export default function App() {
  const [activeTab, setActiveTab] = useState<'create' | 'library'>('create')
  return (
    <div className="min-h-screen bg-background text-text-primary font-sans">
      <header className="border-b border-border bg-surface px-6 py-3 flex items-center gap-6">
        <h1 className="text-lg font-bold text-primary tracking-tight">Win-Auto</h1>
        <nav className="flex gap-1">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id ? 'bg-primary text-white' : 'text-text-secondary hover:bg-surface-secondary'}`}>
              <tab.icon size={16} />{tab.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="p-6 max-w-5xl mx-auto overflow-auto" style={{ height: 'calc(100vh - 57px)' }}>
        {activeTab === 'create' && <CreatePage />}
        {activeTab === 'library' && <LibraryPage />}
      </main>
    </div>
  )
}
