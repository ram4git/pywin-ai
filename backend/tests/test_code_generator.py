"""Tests for the code generator service."""
import ast
import pytest
from services.code_generator import generate_code

SAMPLE_PLAN = [
    {"step": 1, "action": "open_application", "target": "Notepad", "description": "Open Notepad",
     "params": {"method": "start_menu", "search_term": "Notepad"}, "backend": "uia"},
    {"step": 2, "action": "wait_for_window", "target": "Notepad", "description": "Wait for Notepad",
     "params": {"timeout_seconds": 10}, "backend": "uia"},
    {"step": 3, "action": "type_text", "target": "Editor", "description": "Type hello",
     "params": {"text": "Hello World", "method": "keyboard"}, "backend": "uia"},
]

class TestCodeGenerator:
    def test_generates_valid_python(self):
        code = generate_code(SAMPLE_PLAN, "test-123", "data/screenshots")
        ast.parse(code)  # Should not raise

    def test_includes_all_steps(self):
        code = generate_code(SAMPLE_PLAN, "test-123", "data/screenshots")
        assert "Step 1" in code and "Step 2" in code and "Step 3" in code

    def test_includes_reporting(self):
        code = generate_code(SAMPLE_PLAN, "test-123", "data/screenshots")
        assert "report_step" in code and "report_complete" in code

    def test_includes_error_handling(self):
        code = generate_code(SAMPLE_PLAN, "test-123", "data/screenshots")
        assert "except" in code and "report_error" in code

    def test_includes_screenshot_capture(self):
        code = generate_code(SAMPLE_PLAN, "test-123", "data/screenshots")
        assert "capture_screenshot" in code

    def test_includes_stabilization_delay(self):
        code = generate_code(SAMPLE_PLAN, "test-123", "data/screenshots")
        assert "0.3" in code
