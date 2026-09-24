# Accelerator Toolkit

`starburst-accelerator-toolkit` is a portable accelerator and HPC training toolkit. **Starburst is the first deployment profile, not a hard-coded target.**

The toolkit separates four concerns:

- **backend** — NVIDIA CUDA, Hygon DCU/DTK, AMD ROCm, CPU;
- **scheduler** — direct/local execution, Slurm, and future PBS support;
- **profile** — machine-specific paths, partitions, GRES and environment details;
- **project config** — a tiny `.accelerator.yaml` stored with each scientific repository.

This keeps scientific training code independent of a specific cluster whenever the framework API is compatible.

## Commands

```bash
accel detect
accel doctor --profile starburst/comput2-dcu
accel validate --profile starburst/comput2-dcu --grid 128
accel run --profile starburst/comput2-dcu -- python train.py
accel submit --profile starburst/comput2-dcu --dry-run -- python train.py
```

## Project-level configuration

A scientific repository only needs a small `.accelerator.yaml`:

```yaml
default_profile: starburst/comput1-cuda
profiles:
  - starburst/comput1-cuda
  - starburst/comput2-dcu
training:
  command: [python, train.py]
```

Then `accel doctor`, `accel validate`, `accel run`, and `accel submit` can infer the default profile from the current repository.

## Design rule

Profiles may contain machine-specific details; backend and scheduler code must not contain Starburst-specific paths. Accelerator migration must not silently change model architecture, scientific split, seed, optimizer, effective batch size, or checkpoint semantics.

## Install

```bash
git clone git@github.com:WuZiyong/starburst-accelerator-toolkit.git
cd starburst-accelerator-toolkit
scripts/bootstrap.sh
```

The bootstrap creates an isolated toolkit environment and places `accel` in `~/.local/bin`.

See `skill/accelerator-training/SKILL.md` for the recommended Codex/agent workflow.
