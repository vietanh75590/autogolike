# Chạy trên điện thoại Android bằng Termux

Cài Termux từ [F-Droid](https://f-droid.org/packages/com.termux/). Hướng dẫn này dành cho Android, không áp dụng cho iPhone.

## Cài lần đầu

Mở Termux và chạy lần lượt:

```bash
pkg update -y
pkg install -y git
cd ~
git clone https://github.com/vietanh75590/autogolike.git
cd autogolike
bash install_termux.sh
bash run.sh
```

Nếu đã có thư mục `~/autogolike` được clone từ GitHub, dùng phần cập nhật bên dưới thay vì clone lại. Nên đặt dự án trong thư mục home của Termux, không chạy từ `/sdcard`.

Bot chỉ cần Python 3.9+ và thư viện chuẩn. Không cần pip, Rust, `cryptography`, `golike-gauth`, ứng dụng Termux:API hay quyền truy cập bộ nhớ chung.

Lần đầu, chương trình yêu cầu token Golike của chính bạn (ẩn khi nhập), nền tảng và tài khoản đã liên kết. Chuẩn bị token từ phiên đăng nhập của bạn; chương trình không tự đăng nhập hoặc tự lấy token. Token được lưu trong `config.json` cạnh file Python, kể cả khi chạy từ thư mục khác. Không chia sẻ file này. `config.example.json` chỉ là cấu hình mẫu, không cần chép đè vào cấu hình cá nhân.

## Chạy những lần sau

```bash
cd ~/autogolike
bash run.sh
```

Đổi token, tài khoản hoặc cài đặt:

```bash
bash ~/autogolike/run.sh --config
```

Dừng bằng Ctrl+C (phím CTRL trên thanh phím Termux, hoặc Volume Down+C). Có thể kiểm tra cách dùng mà không gọi API:

```bash
bash ~/autogolike/run.sh --help
```

## Cập nhật

Dừng bot trước, rồi chạy:

```bash
cd ~/autogolike
git pull --ff-only origin main
bash install_termux.sh
bash run.sh
```

Lệnh cập nhật giữ `config.json` cá nhân vì file này được Git bỏ qua. Nếu Git báo file sửa cục bộ, giữ bản sao và xử lý thay đổi đó trước; không dùng reset để xóa cấu hình.

## Khi gặp lỗi

- `python: command not found`: chạy lại `bash install_termux.sh`.
- Không mở được liên kết: mở thủ công link in trên màn hình; kiểm tra ứng dụng tương ứng đã cài và cho phép mở liên kết trong cài đặt Android. Bot thử `termux-open-url` rồi Android `am start`.
- Android dừng Termux khi chuyển ứng dụng: cho phép Termux chạy nền và đặt pin thành Không hạn chế. Bot thử giữ wake lock khi chạy và nhả khi thoát bình thường; Android vẫn có thể dừng tiến trình.
- HTTP 0: kiểm tra Internet, ngày giờ máy và chứng chỉ; không tắt xác minh TLS.
- HTTP 401/403 hoặc token hết hạn: chạy `bash run.sh --config` để nhập lại token. Lỗi giới hạn phiên bản, captcha hoặc từ chối API cần được giải quyết với dịch vụ Golike.

Mở liên kết không tự thực hiện thao tác like/follow trên ứng dụng. Mã hiện tại không giải captcha hoặc tạo chữ ký `g-auth`. Khả năng nhận nhiệm vụ/nhận thưởng phụ thuộc API và tài khoản; không được đảm bảo chỉ bằng việc cài thành công trên Termux.
