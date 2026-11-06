# Golike Bot

Chương trình Python lấy nhiệm vụ, mở liên kết và gửi yêu cầu nhận thưởng qua API Golike. Hỗ trợ lựa chọn TikTok, Instagram, Facebook, YouTube, Threads và Twitter/X; khả năng hoạt động thực tế phụ thuộc API và tài khoản.

## Điện thoại Android

Xem [hướng dẫn Termux](README_TERMUX.md) để cài trực tiếp từ GitHub, chạy và cập nhật. Không cần cài thư viện pip.

```bash
pkg update -y
pkg install -y git
cd ~
git clone https://github.com/vietanh75590/autogolike.git
cd autogolike
bash install_termux.sh
bash run.sh
```

Nếu đã clone trước đó, xem mục cập nhật trong hướng dẫn Termux.

## Máy tính

Cài Python 3.9+ rồi chạy `python golike_bot.py`. Windows có thể mở `run.bat`; Linux dùng `bash run.sh`.

Lần đầu nhập token từ phiên đăng nhập Golike của chính bạn và chọn tài khoản đã liên kết. Cấu hình được lưu vào `config.json` cạnh mã nguồn, được Git bỏ qua. Token được ẩn lúc nhập; không tải cấu hình cá nhân lên GitHub.

```bash
python golike_bot.py --help
python golike_bot.py --config
# Các tùy chọn sau áp dụng khi đã cấu hình tài khoản:
python golike_bot.py --delay 20 --interval 5 --max-jobs 50 --open-link
```

Dừng bằng Ctrl+C. Mở link không tự thực hiện like/follow. Mã hiện tại không giải captcha hay tạo chữ ký `g-auth`; máy chủ có thể từ chối yêu cầu. Không có cam kết nhận thưởng hoặc tránh giới hạn tài khoản.

## Kiểm tra cục bộ

```bash
python -m unittest discover -s tests -v
bash run.sh --help
```

Các kiểm tra cục bộ không sử dụng token và không gửi yêu cầu nhận thưởng thật.
