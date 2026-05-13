# win-auto/backend/routes/generate.py
import uuid
from fastapi import APIRouter, HTTPException
from routes.schemas import GenerateRequest, RefineRequest
from services.llm_service import LLMService
from services.code_generator import generate_code
from services.code_validator import validate_code

router = APIRouter(prefix="/api/generate", tags=["generate"])
llm_service = LLMService()

@router.post("")
def generate_plan(body: GenerateRequest):
    try:
        plan = llm_service.generate_plan(body.prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")
    eid = str(uuid.uuid4())
    code = generate_code(plan, eid, "data/screenshots")
    validation = validate_code(code)
    return {"plan": plan, "generated_code": code, "validation": {"is_valid": validation.is_valid, "error": validation.error}}

@router.post("/refine")
def refine_plan(body: RefineRequest):
    try:
        plan = llm_service.refine_plan(
            prompt=body.prompt, current_plan=body.current_plan,
            failure=body.failure, annotations=body.annotations,
            screenshot_base64=body.screenshot_base64,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")
    eid = str(uuid.uuid4())
    code = generate_code(plan, eid, "data/screenshots")
    validation = validate_code(code)
    return {"plan": plan, "generated_code": code, "validation": {"is_valid": validation.is_valid, "error": validation.error}}
