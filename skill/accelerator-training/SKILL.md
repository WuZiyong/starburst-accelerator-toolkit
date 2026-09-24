# Accelerator Training Skill

Use this workflow when a user asks to run, migrate, validate, submit, resume, or benchmark machine-learning training on CUDA, Hygon DCU/DTK, ROCm, or an HPC scheduler.

## Core rule

Treat accelerator migration as an execution-layer change. Do not silently change scientific data splits, model architecture, target, optimizer, seeds, checkpoint semantics, precision policy, or effective batch size.

## Workflow

1. Read the repository's `.accelerator.yaml` if present and resolve the requested/default profile.
2. Run `accel doctor --profile <profile>` before changing or launching training.
3. If the framework environment is new, run `accel validate --profile <profile> --grid 64`, then the largest relevant grid.
4. Run a project-owned real-model forward/backward smoke test before production training.
5. For a backend migration, compare a short identical-data/identical-seed run against the known backend. Record loss, gradient norm, output statistics, runtime, and peak memory.
6. Preserve effective batch size. If memory requires a smaller microbatch, use gradient accumulation rather than silently changing the optimization protocol.
7. Prefer scheduler submission for production jobs. Direct SSH execution is for diagnostics and bounded smoke tests only.
8. Record the resolved profile, toolkit version/commit, framework version, accelerator name, command, project commit, and output/log paths.

## Hygon DCU notes

Use a DTK-matched Hygon PyTorch build; do not reuse an NVIDIA CUDA wheel. Hygon PyTorch commonly exposes the accelerator through the `torch.cuda` API, so CUDA-named Python calls are not by themselves evidence of incompatibility. Validate actual operators used by the project.

## Multi-device policy

Benchmark one device first. Prefer independent seeds/experiments across devices when that preserves the scientific protocol and avoids communication overhead. Add DDP only after measuring single-device throughput and topology; do not assume linear scaling.

## Failure handling

If hardware inventory, scheduler GRES, or device visibility disagree, stop production launch and report the mismatch. Do not compensate by expanding device visibility outside an allocation.
