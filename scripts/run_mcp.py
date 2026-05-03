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

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write("\n--- MCP launcher started ---\n")
        log_file.write(f"Project root: {PROJECT_ROOT}\n")
        log_file.write(f"Python executable: {python_executable}\n")
        log_file.flush()

        subprocess.run(
            [
                python_executable,
                "-m",
                "interfaces.mcp_server",
            ],
            cwd=PROJECT_ROOT,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=log_file,
            check=False,
        )


if __name__ == "__main__":
    main()