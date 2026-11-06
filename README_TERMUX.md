# Hướng Dẫn Chạy Golike Auto Bot Trên Điện Thoại (Bản Zero Dependencies)

Bản cập nhật này được viết bằng **100% thư viện chuẩn có sẵn của Python** (`urllib`, `base64`, `json`):
* ❌ **KHÔNG CẦN** `pip install colorama` (Đã có sẵn bộ màu ANSI tích hợp).
* ❌ **KHÔNG CẦN** `pip install requests`.
* ❌ **KHÔNG CẦN** `pip install cryptography` (Không lo lỗi build Rust / C).
* ❌ **KHÔNG CẦN** `golike-gauth`.
* ✅ **Mở lên là chạy ngay 100% out of the box!**

---

## 🚀 Cách chạy trên Termux (Chỉ 2 dòng lệnh):

Trên màn hình Termux hiện tại của bạn (`~/autogolike $`), chỉ cần gõ đúng 2 lệnh này:

```bash
# 1. Cập nhật file bot mới nhất vào thư mục Termux:
cp -f /sdcard/Download/autogolike/golike_bot.py ~/autogolike/

# 2. Khởi động bot ngay:
python golike_bot.py
```

---

## ⚡ Các tính năng tự động:
1. **Không hỏi lại**: Khi đã có cấu hình, bot tự động chạy ngay sau 1 giây, không bắt bạn chọn Menu 1/2/3.
2. **Auto Submit**: Tự đếm ngược thời gian chờ và tự động gửi yêu cầu nhận tiền thưởng.
3. **Tự động mở App**: Tự mở TikTok / Facebook / Instagram trên điện thoại.
4. **Nếu muốn đổi cấu hình / nick**: Chỉ cần chạy `python golike_bot.py --config`.
