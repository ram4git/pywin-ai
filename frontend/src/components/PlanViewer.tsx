import { CheckCircle2, Circle, Loader2, XCircle, Clock } from 'lucide-react'
import type { PlanStep } from '../api/types'

export interface StepState { status: 'pending' | 'running' | 'done' | 'failed'; screenshot?: string; error?: string; elapsedMs?: number }
interface Props { plan: PlanStep[]; stepStates: Record<number, StepState>; onScreenshotClick?: (path: string) => void }

const icon = (s: StepState['status']) => {
  if (s === 'done') return <CheckCircle2 size={18} className="text-success" />
  if (s === 'running') return <Loader2 size={18} className="text-primary animate-spin" />
  if (s === 'failed') return <XCircle size={18} className="text-error" />
  return <Circle size={18} className="text-text-muted" />
}

export default function PlanViewer({ plan, stepStates, onScreenshotClick }: Props) {
  if (!plan.length) return null
  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-primary mb-3">Automation Plan ({plan.length} steps)</h3>
      <div className="space-y-2">
        {plan.map(step => {
          const st = stepStates[step.step] || { status: 'pending' }
          return (
            <div key={step.step} className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
              st.status === 'running' ? 'border-primary/30 bg-primary-light/30' :
              st.status === 'failed' ? 'border-error/30 bg-red-50' : 'border-border-light bg-surface-secondary/50'}`}>
              <div className="mt-0.5">{icon(st.status)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono text-text-muted">#{step.step}</span>
                  <span className="text-sm font-medium text-text-primary">{step.description}</span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-surface-secondary text-text-muted font-mono">{step.action}</span>
                  {step.backend === 'win32' && <span className="text-xs px-1.5 py-0.5 rounded bg-warning/10 text-warning font-mono">win32</span>}
                </div>
                {st.status === 'running' && st.elapsedMs !== undefined && (
                  <div className="flex items-center gap-1 mt-1 text-xs text-primary"><Clock size={12} />Running... {st.elapsedMs < 1000 ? `${st.elapsedMs}ms` : `${(st.elapsedMs / 1000).toFixed(1)}s`}</div>
                )}
                {st.error && <p className="text-xs text-error mt-1">{st.error}</p>}
              </div>
              {st.screenshot && (
                <button onClick={() => onScreenshotClick?.(st.screenshot!)}
                  className="shrink-0 w-16 h-10 rounded border border-border overflow-hidden hover:ring-2 hover:ring-primary/30 transition">
                  <img src={st.screenshot} alt={`Step ${step.step}`} className="w-full h-full object-cover" />
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
