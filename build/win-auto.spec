# win-auto/build/win-auto.spec
from pathlib import Path
block_cipher = None
root = Path(SPECPATH).parent
a = Analysis(
    [str(root / 'backend' / 'main.py')],
    pathex=[str(root / 'backend')],
    datas=[
        (str(root / 'frontend' / 'dist'), 'frontend/dist'),
        (str(root / 'backend' / 'alembic'), 'alembic'),
        (str(root / 'backend' / 'alembic.ini'), '.'),
        (str(root / 'backend' / '.env.example'), '.'),
    ],
    hiddenimports=[
        'pywinauto', 'pywinauto.controls', 'anthropic',
        'sqlalchemy', 'sqlalchemy.dialects.sqlite',
        'mss', 'pyperclip', 'pyautogui',
        'uvicorn.logging', 'uvicorn.protocols.http', 'alembic',
    ],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='win-auto', debug=False, strip=False, upx=True, console=False)
