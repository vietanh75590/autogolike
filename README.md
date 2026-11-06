# Golike Auto Bot - Tự Động Lấy Nhiệm Vụ & Nhận Thưởng

Tool bot tự động hóa làm nhiệm vụ Golike đa nền tảng (TikTok, Instagram, Facebook, YouTube, Threads, Twitter).

---

## ✨ Tính năng nổi bật

1. **Tự động lấy nhiệm vụ (Auto Get Jobs)**:
   - Tự động kết nối tới hệ thống Golike và lấy nhiệm vụ mới nhất của tài khoản đã chọn.
   - Hỗ trợ đầy đủ: TikTok, Instagram, Facebook, YouTube, Threads, Twitter / X.

2. **Tùy chỉnh thời gian chờ nhận thưởng (Custom Claim Delay)**:
   - Tự do cài đặt số giây chờ trước khi bấm nhận thưởng (ví dụ: `15` giây, `20` giây).
   - Hỗ trợ dải thời gian ngẫu nhiên (ví dụ: `15-25` giây) giúp hành vi giống người dùng thật, tránh bị khóa nick.
   - Đồng hồ đếm ngược trực tiếp trên màn hình console.

3. **Tự động bấm nhận thưởng (Auto Claim Reward)**:
   - Tự động tạo chữ ký bảo mật (`sig` / `g-auth`) và tự động giải captcha dạng kéo thả (drag geometry captcha) với thư viện `golike-gauth`.
   - Tự động retry (thử lại) nếu hệ thống báo chưa xong nhiệm vụ.
   - Tự động skip/bỏ qua nhiệm vụ nếu gặp lỗi hoặc tài khoản mục tiêu bị khóa.

4. **Tùy chọn mở link tự động**:
   - Tự động mở liên kết nhiệm vụ (video, trang cá nhân, bài viết...) trên trình duyệt nếu muốn làm thật bằng tay/script.

5. **Lưu cấu hình thông minh**:
   - Lưu cấu hình vào `config.json`. Các lần chạy tiếp theo chỉ cần mở lên là chạy ngay, không cần nhập lại token hay thiết lập lại.

6. **Báo cáo & Thống kê**:
   - Thống kê chi tiết: số tiền kiếm được (+VNĐ), số nhiệm vụ thành công, thất bại, đã bỏ qua, thời gian bot chạy.

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Cài đặt thư viện phụ thuộc (nếu chưa có)
Mở cửa sổ dòng lệnh (Terminal/PowerShell) tại thư mục này và chạy:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy bot
- **Cách 1**: Nhấp đúp vào file [`run.bat`](file:///e:/mon%20t5/autogolike/run.bat).
- **Cách 2**: Chạy lệnh qua PowerShell hoặc Command Prompt:
  ```bash
  python golike_bot.py
  ```

---

## 🔑 Hướng dẫn lấy Golike Authorization Token

1. Dùng trình duyệt (Chrome, Edge, Cốc Cốc...) truy cập vào: **https://app.golike.net**
2. Đăng nhập tài khoản Golike của bạn.
3. Nhấn phím **F12** (hoặc chuột phải -> chọn **Inspect / Kiểm tra**).
4. Chọn tab **Network** (Mạng).
5. Tải lại trang (nhấn **F5**) hoặc bấm vào mục bất kỳ trên trang.
6. Trong ô lọc (Filter), nhập: `me` hoặc `users`.
7. Nhấn vào yêu cầu `me` -> nhìn sang khung bên phải ở mục **Headers** -> cuộn xuống **Request Headers**.
8. Tìm dòng:
   ```text
   authorization: Bearer eyJhbGciOiJIUzI1NiIsIn...
   ```
9. Sao chép toàn bộ chuỗi token (từ đoạn `eyJhbGci...` hoặc cả dòng `Bearer eyJ...`) rồi dán vào tool khi được hỏi.

---

## ⚙️ Các tham số chạy tự động (Dành cho dòng lệnh / Schedule)

Bạn có thể chạy bot trực tiếp với các tham số mà không cần qua menu:
```bash
# Chạy với TikTok, delay nhận thưởng 20 giây, nghỉ giữa các job 5 giây:
python golike_bot.py --platform tiktok --delay 20 --interval 5

# Chạy tối đa 50 nhiệm vụ rồi tự dừng:
python golike_bot.py --delay 15 --max-jobs 50

# Chạy mở link trên trình duyệt tự động:
python golike_bot.py --delay 15 --open-link
```
