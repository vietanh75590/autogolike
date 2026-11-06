#!/data/data/com.termux/files/usr/bin/bash
echo "=========================================================="
echo "    CÀI ĐẶT MÔI TRƯỜNG CHO GOLIKE AUTO BOT TRÊN TERMUX"
echo "=========================================================="

pkg update -y
# Cài đặt python và python-cryptography bản dựng sẵn của Termux (tránh lỗi build rust)
pkg install -y python python-cryptography termux-api termux-tools libffi openssl

pip install --upgrade pip
pip install requests colorama golike-gauth

echo "=========================================================="
echo "    CÀI ĐẶT THÀNH CÔNG!"
echo "    Khởi động bot: python golike_bot.py"
echo "=========================================================="
