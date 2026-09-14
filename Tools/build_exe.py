"""Build the Windows GUI with an isolated, pinned PyInstaller environment."""
from pathlib import Path
import os
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent.parent
PYINSTALLER_VERSION = "6.22.3"


def main():
    if sys.platform != "win32":
        raise SystemExit("Build the Windows EXE on Windows.")
    environment = ROOT / "Temp" / "config-tool-build-env"
    python = environment / "Scripts" / "python.exe"
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    f"pyinstaller=={PYINSTALLER_VERSION}"], check=True)
    build_env = os.environ.copy()
    build_env["PYINSTALLER_CONFIG_DIR"] = str(ROOT / "Temp" / "config-tool-pyinstaller-cache")
    subprocess.run([
        str(python), "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", "TDConfigTool", "--noupx",
        "--distpath", str(ROOT / "Builds" / "ConfigTool"),
        "--workpath", str(ROOT / "Temp" / "config-tool-pyinstaller"),
        "--specpath", str(ROOT / "Temp"),
        "--paths", str(ROOT / "Tools"), str(ROOT / "Tools" / "config_desktop.py"),
    ], check=True, cwd=ROOT, env=build_env)
    print(ROOT / "Builds" / "ConfigTool" / "TDConfigTool.exe")


if __name__ == "__main__":
    main()
