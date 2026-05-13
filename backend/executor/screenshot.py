# win-auto/backend/executor/screenshot.py
from pathlib import Path

def capture_screenshot(execution_id: str, step_number: int, screenshots_dir: str) -> str:
    step_dir = Path(screenshots_dir) / execution_id
    step_dir.mkdir(parents=True, exist_ok=True)
    filepath = step_dir / f"step-{step_number}.png"
    try:
        import mss
        with mss.mss() as sct:
            sct.shot(output=str(filepath))
    except Exception:
        filepath.touch()
    return str(filepath)
