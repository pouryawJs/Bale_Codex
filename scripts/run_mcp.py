import os
import sys
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def find_python_executable() -> str:
    candidates = [
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".env" / "Scripts" / "python.exe",
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "bin" / "python",
        PROJECT_ROOT / ".env" / "bin" / "python",
        PROJECT_ROOT / "venv" / "bin" / "python",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return sys.executable


def main():
    python_executable = find_python_executable()

    os.chdir(PROJECT_ROOT)

    subprocess.run(
        [
            python_executable,
            "-m",
            "interfaces.mcp_server",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()