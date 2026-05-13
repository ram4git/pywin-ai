# win-auto/backend/routes/schemas.py
from pydantic import BaseModel
from datetime import datetime


class ScriptCreate(BaseModel):
    name: str
    prompt: str
    plan: list[dict] | None = None
    generated_code: str | None = None


class ScriptUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None
    plan: list[dict] | None = None
    generated_code: str | None = None


class ScriptResponse(BaseModel):
    id: str
    name: str
    prompt: str
    plan: list[dict] | None
    generated_code: str | None
    last_successful_run: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    prompt: str


class RefineRequest(BaseModel):
    prompt: str
    current_plan: list[dict]
    failure: dict
    annotations: list[str] = []
    screenshot_base64: str | None = None


class ExecuteRequest(BaseModel):
    plan: list[dict]
    prompt: str
    script_id: str | None = None
