#!/usr/bin/env python3
"""Code generator: compiles a structured JSON plan into a runnable PyWinAuto script."""
import json
from typing import Callable

SCRIPT_HEADER = '''#!/usr/bin/env python3
"""Auto-generated PyWinAuto automation script."""
import sys
import os
sys.path.insert(0, os.environ.get("WINAUTOUTIL_PATH", os.path.dirname(os.path.abspath(__file__)) + "/.."))

import json
import time
import pywinauto
import pyautogui

from executor.helpers import report_step, report_complete, report_error
from executor.screenshot import capture_screenshot

EXECUTION_ID = "{execution_id}"
SCREENSHOTS_DIR = "{screenshots_dir}"

'''

def _gen_open_application(params: dict, backend: str) -> list[str]:
    method = params.get("method", "start_menu")
    if method == "start_menu":
        term = params.get("search_term", "")
        return [
            "pyautogui.hotkey('win')", "time.sleep(0.5)",
            f"pyautogui.typewrite({json.dumps(term)}, interval=0.05)",
            "time.sleep(1)", "pyautogui.press('enter')", "time.sleep(2)",
        ]
    elif method == "path":
        exe = params.get("exe_path", "")
        return [f"app = pywinauto.Application(backend={json.dumps(backend)}).start({json.dumps(exe)})", "time.sleep(2)"]
    return ["pass  # open_application: unsupported method"]

def _gen_wait_for_window(params: dict, backend: str) -> list[str]:
    timeout = params.get("timeout_seconds", 10)
    title = params.get("title", params.get("target", "Untitled"))
    return [
        f"pywinauto.timings.wait_until_passes({timeout}, 0.5,",
        f"    lambda: pywinauto.findwindows.find_windows(title_re=r'.*{title}.*'))",
    ]

def _gen_click_element(params: dict, backend: str) -> list[str]:
    name = params.get("name", "")
    auto_id = params.get("automation_id", "")
    if name:
        return [f"pywinauto.Desktop(backend={json.dumps(backend)}).window(title_re=r'.*').child_window(title={json.dumps(name)}).click_input()"]
    elif auto_id:
        return [f"pywinauto.Desktop(backend={json.dumps(backend)}).window(title_re=r'.*').child_window(auto_id={json.dumps(auto_id)}).click_input()"]
    return ["pass  # click_element: no target specified"]

def _gen_type_text(params: dict, backend: str) -> list[str]:
    text = params.get("text", "")
    method = params.get("method", "keyboard")
    if method == "keyboard":
        return [f"pyautogui.typewrite({json.dumps(text)}, interval=0.02)"]
    return [f"pass  # type_text: set_text requires specific control"]

def _gen_keyboard_shortcut(params: dict, backend: str) -> list[str]:
    keys = params.get("keys", "")
    parts = [k.strip().lower() for k in keys.split("+")]
    return [f"pyautogui.hotkey({', '.join(json.dumps(p) for p in parts)})"]

def _gen_wait(params: dict, backend: str) -> list[str]:
    return [f"time.sleep({params.get('seconds', 1)})"]

def _gen_focus_window(params: dict, backend: str) -> list[str]:
    title = params.get("title", "")
    return [f"pywinauto.Desktop(backend={json.dumps(backend)}).window(title_re=r'.*{title}.*').set_focus()"]

def _gen_clipboard_copy(params: dict, backend: str) -> list[str]:
    return ["pyautogui.hotkey('ctrl', 'c')", "time.sleep(0.5)"]

def _gen_clipboard_paste(params: dict, backend: str) -> list[str]:
    return ["pyautogui.hotkey('ctrl', 'v')", "time.sleep(0.5)"]

def _gen_select_menu_item(params: dict, backend: str) -> list[str]:
    path = params.get("path", "")
    parts = [p.strip() for p in path.split("->")]
    return [f"pywinauto.Desktop(backend={json.dumps(backend)}).window(title_re=r'.*').menu_select({json.dumps(' -> '.join(parts))})"]

def _gen_close_window(params: dict, backend: str) -> list[str]:
    return ["pyautogui.hotkey('alt', 'F4')"]

def _gen_assert_element_exists(params: dict, backend: str) -> list[str]:
    name = params.get("name", "")
    timeout = params.get("timeout_seconds", 5)
    return [f"pywinauto.Desktop(backend={json.dumps(backend)}).window(title_re=r'.*').child_window(title={json.dumps(name)}).wait('exists', timeout={timeout})"]

def _gen_noop(params: dict, backend: str) -> list[str]:
    return ["pass  # Action type requires manual implementation"]

ACTION_GENERATORS: dict[str, Callable] = {
    "open_application": _gen_open_application,
    "wait_for_window": _gen_wait_for_window,
    "click_element": _gen_click_element,
    "right_click_element": _gen_click_element,
    "select_menu_item": _gen_select_menu_item,
    "select_tree_item": _gen_noop,
    "type_text": _gen_type_text,
    "keyboard_shortcut": _gen_keyboard_shortcut,
    "clipboard_copy": _gen_clipboard_copy,
    "clipboard_paste": _gen_clipboard_paste,
    "paste_special": _gen_clipboard_paste,
    "wait": _gen_wait,
    "focus_window": _gen_focus_window,
    "close_window": _gen_close_window,
    "select_combo_box": _gen_noop,
    "select_tab": _gen_noop,
    "scroll": _gen_noop,
    "assert_element_exists": _gen_assert_element_exists,
    "assert_text_contains": _gen_noop,
}

def generate_code(plan: list[dict], execution_id: str, screenshots_dir: str) -> str:
    """Compile a structured JSON plan into a runnable PyWinAuto Python script."""
    lines: list[str] = [SCRIPT_HEADER.format(execution_id=execution_id, screenshots_dir=screenshots_dir)]
    for step in plan:
        step_num = step["step"]
        action = step.get("action", "unknown")
        desc = step.get("description", action)
        backend = step.get("backend", "uia")
        params = step.get("params", {})
        generator = ACTION_GENERATORS.get(action, _gen_noop)
        action_lines = generator(params, backend)

        lines.append(f"# Step {step_num}: {desc}")
        lines.append(f"report_step({step_num}, 'running')")
        lines.append("try:")
        for al in action_lines:
            lines.append(f"    {al}")
        lines.append(f"    time.sleep(0.3)")
        lines.append(f"    capture_screenshot(EXECUTION_ID, {step_num}, SCREENSHOTS_DIR)")
        lines.append(f"    report_step({step_num}, 'done')")
        lines.append("except Exception as _step_err:")
        lines.append(f"    capture_screenshot(EXECUTION_ID, {step_num}, SCREENSHOTS_DIR)")
        lines.append(f"    report_error({step_num}, str(_step_err))")
        lines.append(f"    sys.exit(1)")
        lines.append("")
    lines.append("report_complete()")
    return "\n".join(lines)
