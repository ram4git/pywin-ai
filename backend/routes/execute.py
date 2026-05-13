# win-auto/backend/routes/execute.py
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Execution, ExecutionStep, ExecutionStatus, StepStatus
from routes.schemas import ExecuteRequest
from services.code_generator import generate_code
from services.code_validator import validate_code
from services.executor_service import executor_service
from config import settings

router = APIRouter(prefix="/api/execute", tags=["execute"])

@router.post("")
def start_execution(body: ExecuteRequest, db: Session = Depends(get_db)):
    if executor_service.is_running:
        raise HTTPException(status_code=409, detail="Another execution is already running")
    execution_id = str(uuid.uuid4())
    code = generate_code(body.plan, execution_id, settings.screenshots_dir)
    validation = validate_code(code)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=f"Validation failed: {validation.error}")

    scripts_dir = Path(settings.scripts_dir)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = scripts_dir / f"{execution_id}.py"
    script_path.write_text(code)

    execution = Execution(id=execution_id, script_id=body.script_id, prompt=body.prompt, plan=body.plan, status=ExecutionStatus.running)
    db.add(execution)
    for s in body.plan:
        db.add(ExecutionStep(execution_id=execution_id, step_number=s["step"], action=s, status=StepStatus.pending))
    db.commit()

    try:
        process = executor_service.start(str(script_path), execution_id)
        execution.pid = process.pid
        db.commit()
    except RuntimeError as e:
        execution.status = ExecutionStatus.failed
        execution.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=409, detail=str(e))
    return {"execution_id": execution_id, "generated_code": code, "status": "running"}

@router.get("/{execution_id}/stream")
async def stream_execution(execution_id: str, db: Session = Depends(get_db)):
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    process = executor_service._current_process
    if not process:
        raise HTTPException(status_code=400, detail="No active process")

    async def event_generator():
        async for data in executor_service.stream_output(process):
            event_type = data.get("type", "step_update")
            yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
            if event_type in ("execution_complete", "execution_failed"):
                st = ExecutionStatus.completed if event_type == "execution_complete" else ExecutionStatus.failed
                execution.status = st
                execution.finished_at = datetime.utcnow()
                if "error" in data:
                    execution.error_message = data["error"]
                db.commit()
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})

@router.post("/{execution_id}/stop")
def stop_execution(execution_id: str, db: Session = Depends(get_db)):
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.status != ExecutionStatus.running:
        raise HTTPException(status_code=400, detail="Not running")
    executor_service.stop()
    execution.status = ExecutionStatus.stopped
    execution.finished_at = datetime.utcnow()
    execution.error_message = "Stopped by user"
    db.commit()
    return {"status": "stopped"}
