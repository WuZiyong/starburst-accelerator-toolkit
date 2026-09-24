from __future__ import annotations

import argparse, json, platform, time
import torch


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument('--grid',type=int,default=64,choices=(32,64,128)); p.add_argument('--channels',type=int,default=8); a=p.parse_args()
    if not torch.cuda.is_available(): raise RuntimeError('Accelerator backend is not available through torch.cuda')
    count=torch.cuda.device_count()
    if count < 1: raise RuntimeError('No accelerator devices visible')
    torch.manual_seed(20260924); torch.cuda.manual_seed_all(20260924); torch.cuda.reset_peak_memory_stats()
    d=torch.device('cuda:0')
    model=torch.nn.Sequential(torch.nn.Conv3d(4,a.channels,3,padding=1),torch.nn.SiLU(),torch.nn.Conv3d(a.channels,1,3,padding=1)).to(d)
    opt=torch.optim.AdamW(model.parameters(),lr=1e-4)
    x=torch.randn(1,4,a.grid,a.grid,a.grid,device=d); y=torch.randn(1,1,a.grid,a.grid,a.grid,device=d)
    torch.cuda.synchronize(); start=time.monotonic(); opt.zero_grad(set_to_none=True); loss=(model(x)-y).square().mean(); loss.backward(); opt.step(); torch.cuda.synchronize()
    result={'status':'PASS','python':platform.python_version(),'torch':torch.__version__,'torch_cuda':torch.version.cuda,'torch_hip':getattr(torch.version,'hip',None),'visible_devices':count,'device0':torch.cuda.get_device_name(0),'grid':a.grid,'loss':float(loss.detach().cpu()),'step_seconds':time.monotonic()-start,'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'peak_reserved_gib':torch.cuda.max_memory_reserved()/2**30}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
