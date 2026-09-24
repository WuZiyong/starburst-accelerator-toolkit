from __future__ import annotations

import subprocess
from typing import Any, Sequence

from accelerator_toolkit.backends import get_backend
from accelerator_toolkit.util import hostname, shell_join


def runtime_shell(profile: dict[str, Any], command: Sequence[str]) -> str:
    backend = get_backend(str(profile["backend"]))
    return backend.describe_command(profile, [str(x) for x in command])


def remote_host(profile: dict[str, Any]) -> str | None:
    host = profile.get("host", {})
    ssh_host = host.get("ssh")
    expected = host.get("expected_hostname")
    if ssh_host and expected and hostname() != str(expected):
        return str(ssh_host)
    return None


def _script(shell_command: str) -> str:
    return "set -Eeuo pipefail\n" + shell_command + "\n"


def run_profile(profile: dict[str, Any], command: Sequence[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    shell_command = runtime_shell(profile, command); target = remote_host(profile)
    if target:
        return subprocess.run(["ssh","-o","BatchMode=yes",target,"bash","-s"], input=_script(shell_command), text=True, check=check)
    return subprocess.run(["bash","-lc",shell_command], text=True, check=check)


def capture_profile(profile: dict[str, Any], command: Sequence[str], timeout: int = 30) -> tuple[int, str]:
    shell_command = runtime_shell(profile, command); target = remote_host(profile)
    try:
        if target:
            proc=subprocess.run(["ssh","-o","BatchMode=yes",target,"bash","-s"],input=_script(shell_command),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        else:
            proc=subprocess.run(["bash","-lc",shell_command],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        return proc.returncode,proc.stdout
    except (OSError,subprocess.TimeoutExpired) as exc:
        return 127,str(exc)


def printable_run(profile: dict[str, Any], command: Sequence[str]) -> str:
    shell_command=runtime_shell(profile,command); target=remote_host(profile)
    if target:
        return f"ssh -o BatchMode=yes {target} 'bash -s' <<'ACCEL'\n{_script(shell_command)}ACCEL"
    return shell_join(["bash","-lc",shell_command])
