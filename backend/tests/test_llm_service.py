# win-auto/backend/tests/test_llm_service.py
import pytest
import json
from unittest.mock import patch, MagicMock
from services.llm_service import LLMService

MOCK_PLAN = [
    {"step": 1, "action": "open_application", "target": "Notepad",
     "description": "Open Notepad", "params": {"method": "start_menu", "search_term": "Notepad"}, "backend": "uia"},
    {"step": 2, "action": "type_text", "target": "Notepad editor",
     "description": "Type hello", "params": {"text": "Hello World", "method": "keyboard"}, "backend": "uia"},
]

class TestLLMService:
    @patch("services.llm_service.anthropic")
    def test_generate_plan(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(MOCK_PLAN))]
        mock_client.messages.create.return_value = mock_response

        service = LLMService()
        plan = service.generate_plan("Open notepad and type hello")
        assert len(plan) == 2
        assert plan[0]["action"] == "open_application"

    @patch("services.llm_service.anthropic")
    def test_refine_plan(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(MOCK_PLAN))]
        mock_client.messages.create.return_value = mock_response

        service = LLMService()
        plan = service.refine_plan(
            prompt="Open notepad",
            current_plan=MOCK_PLAN,
            failure={"step": 1, "error": "Window not found"},
            annotations=["Try Start Menu search"],
        )
        assert len(plan) == 2
        call_args = mock_client.messages.create.call_args
        assert any("Window not found" in str(m) for m in call_args.kwargs["messages"])
