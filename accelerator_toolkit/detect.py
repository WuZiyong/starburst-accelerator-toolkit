from __future__ import annotations

from accelerator_toolkit.backends import cuda, dcu, rocm


def detect_backends() -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    probes = [("cuda", cuda.detect), ("dcu", dcu.detect), ("rocm", rocm.detect)]
    for name, probe in probes:
        try:
            available = bool(probe())
            error = None
        except Exception as exc:
            available = False
            error = repr(exc)
        found.append({"backend": name, "available": available, "error": error})
    return found
