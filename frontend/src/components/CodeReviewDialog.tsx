import { useState } from 'react'
import { ShieldCheck, ShieldAlert, X, Play } from 'lucide-react'

interface Props { code: string; isValid: boolean; validationError: string | null; onApprove: () => void; onCancel: () => void }

export default function CodeReviewDialog({ code, isValid, validationError, onApprove, onCancel }: Props) {
  const [expanded, setExpanded] = useState(true)
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-surface rounded-2xl border border-border shadow-card-hover w-full max-w-2xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div className="flex items-center gap-2">
            {isValid ? <ShieldCheck size={20} className="text-success" /> : <ShieldAlert size={20} className="text-error" />}
            <h2 className="text-base font-semibold text-text-primary">Review Generated Code</h2>
          </div>
          <button onClick={onCancel} className="text-text-muted hover:text-text-primary transition"><X size={20} /></button>
        </div>
        <div className="flex-1 overflow-auto p-5 space-y-4">
          {!isValid && validationError && <div className="p-3 rounded-lg bg-red-50 border border-error/30 text-sm text-error"><strong>Validation failed:</strong> {validationError}</div>}
          {isValid && <div className="p-3 rounded-lg bg-green-50 border border-success/30 text-sm text-success">Code passed security validation.</div>}
          <button onClick={() => setExpanded(!expanded)} className="text-sm font-medium text-primary hover:underline">{expanded ? 'Collapse' : 'Expand'} code</button>
          {expanded && <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 text-xs overflow-auto max-h-96 font-mono leading-relaxed">{code}</pre>}
        </div>
        <div className="flex items-center justify-end gap-3 px-5 py-4 border-t border-border">
          <button onClick={onCancel} className="px-4 py-2 rounded-lg text-sm font-medium text-text-secondary hover:bg-surface-secondary transition">Cancel</button>
          <button onClick={onApprove} disabled={!isValid}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <Play size={16} /> Approve & Run
          </button>
        </div>
      </div>
    </div>
  )
}
