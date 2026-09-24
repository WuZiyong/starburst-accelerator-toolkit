from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from accelerator_toolkit.backends import get_backend
from accelerator_toolkit.config import TOOLKIT_ROOT, resolve_profile
from accelerator_toolkit.detect import detect_backends
from accelerator_toolkit.doctor import doctor
from accelerator_toolkit.execution import capture_profile, printable_run, run_profile
from accelerator_toolkit.schedulers import slurm
from accelerator_toolkit.util import emit_json


def _command(values: list[str]) -> list[str]:
    if values and values[0] == "--": values = values[1:]
    if not values: raise ValueError("A command is required after --")
    return values


def _profile(args):
    return resolve_profile(args.profile)[1]


def cmd_detect(args) -> int:
    emit_json(detect_backends()); return 0


def cmd_doctor(args) -> int:
    profile=_profile(args); checks=doctor(profile); emit_json({"profile":profile["_profile_name"],"checks":checks})
    return 1 if any(x.get("status") == "FAIL" for x in checks) else 0


def cmd_env(args) -> int:
    profile=_profile(args); backend=get_backend(str(profile["backend"])); print("\n".join(backend.shell_prelude(profile))); return 0


def cmd_validate(args) -> int:
    profile=_profile(args); smoke=str(TOOLKIT_ROOT/"accelerator_toolkit"/"smoke.py"); python=str(profile.get("runtime",{}).get("python") or "python")
    rc,out=capture_profile(profile,[python,smoke,"--grid",str(args.grid)],timeout=args.timeout); print(out,end="" if out.endswith("\n") else "\n"); return rc

def cmd_run(args) -> int:
    profile=_profile(args); command=_command(args.command)
    if args.dry_run: print(printable_run(profile,command)); return 0
    return run_profile(profile,command).returncode


def cmd_submit(args) -> int:
    profile=_profile(args); command=_command(args.command); scheduler=profile.get("scheduler",{}).get("type")
    if scheduler != "slurm": raise ValueError(f"submit currently supports slurm profiles, got {scheduler!r}")
    rc,out=slurm.submit(profile,command,dry_run=args.dry_run); print(out,end="" if out.endswith("\n") else "\n"); return rc


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="accel",description="Portable accelerator and HPC training toolkit")
    sub=p.add_subparsers(dest="subcommand",required=True)
    d=sub.add_parser("detect"); d.set_defaults(func=cmd_detect)
    for name,func in (("doctor",cmd_doctor),("env",cmd_env)):
        q=sub.add_parser(name); q.add_argument("--profile"); q.set_defaults(func=func)
    v=sub.add_parser("validate"); v.add_argument("--profile"); v.add_argument("--grid",type=int,default=64,choices=(32,64,128)); v.add_argument("--timeout",type=int,default=120); v.set_defaults(func=cmd_validate)
    r=sub.add_parser("run"); r.add_argument("--profile"); r.add_argument("--dry-run",action="store_true"); r.add_argument("command",nargs=argparse.REMAINDER); r.set_defaults(func=cmd_run)
    s=sub.add_parser("submit"); s.add_argument("--profile"); s.add_argument("--dry-run",action="store_true"); s.add_argument("command",nargs=argparse.REMAINDER); s.set_defaults(func=cmd_submit)
    return p


def main() -> None:
    try:
        args = parser().parse_args()
        code = args.func(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"accel: {exc}", file=sys.stderr)
        code = 2
    raise SystemExit(code)

if __name__=="__main__": main()
