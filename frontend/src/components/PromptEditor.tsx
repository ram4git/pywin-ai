import { useState } from 'react'
import { Wand2, Loader2 } from 'lucide-react'

interface Props { onGenerate: (prompt: string) => void; isGenerating: boolean; initialPrompt?: string }

export default function PromptEditor({ onGenerate, isGenerating, initialPrompt = '' }: Props) {
  const [prompt, setPrompt] = useState(initialPrompt)
  const submit = () => { if (prompt.trim() && !isGenerating) onGenerate(prompt.trim()) }
  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <label htmlFor="prompt" className="block text-sm font-semibold text-text-primary mb-2">Describe your automation</label>
      <textarea id="prompt" value={prompt} onChange={e => setPrompt(e.target.value)}
        placeholder="Open SSMS, run a query on SalesDB, copy the results to Excel, create a chart, and email it via Outlook..."
        className="w-full h-32 px-4 py-3 rounded-lg border border-border bg-surface-secondary text-text-primary placeholder:text-text-muted text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition"
        onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) submit() }} />
      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-text-muted">Ctrl+Enter to generate</span>
        <button onClick={submit} disabled={!prompt.trim() || isGenerating}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {isGenerating ? <><Loader2 size={16} className="animate-spin" /> Generating...</> : <><Wand2 size={16} /> Generate Plan</>}
        </button>
      </div>
    </div>
  )
}
