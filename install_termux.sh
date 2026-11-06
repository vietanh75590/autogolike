#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if ! command -v pkg >/dev/null 2>&1; then
    echo "Script này dành cho Termux trên Android. Trên máy tính cài Python 3.9+ rồi chạy bash run.sh."
    exit 1
fi
pkg update -y
pkg install -y python termux-tools ca-certificates
# Chỉ dùng thư viện chuẩn; không cần pip, Rust hoặc Termux:API.
python -c 'import ssl, urllib.request; print("Python và TLS sẵn sàng:", ssl.OPENSSL_VERSION)'
python golike_bot.py --help >/dev/null
echo "Cài đặt hoàn tất. Chạy: bash run.sh"
