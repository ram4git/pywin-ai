# win-auto/backend/routes/scripts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Script
from routes.schemas import ScriptCreate, ScriptUpdate, ScriptResponse

router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.get("", response_model=list[ScriptResponse])
def list_scripts(db: Session = Depends(get_db)):
    return db.query(Script).order_by(Script.updated_at.desc()).all()


@router.get("/{script_id}", response_model=ScriptResponse)
def get_script(script_id: str, db: Session = Depends(get_db)):
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.post("", response_model=ScriptResponse, status_code=201)
def create_script(body: ScriptCreate, db: Session = Depends(get_db)):
    script = Script(**body.model_dump())
    db.add(script)
    db.commit()
    db.refresh(script)
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
def update_script(script_id: str, body: ScriptUpdate, db: Session = Depends(get_db)):
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(script, key, value)
    db.commit()
    db.refresh(script)
    return script


@router.delete("/{script_id}", status_code=204)
def delete_script(script_id: str, db: Session = Depends(get_db)):
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    db.delete(script)
    db.commit()
