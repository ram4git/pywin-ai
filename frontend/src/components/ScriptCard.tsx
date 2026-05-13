import { Play, RefreshCw, Edit3, Trash2 } from 'lucide-react'
import type { Script } from '../api/types'

interface Props { script: Script; onRun: (s: Script) => void; onRegenerate: (s: Script) => void; onEdit: (s: Script) => void; onDelete: (s: Script) => void }

function timeAgo(d: string | null): string {
  if (!d) return 'Never run'
  const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  return days < 7 ? `${days}d ago` : `${Math.floor(days / 7)}w ago`
}

export default function ScriptCard({ script, onRun, onRegenerate, onEdit, onDelete }: Props) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4 shadow-card hover:shadow-card-hover transition-shadow group">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-sm font-semibold text-text-primary truncate pr-2">{script.name}</h3>
        <div className={`w-2.5 h-2.5 rounded-full shrink-0 mt-1 ${script.last_successful_run ? 'bg-success' : 'bg-text-muted'}`} />
      </div>
      <p className="text-xs text-text-muted line-clamp-2 mb-3">{script.prompt}</p>
      <div className="flex items-center gap-3 text-xs text-text-muted mb-3">
        <span>{script.plan?.length ?? 0} steps</span>
        <span>Last: {timeAgo(script.last_successful_run)}</span>
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button onClick={() => onRun(script)} className="flex items-center gap-1 px-2.5 py-1.5 rounded-md bg-primary text-white text-xs font-medium hover:bg-primary-dark transition"><Play size={12} /> Run</button>
        <button onClick={() => onRegenerate(script)} className="flex items-center gap-1 px-2.5 py-1.5 rounded-md bg-surface-secondary text-text-secondary text-xs font-medium hover:bg-border-light transition"><RefreshCw size={12} /> Re-gen</button>
        <button onClick={() => onEdit(script)} className="p-1.5 rounded-md text-text-muted hover:text-primary hover:bg-surface-secondary transition"><Edit3 size={14} /></button>
        <button onClick={() => onDelete(script)} className="p-1.5 rounded-md text-text-muted hover:text-error hover:bg-red-50 transition"><Trash2 size={14} /></button>
      </div>
    </div>
  )
}
