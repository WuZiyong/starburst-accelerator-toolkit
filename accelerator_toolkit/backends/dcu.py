from __future__ import annotations

from pathlib import Path
from typing import Any

from accelerator_toolkit.util import run_capture, shell_join

NAME = "dcu"


def dtk_root(profile: dict[str, Any]) -> str:
    return str(profile.get("runtime", {}).get("dtk_root") or "/opt/dtk")


def shell_prelude(profile: dict[str, Any]) -> list[str]:
    runtime = profile.get("runtime", {})
    root = dtk_root(profile)
    lines = [f'source "{root}/env.sh"', 'export PATH="/sbin:/usr/sbin:$PATH"', f'export HSA_FORCE_FINE_GRAIN_PCIE="{runtime.get("hsa_force_fine_grain_pcie", 1)}"']
    env = runtime.get("python_env")
    if env:
        lines.append(f'source "{env}/bin/activate"')
    return lines


def doctor(profile: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = dtk_root(profile)
    smi = str(Path(root) / "bin/hy-smi")
    rc, out = run_capture([smi, "--showmeminfo", "vram"])
    total_lines = [line.strip() for line in out.splitlines() if "Total Memory" in line]
    checks.append({"check": "hy-smi", "status": "PASS" if rc == 0 and total_lines else "FAIL", "devices": len(total_lines), "vram": total_lines, "output": out.strip() if rc else None})

    pci_id = str(profile.get("hardware", {}).get("pci_id") or "1d94:54b7")
    rc_pci, pci = run_capture(["/sbin/lspci", "-nn"])
    pci_count = sum(pci_id.lower() in line.lower() for line in pci.splitlines()) if rc_pci == 0 else 0
    checks.append({"check": "pci_devices", "status": "PASS" if pci_count else "FAIL", "pci_id": pci_id, "count": pci_count})

    configured = profile.get("hardware", {}).get("configured_devices")
    if configured is not None:
        status = "PASS" if pci_count == int(configured) else "WARN"
        checks.append({"check": "configured_device_count", "status": status, "configured": int(configured), "visible": pci_count})

    env = profile.get("runtime", {}).get("python_env")
    if env:
        py = Path(env) / "bin/python"
        checks.append({"check": "python_env", "status": "PASS" if py.exists() else "WARN", "path": str(py)})
    return checks


def detect(profile: dict[str, Any] | None = None) -> bool:
    roots = []
    if profile:
        roots.append(dtk_root(profile))
    roots += ["/opt/dtk-24.04.1", "/opt/dtk-23.04", "/opt/dtk"]
    for root in roots:
        smi = Path(root) / "bin/hy-smi"
        if smi.exists():
            rc, out = run_capture([str(smi)], timeout=5)
            if rc == 0 and "DCU" in out:
                return True
    return False


def describe_command(profile: dict[str, Any], command: list[str]) -> str:
    return "; ".join([*shell_prelude(profile), f"exec {shell_join(command)}"])
