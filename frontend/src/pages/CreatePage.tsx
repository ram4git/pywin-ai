import { useState, useCallback, useRef } from 'react'
import { Save, Square, AlertTriangle } from 'lucide-react'
import PromptEditor from '../components/PromptEditor'
import PlanViewer, { type StepState } from '../components/PlanViewer'
import CodeReviewDialog from '../components/CodeReviewDialog'
import RefinementPanel from '../components/RefinementPanel'
import { api } from '../api/client'
import type { PlanStep, PageStatus, GenerateResponse } from '../api/types'

export default function CreatePage() {
  const [status, setStatus] = useState<PageStatus>('idle')
  const [prompt, setPrompt] = useState('')
  const [plan, setPlan] = useState<PlanStep[]>([])
  const [code, setCode] = useState('')
  const [codeValid, setCodeValid] = useState(false)
  const [valError, setValError] = useState<string | null>(null)
  const [steps, setSteps] = useState<Record<number, StepState>>({})
  const [execId, setExecId] = useState<string | null>(null)
  const [failStep, setFailStep] = useState<number | null>(null)
  const [failErr, setFailErr] = useState('')
  const [failShot, setFailShot] = useState<string>()
  const [iter, setIter] = useState(0)
  const [showReview, setShowReview] = useState(false)
  const [showSave, setShowSave] = useState(false)
  const [name, setName] = useState('')
  const cleanupRef = useRef<(() => void) | null>(null)

  const handleGenerate = useCallback(async (p: string) => {
    setPrompt(p); setStatus('generating'); setSteps({}); setFailStep(null)
    try {
      const r: GenerateResponse = await api.generate.plan(p)
      setPlan(r.plan); setCode(r.generated_code); setCodeValid(r.validation.is_valid); setValError(r.validation.error)
      setShowReview(true); setStatus('reviewing')
    } catch (e: unknown) { setStatus('failed'); setFailErr(e instanceof Error ? e.message : 'Failed') }
  }, [])

  const handleRun = useCallback(async () => {
    setShowReview(false); setStatus('running'); setSteps({})
    try {
      const r = await api.execute.start({ plan, prompt })
      setExecId(r.execution_id)
      cleanupRef.current = api.execute.stream(r.execution_id, ev => {
        if (ev.type === 'step_update' && ev.step !== undefined) {
          setSteps(p => ({ ...p, [ev.step!]: { status: (ev.status as StepState['status']) || 'pending', screenshot: ev.screenshot, error: ev.error, elapsedMs: ev.elapsed_ms } }))
          if (ev.status === 'failed') { setFailStep(ev.step!); setFailErr(ev.error || ''); setFailShot(ev.screenshot) }
        } else if (ev.type === 'execution_complete') setStatus('completed')
        else if (ev.type === 'execution_failed') setStatus('failed')
      })
    } catch (e: unknown) { setStatus('failed'); setFailErr(e instanceof Error ? e.message : 'Failed') }
  }, [plan, prompt])

  const handleStop = useCallback(async () => {
    if (execId) { cleanupRef.current?.(); await api.execute.stop(execId); setStatus('stopped') }
  }, [execId])

  const handleRefine = useCallback(async (annotations: string[]) => {
    if (!failStep) return
    setStatus('generating'); setIter(c => c + 1)
    try {
      const r = await api.generate.refine({ prompt, current_plan: plan, failure: { step: failStep, error: failErr }, annotations })
      setPlan(r.plan); setCode(r.generated_code); setCodeValid(r.validation.is_valid); setValError(r.validation.error)
      setShowReview(true); setStatus('reviewing'); setFailStep(null)
    } catch (e: unknown) { setStatus('failed'); setFailErr(e instanceof Error ? e.message : 'Refinement failed') }
  }, [prompt, plan, failStep, failErr])

  const handleSave = useCallback(async () => {
    if (!name.trim()) return
    await api.scripts.create({ name, prompt, plan, generated_code: code })
    setShowSave(false); setName('')
  }, [name, prompt, plan, code])

  return (
    <div className="space-y-4">
      <PromptEditor onGenerate={handleGenerate} isGenerating={status === 'generating'} initialPrompt={prompt} />
      {plan.length > 0 && <PlanViewer plan={plan} stepStates={steps} />}
      {status === 'running' && (
        <div className="flex justify-center">
          <button onClick={handleStop} className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-error text-white text-sm font-semibold hover:bg-red-600 transition-colors">
            <Square size={16} /> Stop
          </button>
        </div>
      )}
      {status === 'completed' && (
        <div className="flex items-center justify-center gap-3">
          <span className="text-sm font-medium text-success">Completed!</span>
          <button onClick={() => setShowSave(true)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-dark transition-colors"><Save size={16} /> Save Script</button>
        </div>
      )}
      {(status === 'failed' || status === 'stopped') && !failStep && failErr && (
        <div className="flex items-start gap-3 p-4 rounded-xl border border-red-500/30 bg-red-500/10">
          <AlertTriangle size={20} className="text-error shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-error">Generation Failed</p>
            <p className="text-sm text-text-secondary mt-1">{failErr}</p>
            <button onClick={() => { setStatus('idle'); setFailErr('') }} className="mt-2 text-xs text-primary hover:underline">Dismiss</button>
          </div>
        </div>
      )}
      {(status === 'failed' || status === 'stopped') && failStep && (
        <RefinementPanel error={failErr} failedStep={failStep} screenshotPath={failShot} prompt={prompt} plan={plan} iterationCount={iter} onRefine={handleRefine} isRefining={status === 'generating'} />
      )}
      {showReview && <CodeReviewDialog code={code} isValid={codeValid} validationError={valError} onApprove={handleRun} onCancel={() => { setShowReview(false); setStatus('idle') }} />}
      {showSave && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-surface rounded-xl border border-border shadow-card-hover p-6 w-full max-w-md">
            <h2 className="text-base font-semibold mb-3">Save Script</h2>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="Script name" autoFocus
              className="w-full px-3 py-2 rounded-lg border border-border text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-primary/30"
              onKeyDown={e => e.key === 'Enter' && handleSave()} />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowSave(false)} className="px-4 py-2 rounded-lg text-sm text-text-secondary hover:bg-surface-secondary transition">Cancel</button>
              <button onClick={handleSave} disabled={!name.trim()} className="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-50 transition-colors">Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
