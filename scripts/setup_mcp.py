import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def find_python_executable() -> Path:
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
            return candidate

    return Path(sys.executable)


def main():
    python_executable = find_python_executable()
    run_mcp_path = PROJECT_ROOT / "scripts" / "run_mcp.py"

    print("\nCodex MCP Server settings")
    print("=" * 40)
    print("\nCommand to launch:")
    print(str(python_executable))

    print("\nArguments:")
    print(str(run_mcp_path))

    print("\nWorking directory:")
    print(str(PROJECT_ROOT))

    print("\nIf your Codex UI asks for one argument per row, add only this one:")
    print(str(run_mcp_path))

    print("\nIf you edit config.toml manually, use this:")
    print()
    print("[mcp_servers.bale_codex]")
    print(f'command = "{str(python_executable).replace("\\\\", "\\\\\\\\")}"')
    print(f'args = ["{str(run_mcp_path).replace("\\\\", "\\\\\\\\")}"]')
    print(f'cwd = "{str(PROJECT_ROOT).replace("\\\\", "\\\\\\\\")}"')
    print("tool_timeout_sec = 120")


if __name__ == "__main__":
    main()
