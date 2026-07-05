#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"
PYTHON_BOOTSTRAP="${PYTHON_BOOTSTRAP:-}"

if [[ -z "${PYTHON_BOOTSTRAP}" ]]; then
  if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BOOTSTRAP="python3.11"
  else
    PYTHON_BOOTSTRAP="python3"
  fi
fi

if [[ -x "${PYTHON}" ]]; then
  if ! "${PYTHON}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "Existing .venv uses Python $("${PYTHON}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'), but this project requires Python >= 3.11." >&2
    echo "Remove .venv and rerun this script, or set PYTHON_BOOTSTRAP to a Python 3.11+ executable." >&2
    exit 1
  fi
else
  "${PYTHON_BOOTSTRAP}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
    echo "${PYTHON_BOOTSTRAP} is not Python >= 3.11. Install Python 3.11+ or set PYTHON_BOOTSTRAP=/path/to/python3.11." >&2
    exit 1
  }
  "${PYTHON_BOOTSTRAP}" -m venv "${PROJECT_ROOT}/.venv"
fi

"${PYTHON}" -m pip install --upgrade pip
"${PYTHON}" -m pip install -r "${PROJECT_ROOT}/requirements.txt"
"${PYTHON}" -m pip install -e "${PROJECT_ROOT}" --no-deps
