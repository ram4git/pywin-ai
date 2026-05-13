# win-auto/backend/services/llm_service.py
import json
import logging
import re
import anthropic
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Windows desktop automation expert. Generate structured action plans for PyWinAuto.

OUTPUT FORMAT:
Return a JSON array of step objects. Each step:
- "step": integer (1-indexed)
- "action": action type (see list below)
- "target": human-readable target description
- "description": what this step does
- "params": action-specific parameters
- "backend": "uia" (default) or "win32"

Return raw JSON only. No markdown wrapping.

AVAILABLE ACTIONS:
- open_application: params: method (start_menu|path|taskbar), search_term or exe_path
- wait_for_window: params: timeout_seconds (default 10), title
- click_element: params: method (name|automation_id|toolbar_button), name or automation_id
- right_click_element: same params as click_element
- select_menu_item: params: path (e.g. "File->Save As")
- select_tree_item: params: path, action (select|expand|collapse)
- type_text: params: text, method (keyboard|set_text)
- keyboard_shortcut: params: keys (e.g. "Ctrl+C", "F5")
- clipboard_copy: params: select_method, copy_method
- clipboard_paste: params: paste_method
- paste_special: params: format (text|html|unicode)
- wait: params: seconds
- focus_window: params: title (partial match)
- close_window: params: title, method (close_button|alt_f4|click_x)
- select_combo_box: params: name/automation_id, value
- select_tab: params: name or index
- scroll: params: direction (up|down|left|right), amount
- assert_element_exists: params: name/automation_id, timeout_seconds
- assert_text_contains: params: target, expected_text

BACKEND: "uia" for modern apps (WPF, WinForms, Excel, Outlook). "win32" for legacy MFC/Win32.

SAFETY: Never generate code that deletes files, makes network requests, or runs shell commands.

BEST PRACTICES:
- wait_for_window after open_application
- assert_element_exists before critical clicks
- Prefer name-based targeting over coordinates
- Short wait steps after clipboard operations
- One UI interaction per step
"""


class LLMService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def _parse_json(self, text: str) -> list[dict]:
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        logger.debug("LLM raw response (first 200 chars): %s", text[:200])
        return json.loads(cleaned)

    def generate_plan(self, prompt: str) -> list[dict]:
        response = self.client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_json(response.content[0].text)

    def refine_plan(
        self, prompt: str, current_plan: list[dict],
        failure: dict, annotations: list[str],
        screenshot_base64: str | None = None,
    ) -> list[dict]:
        context_parts = [
            f"ORIGINAL PROMPT:\n{prompt}",
            f"\nMOST RECENT PLAN:\n{json.dumps(current_plan, indent=2)}",
            f"\nFAILURE:\nStep {failure.get('step', '?')} failed: {failure.get('error', 'unknown')}",
        ]
        if annotations:
            context_parts.append("\nUSER NOTES:\n" + "\n".join(f"- {a}" for a in annotations))
        context_parts.append("\nGenerate an improved plan that fixes the failure.")

        messages_content = []
        if screenshot_base64:
            messages_content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": screenshot_base64},
            })
        messages_content.append({"type": "text", "text": "\n".join(context_parts)})

        response = self.client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": messages_content}],
        )
        return self._parse_json(response.content[0].text)
