"""Build win-auto as a single .exe."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def build_frontend():
    print("Building frontend...")
    subprocess.run(["yarn", "install"], cwd=str(ROOT / "frontend"), check=True)
    subprocess.run(["yarn", "build"], cwd=str(ROOT / "frontend"), check=True)

def build_exe():
    print("Building .exe...")
    subprocess.run([sys.executable, "-m", "PyInstaller", str(ROOT / "build" / "win-auto.spec"), "--clean"], cwd=str(ROOT), check=True)
    print(f"Done: {ROOT / 'dist' / 'win-auto.exe'}")

if __name__ == "__main__":
    build_frontend()
    build_exe()
