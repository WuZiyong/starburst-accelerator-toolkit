#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV="${ACCEL_TOOLKIT_ENV:-${HOME}/.local/share/accelerator-toolkit/venv}"
BIN="${HOME}/.local/bin"
PYTHON="${ACCEL_BOOTSTRAP_PYTHON:-python3}"
mkdir -p "$(dirname "$ENV")" "$BIN"
if [[ ! -x "$ENV/bin/python" ]]; then "$PYTHON" -m venv --system-site-packages "$ENV"; fi
if ! "$ENV/bin/python" -c 'import yaml' >/dev/null 2>&1; then "$ENV/bin/python" -m pip install 'PyYAML>=6'; fi
"$ENV/bin/python" -m pip install --no-build-isolation --no-deps -e "$ROOT"
ln -sfn "$ENV/bin/accel" "$BIN/accel"
echo "Installed accel -> $BIN/accel"
echo "Ensure $BIN is on PATH."
