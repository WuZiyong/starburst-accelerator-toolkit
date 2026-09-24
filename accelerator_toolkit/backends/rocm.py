from __future__ import annotations

from pathlib import Path
from typing import Any

from accelerator_toolkit.util import run_capture, shell_join

NAME = "rocm"


def shell_prelude(profile: dict[str, Any]) -> list[str]:
    runtime = profile.get("runtime", {})
    root = str(runtime.get("rocm_root") or "/opt/rocm")
    lines = [f'export ROCM_PATH="{root}"', f'export PATH="{root}/bin:{root}/hip/bin:$PATH"', f'export LD_LIBRARY_PATH="{root}/lib:{root}/lib64:${{LD_LIBRARY_PATH:-}}"']
    env = runtime.get("python_env")
    if env:
        lines.append(f'source "{env}/bin/activate"')
    return lines


def doctor(profile: dict[str, Any]) -> list[dict[str, Any]]:
    root = str(profile.get("runtime", {}).get("rocm_root") or "/opt/rocm")
    smi = Path(root) / "bin/rocm-smi"
    rc, out = run_capture([str(smi)]) if smi.exists() else (127, f"missing {smi}")
    checks = [{"check": "rocm-smi", "status": "PASS" if rc == 0 else "FAIL", "output": out.strip()}]
    env = profile.get("runtime", {}).get("python_env")
    if env:
        py = Path(env) / "bin/python"
        checks.append({"check": "python_env", "status": "PASS" if py.exists() else "WARN", "path": str(py)})
    return checks


def detect() -> bool:
    for path in (Path("/opt/rocm/bin/rocm-smi"), Path("/usr/bin/rocm-smi")):
        if path.exists() and run_capture([str(path)], timeout=5)[0] == 0:
            return True
    return False


def describe_command(profile: dict[str, Any], command: list[str]) -> str:
    return "; ".join([*shell_prelude(profile), f"exec {shell_join(command)}"])
