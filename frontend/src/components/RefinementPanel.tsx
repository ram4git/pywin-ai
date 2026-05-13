import { useState } from 'react'
import { RefreshCw, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'

interface Props {
  error: string; failedStep: number; screenshotPath?: string;
  prompt: string; plan: unknown[]; iterationCount: number;
  onRefine: (annotations: string[]) => void; isRefining: boolean;
}

export default function RefinementPanel({ error, failedStep, screenshotPath, prompt, plan, iterationCount, onRefine, isRefining }: Props) {
  const [note, setNote] = useState('')
  const [notes, setNotes] = useState<string[]>([])
  const [showCtx, setShowCtx] = useState(false)
  const addNote = () => { if (note.trim()) { setNotes(p => [...p, note.trim()]); setNote('') } }
  return (
    <div className="bg-surface rounded-xl border border-error/30 p-5 shadow-card">
      <div className="flex items-center gap-2 mb-3"><AlertTriangle size={18} className="text-error" /><h3 className="text-sm font-semibold text-error">Step #{failedStep} Failed</h3></div>
      <p className="text-sm text-text-secondary bg-red-50 rounded-lg p-3 mb-4 font-mono">{error}</p>
      {screenshotPath && <img src={screenshotPath} alt={`Failure at step ${failedStep}`} className="w-full rounded-lg border border-border mb-4" />}
      <div className="mb-4">
        <label htmlFor="annotation" className="block text-sm font-medium text-text-primary mb-1">Your notes (help the AI fix this)</label>
        <div className="flex gap-2">
          <input id="annotation" value={note} onChange={e => setNote(e.target.value)} onKeyDown={e => e.key === 'Enter' && addNote()}
            placeholder="e.g., The button is in a different tab..." className="flex-1 px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" />
          <button onClick={addNote} className="px-3 py-2 rounded-lg bg-surface-secondary text-sm font-medium hover:bg-border-light transition">Add</button>
        </div>
        {notes.length > 0 && <ul className="mt-2 space-y-1">{notes.map((n, i) => <li key={i} className="text-xs text-text-secondary bg-surface-secondary rounded px-2 py-1">{n}</li>)}</ul>}
      </div>
      <button onClick={() => setShowCtx(!showCtx)} className="flex items-center gap-1 text-xs text-text-muted hover:text-primary mb-3 transition">
        {showCtx ? <ChevronUp size={14} /> : <ChevronDown size={14} />} View context being sent to AI
      </button>
      {showCtx && <pre className="bg-gray-900 text-gray-100 rounded-lg p-3 text-xs overflow-auto max-h-48 mb-4 font-mono">{JSON.stringify({ prompt, plan_steps: plan.length, failure: { step: failedStep, error }, notes }, null, 2)}</pre>}
      {iterationCount >= 5 && <p className="text-xs text-warning mb-3">Refined {iterationCount} times. Consider starting fresh.</p>}
      <button onClick={() => onRefine(notes)} disabled={isRefining}
        className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-50 transition-colors">
        <RefreshCw size={16} className={isRefining ? 'animate-spin' : ''} /> {isRefining ? 'Re-generating...' : 'Re-generate Plan'}
      </button>
    </div>
  )
}
