from __future__ import annotations

import subprocess
from typing import Any, Sequence

from accelerator_toolkit.backends import get_backend
from accelerator_toolkit.util import shell_join


def render_script(profile: dict[str, Any], command: Sequence[str]) -> str:
    sched = profile.get("scheduler", {})
    lines = ["#!/usr/bin/env bash"]
    opts = {
        "partition": sched.get("partition"),
        "nodes": sched.get("nodes", 1),
        "ntasks": sched.get("ntasks", 1),
        "cpus-per-task": sched.get("cpus_per_task", 8),
        "mem": sched.get("mem", "32G"),
        "gres": sched.get("gres"),
        "job-name": sched.get("job_name", "accel-job"),
        "output": sched.get("output", "slurm-%j.out"),
    }
    for key, value in opts.items():
        if value is not None:
            lines.append(f"#SBATCH --{key}={value}")
    extra = sched.get("extra", []) or []
    lines.extend(f"#SBATCH {item}" for item in extra)
    lines += ["set -Eeuo pipefail", ""]
    backend = get_backend(str(profile["backend"]))
    lines.extend(backend.shell_prelude(profile))
    lines += ["", f"exec {shell_join([str(x) for x in command])}", ""]
    return "\n".join(lines)


def submit(profile: dict[str, Any], command: Sequence[str], dry_run: bool = False) -> tuple[int, str]:
    script = render_script(profile, command)
    if dry_run:
        return 0, script
    proc = subprocess.run(["sbatch"], input=script, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout
