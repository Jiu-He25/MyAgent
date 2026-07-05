#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
  echo "Project virtual environment not found. Run scripts/setup_env.sh first." >&2
  exit 1
fi

cd "${PROJECT_ROOT}"
"${PYTHON}" -m apps.cli.main "$@"
