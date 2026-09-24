from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

TOOLKIT_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def find_project_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".accelerator.yaml").exists() or (candidate / ".git").exists():
            return candidate
    return here


def load_project_config(start: Path | None = None) -> tuple[Path, dict[str, Any]]:
    root = find_project_root(start)
    path = root / ".accelerator.yaml"
    return root, load_yaml(path) if path.exists() else {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out

def resolve_profile(name: str | None = None, start: Path | None = None) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    project_root, project = load_project_config(start)
    selected = name or project.get("default_profile")
    if not selected:
        raise ValueError("No profile selected. Pass --profile or add default_profile to .accelerator.yaml")

    candidate = Path(str(selected)).expanduser()
    if candidate.exists():
        path = candidate.resolve()
        profile_name = path.stem
    else:
        rel = str(selected)
        if not rel.endswith(".yaml"):
            rel += ".yaml"
        path = (TOOLKIT_ROOT / "profiles" / rel).resolve()
        profile_name = str(selected).removesuffix(".yaml")
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {selected} -> {path}")

    profile = load_yaml(path)
    overrides = project.get("profile_overrides", {}).get(profile_name, {})
    if overrides:
        profile = deep_merge(profile, overrides)
    profile["_profile_name"] = profile_name
    profile["_profile_path"] = str(path)
    profile["_project_root"] = str(project_root)
    return project_root, profile, project


def profile_python(profile: dict[str, Any]) -> str:
    runtime = profile.get("runtime", {})
    return str(runtime.get("python") or "python")
