# win-auto/backend/tests/test_routes_generate.py
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
MOCK_PLAN = [{"step": 1, "action": "wait", "target": "", "description": "Wait", "params": {"seconds": 1}, "backend": "uia"}]

class TestGenerateRoutes:
    @patch("routes.generate.llm_service")
    def test_generate_plan(self, mock_llm):
        mock_llm.generate_plan.return_value = MOCK_PLAN
        resp = client.post("/api/generate", json={"prompt": "Wait 1 second"})
        assert resp.status_code == 200
        assert resp.json()["plan"] == MOCK_PLAN
        assert "generated_code" in resp.json()

    @patch("routes.generate.llm_service")
    def test_refine_plan(self, mock_llm):
        mock_llm.refine_plan.return_value = MOCK_PLAN
        resp = client.post("/api/generate/refine", json={
            "prompt": "Wait", "current_plan": MOCK_PLAN,
            "failure": {"step": 1, "error": "Timeout"}, "annotations": ["Try shorter wait"],
        })
        assert resp.status_code == 200
        assert resp.json()["plan"] == MOCK_PLAN
