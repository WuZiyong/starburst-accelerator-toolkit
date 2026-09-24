from __future__ import annotations

import json
import os
import shlex
import shutil
import socket
import subprocess
from typing import Any, Sequence


def which(name: str) -> str | None:
    return shutil.which(name)


def hostname() -> str:
    return socket.gethostname().split(".")[0]


def shell_join(command: Sequence[str]) -> str:
    return shlex.join([str(x) for x in command])


def run_capture(command: Sequence[str], timeout: int = 20, env: dict[str, str] | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, env=env)
        return proc.returncode, proc.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)


def emit_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def env_with_path_prefix(prefix: str) -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = prefix + ":" + env.get("PATH", "")
    return env
