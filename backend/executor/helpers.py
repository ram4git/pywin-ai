# win-auto/backend/executor/helpers.py
import json

def report_step(step: int, status: str, **kwargs):
    print(json.dumps({"type": "step_update", "step": step, "status": status, **kwargs}), flush=True)

def report_complete():
    print(json.dumps({"type": "execution_complete"}), flush=True)

def report_error(step: int, error: str, **kwargs):
    print(json.dumps({"type": "step_update", "step": step, "status": "failed", "error": error, **kwargs}), flush=True)
