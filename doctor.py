from __future__ import annotations

import subprocess
from typing import Any

from accelerator_toolkit.backends import get_backend
from accelerator_toolkit.util import hostname, run_capture


def _remote_probe(profile: dict[str, Any]) -> dict[str, Any] | None:
    host=profile.get('host',{}); ssh_host=host.get('ssh'); expected=host.get('expected_hostname')
    if not ssh_host or not expected or hostname()==str(expected): return None
    backend=str(profile.get('backend')); runtime=profile.get('runtime',{})
    if backend=='dcu':
        root=str(runtime.get('dtk_root') or '/opt/dtk'); pci=str(profile.get('hardware',{}).get('pci_id') or '1d94:54b7')
        shell=f'source "{root}/env.sh"\nexport PATH="/sbin:/usr/sbin:$PATH"\necho HOST=$(hostname)\n"{root}/bin/hy-smi" --showmeminfo vram\necho PCI_COUNT=$(/sbin/lspci -nn | grep -c "{pci}" || true)'
    elif backend=='cuda':
        shell='echo HOST=$(hostname)\nnvidia-smi -L\nnvidia-smi --query-gpu=name,memory.total --format=csv,noheader'
    elif backend=='rocm':
        root=str(runtime.get('rocm_root') or '/opt/rocm'); shell=f'echo HOST=$(hostname)\n"{root}/bin/rocm-smi"'
    else: return None
    try:
        proc=subprocess.run(['ssh','-o','BatchMode=yes',str(ssh_host),'bash','-s'],input='set -Eeuo pipefail\n'+shell+'\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        rc,out=proc.returncode,proc.stdout
    except (OSError,subprocess.TimeoutExpired) as exc:
        rc,out=127,str(exc)
    status='PASS' if rc==0 else 'FAIL'
    result={'check':'remote_hardware','status':status,'host':str(ssh_host),'output':out.strip()}
    if backend=='dcu' and rc==0:
        import re
        match=re.search(r'PCI_COUNT=(\\d+)',out); visible=int(match.group(1)) if match else None
        configured=profile.get('hardware',{}).get('configured_devices')
        result.update({'visible_devices':visible,'configured_devices':configured})
        if visible is not None and configured is not None and visible != int(configured): result['status']='WARN'
    return result

def doctor(profile: dict[str, Any]) -> list[dict[str, Any]]:
    checks=[]; remote=_remote_probe(profile)
    if remote is not None: checks.append(remote)
    else: checks.extend(get_backend(str(profile['backend'])).doctor(profile))
    scheduler=profile.get('scheduler',{})
    if scheduler.get('type')=='slurm':
        node=profile.get('host',{}).get('expected_hostname')
        if node:
            rc,out=run_capture(['scontrol','show','node',str(node)],timeout=10)
            state=next((part.split('=',1)[1] for part in out.replace('\n',' ').split() if part.startswith('State=')),None)
            status='PASS' if rc==0 and state and not state.startswith('DOWN') else 'WARN'
            checks.append({'check':'slurm_node','status':status,'node':node,'state':state,'output':out.strip()})
    return checks
