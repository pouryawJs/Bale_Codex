import os
import sys
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = PROJECT_ROOT / "logs" / "mcp.log"


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
    LOG_FILE.parent.mkdir(exist_ok=True)
    python_executable = find_python_executable()

    os.chdir(PROJECT_ROOT)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write("\n--- Starting MCP server ---\n")
        log.write(f"Project root: {PROJECT_ROOT}\n")
        log.write(f"Python executable: {python_executable}\n")
        log.flush()

        subprocess.run(
            [
                python_executable,
                "-m",
                "interfaces.mcp_server",
            ],
            stdout=sys.stdout,   # برای پروتکل MCP باید دست‌نخورده بماند
            stderr=log,          # خطاها داخل فایل ذخیره می‌شوند
            cwd=PROJECT_ROOT,
            check=False,
        )


if __name__ == "__main__":
    main()