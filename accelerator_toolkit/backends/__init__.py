from __future__ import annotations

from . import cuda, dcu, rocm

_BACKENDS = {"cuda": cuda, "dcu": dcu, "rocm": rocm}


def get_backend(name: str):
    try:
        return _BACKENDS[name.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported backend: {name}") from exc
