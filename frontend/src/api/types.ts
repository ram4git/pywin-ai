export interface PlanStep {
  step: number; action: string; target: string; description: string;
  params: Record<string, unknown>; backend: 'uia' | 'win32';
}
export interface Script {
  id: string; name: string; prompt: string; plan: PlanStep[] | null;
  generated_code: string | null; last_successful_run: string | null;
  created_at: string; updated_at: string;
}
export interface GenerateResponse {
  plan: PlanStep[]; generated_code: string;
  validation: { is_valid: boolean; error: string | null };
}
export interface ExecuteResponse { execution_id: string; generated_code: string; status: string; }
export interface ExecutionEvent {
  type: 'step_update' | 'execution_complete' | 'execution_failed' | 'heartbeat';
  step?: number; status?: string; error?: string; screenshot?: string;
  elapsed_ms?: number; [key: string]: unknown;
}
export type PageStatus = 'idle' | 'generating' | 'reviewing' | 'running' | 'completed' | 'failed' | 'stopped'
