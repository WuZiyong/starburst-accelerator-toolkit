from __future__ import annotations

from pathlib import Path
from typing import Any

from accelerator_toolkit.util import run_capture, shell_join

NAME = "cuda"


def shell_prelude(profile: dict[str, Any]) -> list[str]:
    runtime = profile.get("runtime", {})
    lines: list[str] = []
    cuda_root = runtime.get("cuda_root")
    if cuda_root:
        lines += [f'export PATH="{cuda_root}/bin:$PATH"', f'export LD_LIBRARY_PATH="{cuda_root}/lib64:${{LD_LIBRARY_PATH:-}}"']
    env = runtime.get("python_env")
    if env:
        lines.append(f'source "{env}/bin/activate"')
    return lines


def doctor(profile: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    rc, out = run_capture(["nvidia-smi", "-L"])
    devices = [line for line in out.splitlines() if line.strip().startswith("GPU ")]
    checks.append({"check": "nvidia-smi", "status": "PASS" if rc == 0 and devices else "FAIL", "devices": devices, "output": out.strip() if rc else None})
    env = profile.get("runtime", {}).get("python_env")
    if env:
        py = Path(env) / "bin/python"
        checks.append({"check": "python_env", "status": "PASS" if py.exists() else "WARN", "path": str(py)})
    return checks


def detect() -> bool:
    rc, out = run_capture(["nvidia-smi", "-L"], timeout=5)
    return rc == 0 and "GPU " in out


def describe_command(profile: dict[str, Any], command: list[str]) -> str:
    return "; ".join([*shell_prelude(profile), f"exec {shell_join(command)}"])
