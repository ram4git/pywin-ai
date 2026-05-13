# win-auto/backend/services/executor_service.py
import subprocess
import sys
import os
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator

class ExecutorService:
    def __init__(self):
        self._mutex_locked = False
        self._current_pid: int | None = None
        self._current_process: subprocess.Popen | None = None

    @property
    def is_running(self) -> bool:
        return self._mutex_locked

    def start(self, script_path: str, execution_id: str) -> subprocess.Popen:
        if self._mutex_locked:
            raise RuntimeError("Another execution is already running")
        self._mutex_locked = True
        env = os.environ.copy()
        env["WINAUTOUTIL_PATH"] = str(Path(__file__).resolve().parent.parent)
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
        self._current_process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, creationflags=creation_flags,
        )
        self._current_pid = self._current_process.pid
        return self._current_process

    def stop(self):
        if self._current_pid:
            try:
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(self._current_pid)],
                                   capture_output=True, timeout=5)
                else:
                    import signal
                    os.kill(self._current_pid, signal.SIGTERM)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
        self._release()

    def _release(self):
        self._mutex_locked = False
        self._current_pid = None
        self._current_process = None

    async def stream_output(self, process: subprocess.Popen) -> AsyncGenerator[dict, None]:
        loop = asyncio.get_event_loop()
        while True:
            line = await loop.run_in_executor(None, process.stdout.readline)
            if not line:
                break
            try:
                data = json.loads(line.decode().strip())
                yield data
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read().decode() if process.stderr else ""
            yield {"type": "execution_failed", "error": stderr or f"Exit code {process.returncode}"}
        self._release()

executor_service = ExecutorService()
