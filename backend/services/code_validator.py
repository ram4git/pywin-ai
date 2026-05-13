# win-auto/backend/services/code_validator.py
import ast
from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    error: str | None = None


ALLOWED_IMPORTS: set[str] = {
    "pywinauto", "time", "pyperclip", "pyautogui",
    "PIL", "mss", "os", "os.path", "json", "sys",
}

PROHIBITED_BUILTINS: set[str] = {
    "compile", "__import__", "breakpoint",
    "globals", "locals", "delattr", "setattr",
    "eval", "exec",
}

PROHIBITED_ATTR_CALLS: set[tuple[str, str]] = {
    ("os", "system"), ("os", "popen"), ("os", "remove"),
    ("os", "unlink"), ("os", "rmdir"),
    ("shutil", "rmtree"), ("shutil", "move"),
}


class _SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if alias.name not in ALLOWED_IMPORTS and root not in ALLOWED_IMPORTS:
                self.violations.append(f"Disallowed import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root = node.module.split(".")[0]
            if node.module not in ALLOWED_IMPORTS and root not in ALLOWED_IMPORTS:
                self.violations.append(f"Disallowed import: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in PROHIBITED_BUILTINS:
                self.violations.append(f"Prohibited function call: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                pair = (node.func.value.id, node.func.attr)
                if pair in PROHIBITED_ATTR_CALLS:
                    self.violations.append(f"Prohibited call: {pair[0]}.{pair[1]}")
        self.generic_visit(node)


def validate_code(source: str) -> ValidationResult:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return ValidationResult(is_valid=False, error=f"Syntax error: {e}")
    visitor = _SecurityVisitor()
    visitor.visit(tree)
    if visitor.violations:
        return ValidationResult(is_valid=False, error="; ".join(visitor.violations))
    return ValidationResult(is_valid=True)
