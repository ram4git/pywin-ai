# win-auto/backend/tests/test_routes_execute.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from db.database import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)
MOCK_PLAN = [{"step": 1, "action": "wait", "target": "", "description": "Wait", "params": {"seconds": 1}, "backend": "uia"}]

class TestExecuteRoutes:
    @patch("routes.execute.executor_service")
    @patch("routes.execute.validate_code")
    @patch("routes.execute.generate_code")
    def test_start_execution(self, mock_gen, mock_val, mock_exec):
        mock_gen.return_value = "# code"
        mock_val.return_value = MagicMock(is_valid=True)
        mock_process = MagicMock(pid=12345)
        mock_exec.start.return_value = mock_process
        mock_exec.is_running = False
        resp = client.post("/api/execute", json={"plan": MOCK_PLAN, "prompt": "Wait"})
        assert resp.status_code == 200
        assert "execution_id" in resp.json()

    @patch("routes.execute.executor_service")
    def test_rejects_concurrent(self, mock_exec):
        mock_exec.is_running = True
        resp = client.post("/api/execute", json={"plan": MOCK_PLAN, "prompt": "Wait"})
        assert resp.status_code == 409

    @patch("routes.execute.executor_service")
    @patch("routes.execute.validate_code")
    @patch("routes.execute.generate_code")
    def test_rejects_invalid_code(self, mock_gen, mock_val, mock_exec):
        mock_gen.return_value = "bad"
        mock_val.return_value = MagicMock(is_valid=False, error="Disallowed import")
        mock_exec.is_running = False
        resp = client.post("/api/execute", json={"plan": MOCK_PLAN, "prompt": "Naughty"})
        assert resp.status_code == 400
