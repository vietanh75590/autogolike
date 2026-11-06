#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if command -v python3 >/dev/null 2>&1; then
    exec python3 golike_bot.py "$@"
elif command -v python >/dev/null 2>&1; then
    exec python golike_bot.py "$@"
else
    echo "Chưa có Python. Trên Termux chạy: bash install_termux.sh" >&2
    exit 1
fi
