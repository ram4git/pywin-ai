# win-auto/backend/main.py
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from db.database import engine, SessionLocal, Base
from db.models import Execution, ExecutionStatus

if settings.log_file:
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(settings.log_file, mode="a")] if settings.log_file else [logging.StreamHandler()])
logger = logging.getLogger(__name__)

def cleanup_orphaned_executions():
    db = SessionLocal()
    try:
        orphans = db.query(Execution).filter(Execution.status == ExecutionStatus.running).all()
        for orphan in orphans:
            if orphan.pid:
                try:
                    import subprocess, sys
                    if sys.platform == "win32":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(orphan.pid)], capture_output=True, timeout=5)
                except Exception:
                    pass
            orphan.status = ExecutionStatus.failed
            orphan.error_message = "Server restarted during execution"
            orphan.finished_at = datetime.utcnow()
            logger.info(f"Cleaned orphan: {orphan.id}")
        db.commit()
    finally:
        db.close()

def prune_old_screenshots():
    sdir = Path(settings.screenshots_dir)
    if not sdir.exists():
        return
    cutoff = datetime.utcnow() - timedelta(days=settings.screenshot_retention_days)
    for d in sdir.iterdir():
        if d.is_dir():
            try:
                if datetime.fromtimestamp(d.stat().st_mtime) < cutoff:
                    import shutil
                    shutil.rmtree(d)
                    logger.info(f"Pruned screenshots: {d.name}")
            except Exception as e:
                logger.warning(f"Prune failed {d}: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    Path(settings.screenshots_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.scripts_dir).mkdir(parents=True, exist_ok=True)
    if settings.log_file:
        Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
    cleanup_orphaned_executions()
    prune_old_screenshots()
    logger.info(f"Win-Auto starting on {settings.server_host}:{settings.server_port}")
    yield
    logger.info("Win-Auto shutting down")

app = FastAPI(title="Win-Auto", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from routes.scripts import router as scripts_router
from routes.generate import router as generate_router
from routes.execute import router as execute_router
app.include_router(scripts_router)
app.include_router(generate_router)
app.include_router(execute_router)

screenshots_path = Path(settings.screenshots_dir)
if screenshots_path.exists():
    app.mount("/screenshots", StaticFiles(directory=str(screenshots_path)), name="screenshots")

@app.get("/health")
async def health():
    return {"status": "ok"}

frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.server_host, port=settings.server_port, reload=True)
