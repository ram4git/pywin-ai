# win-auto/backend/tests/test_code_validator.py
import pytest
from services.code_validator import validate_code

class TestValidateCode:
    def test_valid_pywinauto_code(self):
        code = "import pywinauto\nimport time\napp = pywinauto.Application(backend='uia')\ntime.sleep(1)"
        result = validate_code(code)
        assert result.is_valid

    def test_allows_all_permitted_imports(self):
        code = "import pywinauto\nimport time\nimport json\nimport sys\nimport os\nimport pyperclip\nimport pyautogui\nimport mss\nfrom PIL import Image"
        result = validate_code(code)
        assert result.is_valid

    def test_rejects_disallowed_import(self):
        result = validate_code("import requests")
        assert not result.is_valid
        assert "requests" in result.error

    def test_rejects_subprocess_import(self):
        result = validate_code("import subprocess")
        assert not result.is_valid
        assert "subprocess" in result.error

    def test_rejects_from_import(self):
        result = validate_code("from http.client import HTTPConnection")
        assert not result.is_valid
        assert "http" in result.error

    def test_rejects_os_remove(self):
        result = validate_code("import os\nos.remove('f.txt')")
        assert not result.is_valid
        assert "os.remove" in result.error

    def test_rejects_shutil_rmtree(self):
        result = validate_code("import shutil\nshutil.rmtree('/tmp')")
        assert not result.is_valid
        assert "shutil.rmtree" in result.error

    def test_rejects_syntax_error(self):
        result = validate_code("def foo(")
        assert not result.is_valid
        assert "Syntax" in result.error

    def test_allows_os_path_join(self):
        result = validate_code("import os.path\nresult = os.path.join('a', 'b')")
        assert result.is_valid

    def test_rejects_prohibited_builtin(self):
        result = validate_code("x = __import__('os')")
        assert not result.is_valid
        assert "Prohibited" in result.error
