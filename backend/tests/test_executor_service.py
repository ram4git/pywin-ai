# win-auto/backend/tests/test_executor_service.py
import pytest
from unittest.mock import patch, MagicMock
from services.executor_service import ExecutorService

class TestExecutorService:
    def test_mutex_prevents_concurrent_runs(self):
        service = ExecutorService()
        service._mutex_locked = True
        with pytest.raises(RuntimeError, match="already running"):
            service.start("dummy.py", "exec-1")

    def test_mutex_released_after_stop(self):
        service = ExecutorService()
        service._mutex_locked = True
        service._current_pid = 12345
        with patch("services.executor_service.os.kill") as mock_kill:
            service.stop()
        assert not service._mutex_locked

    def test_start_sets_mutex(self):
        service = ExecutorService()
        with patch("services.executor_service.subprocess") as mock_sub:
            mock_process = MagicMock()
            mock_process.pid = 99999
            mock_sub.Popen.return_value = mock_process
            mock_sub.CREATE_NEW_PROCESS_GROUP = 0x200
            service.start("test.py", "exec-1")
        assert service._mutex_locked
        assert service._current_pid == 99999
