import { useState, useEffect } from 'react'
import { Search, FolderOpen } from 'lucide-react'
import ScriptCard from '../components/ScriptCard'
import { api } from '../api/client'
import type { Script } from '../api/types'

export default function LibraryPage() {
  const [scripts, setScripts] = useState<Script[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadScripts() }, [])
  const loadScripts = async () => { setLoading(true); try { setScripts(await api.scripts.list()) } finally { setLoading(false) } }

  const filtered = scripts.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.prompt.toLowerCase().includes(search.toLowerCase()))

  const handleRun = async (s: Script) => { if (s.plan) { try { await api.execute.start({ plan: s.plan, prompt: s.prompt, script_id: s.id }) } catch (e) { console.error(e) } } }
  const handleRegenerate = async (s: Script) => { try { const r = await api.generate.plan(s.prompt); await api.scripts.update(s.id, { plan: r.plan, generated_code: r.generated_code }); loadScripts() } catch (e) { console.error(e) } }
  const handleDelete = async (s: Script) => { if (!confirm(`Delete "${s.name}"?`)) return; await api.scripts.remove(s.id); setScripts(p => p.filter(x => x.id !== s.id)) }

  if (loading) return <div className="text-center text-text-muted py-12">Loading...</div>
  return (
    <div className="space-y-4">
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search saved scripts..."
          className="w-full pl-9 pr-4 py-2.5 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 bg-surface" />
      </div>
      {filtered.length === 0 ? (
        <div className="text-center py-16"><FolderOpen size={40} className="mx-auto text-text-muted mb-3" />
          <p className="text-sm text-text-muted">{scripts.length === 0 ? 'No saved scripts yet.' : 'No match.'}</p></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(s => <ScriptCard key={s.id} script={s} onRun={handleRun} onRegenerate={handleRegenerate} onEdit={() => {}} onDelete={handleDelete} />)}
        </div>
      )}
    </div>
  )
}
