"""
Golike Auto Bot - Tự động nhận nhiệm vụ và tự động nộp/nhận thưởng (Auto Submit)
Tối ưu hóa chạy 100% ĐỘC LẬP trên điện thoại Android (Termux) và máy tính (Windows/Linux).
KHÔNG yêu cầu cài thêm thư viện ngoài (Zero external dependencies) - Chạy ngay với Python gốc.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import getpass
import json
import os
import random
import shutil
import ssl
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser
from typing import Any, Dict, List, Optional, Tuple

# Hỗ trợ màu sắc ANSI trên Termux / Windows Terminal mà không cần thư viện colorama
class Fore:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


class Style:
    BRIGHT = "\033[1m"
    DIM = "\033[2m"
    RESET_ALL = "\033[0m"


CONFIG_FILE = str(Path(__file__).resolve().with_name("config.json"))
BASE_API = "https://gateway.golike.net/api"
APP_VERSION = "26.10.27.1"
APP_CLIENT = "109096667105508"
MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
)

PLATFORMS = {
    "1": {
        "key": "tiktok",
        "name": "TikTok",
        "account_endpoint": "/tiktok-account",
        "jobs_endpoint": "/advertising/publishers/tiktok/jobs",
        "complete_endpoint": "/advertising/publishers/tiktok/complete-jobs",
        "skip_endpoint": "/advertising/publishers/tiktok/skip-jobs",
        "name_field": ["unique_username", "nickname", "username", "id"],
    },
    "2": {
        "key": "instagram",
        "name": "Instagram",
        "account_endpoint": "/instagram-account",
        "jobs_endpoint": "/advertising/publishers/instagram/jobs",
        "complete_endpoint": "/advertising/publishers/instagram/complete-jobs",
        "skip_endpoint": "/advertising/publishers/instagram/skip-jobs",
        "name_field": ["instagram_username", "username", "nickname", "id"],
    },
    "3": {
        "key": "facebook",
        "name": "Facebook",
        "account_endpoint": "/facebook-account",
        "jobs_endpoint": "/advertising/publishers/facebook/jobs",
        "complete_endpoint": "/advertising/publishers/facebook/complete-jobs",
        "skip_endpoint": "/advertising/publishers/facebook/skip-jobs",
        "name_field": ["name", "fb_id", "username", "id"],
    },
    "4": {
        "key": "youtube",
        "name": "YouTube",
        "account_endpoint": "/youtube-account",
        "jobs_endpoint": "/advertising/publishers/youtube/jobs",
        "complete_endpoint": "/advertising/publishers/youtube/complete-jobs",
        "skip_endpoint": "/advertising/publishers/youtube/skip-jobs",
        "name_field": ["name", "channel_id", "username", "id"],
    },
    "5": {
        "key": "threads",
        "name": "Threads",
        "account_endpoint": "/threads-account",
        "jobs_endpoint": "/advertising/publishers/threads/jobs",
        "complete_endpoint": "/advertising/publishers/threads/complete-jobs",
        "skip_endpoint": "/advertising/publishers/threads/skip-jobs",
        "name_field": ["threads_username", "username", "id"],
    },
    "6": {
        "key": "twitter",
        "name": "Twitter / X",
        "account_endpoint": "/twitter-account",
        "jobs_endpoint": "/advertising/publishers/twitter/jobs",
        "complete_endpoint": "/advertising/publishers/twitter/complete-jobs",
        "skip_endpoint": "/advertising/publishers/twitter/skip-jobs",
        "name_field": ["twitter_username", "screen_name", "username", "id"],
    },
}


def triple_btoa(ts: Optional[int] = None) -> str:
    """Tạo header 't' của Golike bằng base64 mã hóa 3 lần."""
    if ts is None:
        ts = int(time.time())
    x = str(ts).encode("utf-8")
    for _ in range(3):
        x = base64.b64encode(x)
    return x.decode("ascii")


def make_headers(token: str, device_id: Optional[str] = None) -> Dict[str, str]:
    did = device_id or str(uuid.uuid4())
    jwt = token.strip()
    if jwt.lower().startswith("bearer "):
        jwt = jwt[7:].strip()
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "vi,en-US;q=0.9,en;q=0.8",
        "authorization": f"Bearer {jwt}",
        "content-type": "application/json;charset=utf-8",
        "origin": "https://app.golike.net",
        "referer": "https://app.golike.net/",
        "user-agent": MOBILE_UA,
        "g-device-id": did,
        "g-version": os.environ.get("GOLIKE_APP_VERSION", APP_VERSION),
        "g-client": os.environ.get("GOLIKE_APP_CLIENT", APP_CLIENT),
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "t": triple_btoa(),
    }


def http_request(
    method: str,
    path: str,
    token: str,
    device_id: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Any = None,
    timeout: float = 30,
) -> Tuple[int, Dict[str, Any], str]:
    """Gửi yêu cầu HTTP thuần bằng urllib (không phụ thuộc requests/urllib3)."""
    url = path if path.startswith("http") else f"{BASE_API}{path if path.startswith('/') else '/' + path}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}{'&' if '?' in url else '?'}{query_string}"

    headers = make_headers(token, device_id)
    body_bytes = None
    if json_data is not None:
        body_bytes = json.dumps(json_data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.status
            raw_text = response.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw_text)
            except Exception:
                data = {}
            return status_code, data if isinstance(data, dict) else {}, raw_text
    except urllib.error.HTTPError as e:
        raw_text = e.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw_text)
        except Exception:
            data = {}
        return e.code, data if isinstance(data, dict) else {}, raw_text
    except Exception as e:
        return 0, {}, str(e)


def is_termux_env() -> bool:
    return (
        "TERMUX_VERSION" in os.environ
        or os.path.exists("/data/data/com.termux")
        or os.path.exists("/system/bin/am")
    )


def open_job_url(url: str) -> bool:
    """Tự động mở link vào ứng dụng tương ứng trên Android."""
    if not url:
        return False

    if is_termux_env():
        try:
            res = subprocess.run(
                ["termux-open-url", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            if res.returncode == 0:
                return True
        except Exception:
            pass

        try:
            res = subprocess.run(
                ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            if res.returncode == 0:
                return True
        except Exception:
            pass

    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False


def set_wake_lock(enable: bool = True) -> None:
    if is_termux_env():
        cmd = "termux-wake-lock" if enable else "termux-wake-unlock"
        try:
            subprocess.run([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        except Exception:
            pass


def log_time() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def print_banner() -> None:
    env_name = "TERMUX (ANDROID)" if is_termux_env() else "WINDOWS / LINUX"
    print(Fore.CYAN + "=" * 54)
    print(Fore.GREEN + Style.BRIGHT + "       GOLIKE AUTO BOT - AUTO JOB & SUBMIT")
    print(Fore.YELLOW + f"       Môi trường: {env_name} (Zero Dependencies)")
    print(Fore.YELLOW + "       Tự Động Lấy Job -> Đếm Giờ -> Tự Bấm Nhận Thưởng")
    print(Fore.CYAN + "=" * 54)


class ConfigManager:
    @staticmethod
    def load() -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if not isinstance(cfg, dict):
                        raise ValueError("Cấu hình phải là một JSON object")
                    return cfg
            except Exception as e:
                print(f"{Fore.RED}[!] Lỗi đọc file {CONFIG_FILE}: {e}")
        return {}

    @staticmethod
    def save(cfg: Dict[str, Any]) -> None:
        try:
            fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                if os.name != "nt":
                    os.fchmod(f.fileno(), 0o600)
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            print(f"{Fore.GREEN}[OK] Đã lưu cấu hình vào {CONFIG_FILE}")
        except Exception as e:
            print(f"{Fore.RED}[!] Không thể lưu {CONFIG_FILE}: {e}")


class GolikeBot:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.token = config.get("token", "").strip().strip("'\"")
        if self.token.lower().startswith("bearer "):
            self.token = self.token[7:].strip()

        self.device_id = str(uuid.uuid4())
        self.platform_key = config.get("platform", "tiktok")
        self.account_id = config.get("account_id")
        self.account_name = config.get("account_name", "")
        self.claim_delay_min = int(config.get("claim_delay_min", 12))
        self.claim_delay_max = int(config.get("claim_delay_max", 15))
        self.job_interval = int(config.get("job_interval", 4))
        self.max_retries = int(config.get("max_retries", 3))
        self.retry_delay = int(config.get("retry_delay", 4))
        self.auto_open_link = bool(config.get("auto_open_link", True))
        self.auto_skip_failed = bool(config.get("auto_skip_failed", True))
        self.max_jobs = int(config.get("max_jobs", 0))

        # Thống kê
        self.total_completed = 0
        self.total_failed = 0
        self.total_skipped = 0
        self.total_earned = 0
        self.start_time = time.time()

        # Chọn platform
        self.plt_info = None
        for p in PLATFORMS.values():
            if p["key"] == self.platform_key:
                self.plt_info = p
                break
        if not self.plt_info:
            self.plt_info = PLATFORMS["1"]
            self.platform_key = self.plt_info["key"]

    def get_user_me(self) -> Dict[str, Any]:
        status, data, raw = http_request("GET", "/users/me", self.token, self.device_id)
        if status == 200 and (data.get("status") == 200 or data.get("success")):
            return data.get("data", {})
        raise ValueError(f"Xác thực thất bại (HTTP {status}): {data.get('message', raw)}")

    def get_accounts(self) -> List[Dict[str, Any]]:
        endpoint = self.plt_info["account_endpoint"]
        status, res, _ = http_request("GET", endpoint, self.token, self.device_id)
        if status == 200 and (res.get("status") == 200 or res.get("success")):
            accs = res.get("data", [])
            if isinstance(accs, list):
                return accs
        return []

    def get_job(self) -> Optional[Dict[str, Any]]:
        endpoint = self.plt_info["jobs_endpoint"]
        params = {"account_id": self.account_id}
        status, res, raw = http_request("GET", endpoint, self.token, self.device_id, params=params)

        if status == 200 and (res.get("status") == 200 or res.get("success")) and res.get("data"):
            return res["data"]
        else:
            msg = str(res.get("message") or res.get("error") or "Không có nhiệm vụ")
            normalized = msg.casefold()
            if "cập nhật phiên bản" in normalized or "bản web đã dừng" in normalized:
                raise ValueError(
                    f"Golike yêu cầu cập nhật client (HTTP {status}): {msg}\n"
                    "Đã dừng để tránh thử lại vô hạn. Thông báo này chưa chứng minh token sai "
                    "hoặc tài khoản bị giới hạn. Hãy thử lấy nhiệm vụ trên Golike chính thức.\n"
                    "Header hiện tại: g-version=" + os.environ.get("GOLIKE_APP_VERSION", APP_VERSION)
                    + "; g-client=" + os.environ.get("GOLIKE_APP_CLIENT", APP_CLIENT)
                    + ". Chỉ cấu hình lại bằng giá trị từ request chính thức đang hoạt động."
                )
            if status in (401, 403) or res.get("status") in (401, 403):
                raise ValueError(
                    f"Golike từ chối truy cập (HTTP {status}): {msg}. "
                    "Kiểm tra tài khoản trên Golike chính thức; nếu phiên hết hạn, chạy bash run.sh --config."
                )
            if status == 0:
                print(f"[{log_time()}] {Fore.YELLOW}[MẠNG] Không kết nối được Golike; kiểm tra Internet, ngày giờ và TLS.")
            else:
                print(f"[{log_time()}] {Fore.YELLOW}[HTTP {status}] {msg}{Style.RESET_ALL}")
            return None

    def submit_job(self, job: Dict[str, Any]) -> Tuple[bool, str, int]:
        endpoint = self.plt_info["complete_endpoint"]
        payload = {
            "account_id": self.account_id,
            "ads_id": job.get("id"),
            "async": True,
            "data": None,
        }
        status, res, raw = http_request("POST", endpoint, self.token, self.device_id, json_data=payload)
        if status == 200 and (res.get("status") == 200 or res.get("success")):
            data = res.get("data") or {}
            prices = data.get("prices") or data.get("price") or 0
            msg = res.get("message") or "Nhận thưởng thành công!"
            return True, msg, int(prices)
        else:
            msg = res.get("message") or res.get("error") or "Chưa hoàn thành"
            return False, msg, 0

    def skip_job(self, job: Dict[str, Any]) -> bool:
        endpoint = self.plt_info["skip_endpoint"]
        payload = {
            "ads_id": job.get("id"),
            "account_id": self.account_id,
            "object_id": job.get("object_id", ""),
            "type": job.get("type", ""),
        }
        status, res, _ = http_request("POST", endpoint, self.token, self.device_id, json_data=payload)
        return bool(status == 200 and (res.get("status") == 200 or res.get("success")))

    def countdown(self, seconds: int, text: str = "Chờ auto submit") -> None:
        for rem in range(seconds, 0, -1):
            sys.stdout.write(
                f"\r[{log_time()}] {Fore.YELLOW}⏳ [{text}] Còn: {rem:2d}s {Style.RESET_ALL}"
            )
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def run(self) -> None:
        print_banner()
        set_wake_lock(True)

        print(f"[{log_time()}] {Fore.CYAN}Khởi động Auto Bot:")
        print(f"  • Nền tảng : {Fore.GREEN}{self.plt_info['name']}")
        print(f"  • Tài khoản: {Fore.GREEN}{self.account_name} (ID: {self.account_id})")
        if self.claim_delay_min == self.claim_delay_max:
            print(f"  • Chờ submit: {Fore.YELLOW}{self.claim_delay_min}s (cố định)")
        else:
            print(f"  • Chờ submit: {Fore.YELLOW}{self.claim_delay_min}-{self.claim_delay_max}s (ngẫu nhiên)")
        print(f"  • Tự mở App : {Fore.YELLOW}{'Bật (am start)' if self.auto_open_link else 'Tắt'}")
        print(f"  • Auto Skip : {Fore.YELLOW}{'Bật' if self.auto_skip_failed else 'Tắt'}")
        print(f"  • Mục tiêu  : {Fore.YELLOW}{self.max_jobs if self.max_jobs > 0 else 'Chạy liên tục'}")
        print(Fore.CYAN + "-" * 54)

        try:
            while True:
                if self.max_jobs > 0 and self.total_completed >= self.max_jobs:
                    print(f"\n{Fore.GREEN}[HOÀN THÀNH] Đã đạt đủ {self.max_jobs} nhiệm vụ yêu cầu!")
                    break

                job = self.get_job()
                if not job:
                    print(f"[{log_time()}] {Fore.YELLOW}Nghỉ 15s trước khi quét nhiệm vụ mới...")
                    self.countdown(15, "Tìm job tiếp theo")
                    continue

                job_id = job.get("id")
                job_type = job.get("type", "N/A")
                job_link = job.get("link", "")
                package = job.get("package_name", "")

                print(f"\n[{log_time()}] {Fore.GREEN + Style.BRIGHT}🎯 NHẬN JOB MỚI!")
                print(f"  • Job ID   : {Fore.WHITE}{job_id}")
                print(f"  • Hành động: {Fore.CYAN}{job_type} ({package})")
                print(f"  • Link     : {Fore.BLUE}{job_link}")

                # 1. Tự động mở link vào ứng dụng tương ứng trên điện thoại
                if self.auto_open_link and job_link:
                    opened = open_job_url(job_link)
                    if opened:
                        print(f"  • Trạng thái: {Fore.GREEN}Đã mở trực tiếp App trên điện thoại.")
                    else:
                        print(f"  • Trạng thái: {Fore.YELLOW}Link: {job_link}")

                # 2. Đếm ngược thời gian chờ trước khi Auto Submit
                if self.claim_delay_min == self.claim_delay_max:
                    delay_wait = self.claim_delay_min
                else:
                    delay_wait = random.randint(self.claim_delay_min, self.claim_delay_max)

                print(f"[{log_time()}] {Fore.CYAN}⏳ Chờ {delay_wait}s trước khi AUTO SUBMIT...")
                self.countdown(delay_wait, "Đang chờ nộp")

                # 3. Tự động nộp và nhận thưởng (Auto Submit)
                print(f"[{log_time()}] {Fore.MAGENTA}🚀 Đang AUTO SUBMIT nhận thưởng (ads_id={job_id})...")
                success, msg, prices = self.submit_job(job)

                # 4. Thử lại tự động nếu chưa duyệt
                retries = 0
                while not success and retries < self.max_retries:
                    retries += 1
                    print(f"[{log_time()}] {Fore.RED}[CHƯA DUYỆT] {msg}. Tự nộp lại lần {retries}/{self.max_retries} sau {self.retry_delay}s...")
                    self.countdown(self.retry_delay, f"Nộp lại {retries}/{self.max_retries}")
                    success, msg, prices = self.submit_job(job)

                # 5. Xử lý kết quả
                if success:
                    self.total_completed += 1
                    self.total_earned += prices
                    print(
                        f"[{log_time()}] {Fore.GREEN + Style.BRIGHT}✅ [THÀNH CÔNG] +{prices} VNĐ | "
                        f"Đã làm: {self.total_completed} jobs | Tổng kiếm: {self.total_earned:,} VNĐ"
                    )
                else:
                    self.total_failed += 1
                    print(f"[{log_time()}] {Fore.RED}❌ [THẤT BẠI] Không thể nhận thưởng: {msg}")

                    if self.auto_skip_failed:
                        print(f"[{log_time()}] {Fore.YELLOW}Đang tự động bỏ qua (Skip) nhiệm vụ lỗi...")
                        if self.skip_job(job):
                            self.total_skipped += 1
                            print(f"[{log_time()}] {Fore.GREEN}Đã bỏ qua job thành công.")
                        else:
                            print(f"[{log_time()}] {Fore.RED}Không thể bỏ qua job.")

                # 6. Nghỉ giữa 2 job để bảo vệ tài khoản
                if self.job_interval > 0:
                    self.countdown(self.job_interval, "Nghỉ giữa 2 job")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[!] Đã dừng bot (Ctrl+C).")

        finally:
            set_wake_lock(False)
            self.print_summary()

    def print_summary(self) -> None:
        elapsed = int(time.time() - self.start_time)
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        print("\n" + Fore.CYAN + "=" * 54)
        print(Fore.GREEN + Style.BRIGHT + "                BÁO CÁO KẾT QUẢ")
        print(Fore.CYAN + "=" * 54)
        print(f"  • Thời gian chạy   : {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"  • Jobs thành công  : {Fore.GREEN}{self.total_completed}")
        print(f"  • Jobs thất bại    : {Fore.RED}{self.total_failed}")
        print(f"  • Jobs đã bỏ qua   : {Fore.YELLOW}{self.total_skipped}")
        print(f"  • Tiền nhận được   : {Fore.GREEN + Style.BRIGHT}{self.total_earned:,} VNĐ")
        print(Fore.CYAN + "=" * 54 + "\n")


def setup_interactive() -> Dict[str, Any]:
    print_banner()
    cfg = ConfigManager.load()

    # 1. Nhập Token
    old_token = cfg.get("token", "")
    if old_token:
        print(f"{Fore.CYAN}Đã có token được lưu trên máy.")
        use_old = input(f"Dùng lại Token này? (y/n, mặc định y): ").strip().lower()
        if use_old == "n":
            token = getpass.getpass(f"{Fore.GREEN}Dán Authorization Token Golike mới (ẩn khi nhập): {Style.RESET_ALL}").strip()
        else:
            token = old_token
    else:
        token = getpass.getpass(f"{Fore.GREEN}Dán Authorization Token Golike (ẩn khi nhập): {Style.RESET_ALL}").strip()

    token = token.strip().strip("'\"")
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if not token:
        print(f"{Fore.RED}[!] Token không được để trống!")
        sys.exit(1)

    print(f"\n{Fore.CYAN}Đang kiểm tra tài khoản Golike...")
    status, res, raw = http_request("GET", "/users/me", token)
    if status != 200 or not (res.get("status") == 200 or res.get("success")):
        print(f"{Fore.RED}[!] Token không hợp lệ hoặc đã hết hạn! (HTTP {status})")
        print(f"{Fore.YELLOW}Chi tiết: {res.get('message', raw)}")
        sys.exit(1)

    user_data = res.get("data", {})
    username = user_data.get("username") or user_data.get("name") or "User"
    coin = user_data.get("coin", 0)
    print(f"{Fore.GREEN}[OK] Đăng nhập: {Fore.YELLOW}{username} {Fore.GREEN}| Số dư: {Fore.YELLOW}{coin:,} VNĐ")

    # 2. Chọn Nền Tảng MXH
    print(f"\n{Fore.CYAN}Chọn nền tảng làm nhiệm vụ:")
    for num, p in PLATFORMS.items():
        print(f"  [{num}] {p['name']}")
    choice_p = input(f"Chọn (1-{len(PLATFORMS)}, mặc định 1): ").strip()
    if choice_p not in PLATFORMS:
        choice_p = "1"
    platform = PLATFORMS[choice_p]
    print(f"-> Đã chọn: {Fore.GREEN}{platform['name']}")

    # 3. Lấy danh sách tài khoản đã liên kết
    print(f"\n{Fore.CYAN}Đang tải danh sách tài khoản {platform['name']}...")
    st_acc, res_acc, _ = http_request("GET", platform["account_endpoint"], token)
    accounts = []
    if st_acc == 200 and (res_acc.get("status") == 200 or res_acc.get("success")) and isinstance(res_acc.get("data"), list):
        accounts = res_acc["data"]

    if not accounts:
        print(f"{Fore.RED}[!] Không có tài khoản {platform['name']} nào được liên kết!")
        sys.exit(1)

    print(f"\n{Fore.GREEN}Danh sách tài khoản {platform['name']}:")
    for idx, acc in enumerate(accounts, 1):
        name_val = "N/A"
        for field in platform["name_field"]:
            if acc.get(field):
                name_val = str(acc[field])
                break
        print(f"  [{idx}] {name_val} (ID: {acc.get('id')})")

    choice_a = input(f"Chọn nick (1-{len(accounts)}, mặc định 1): ").strip()
    try:
        sel_idx = int(choice_a) - 1
        if sel_idx < 0 or sel_idx >= len(accounts):
            sel_idx = 0
    except ValueError:
        sel_idx = 0

    selected_acc = accounts[sel_idx]
    account_id = selected_acc.get("id")
    account_name = "N/A"
    for field in platform["name_field"]:
        if selected_acc.get(field):
            account_name = str(selected_acc[field])
            break

    print(f"-> Đã chọn nick: {Fore.GREEN}{account_name}")

    # 4. Cài đặt thời gian chờ Auto Submit
    print(f"\n{Fore.CYAN}=== CÀI ĐẶT THỜI GIAN AUTO SUBMIT ===")
    print(f"{Fore.YELLOW}Thời gian chờ làm xong tương tác trước khi tự động bấm nộp nhận thưởng.")
    delay_input = input(f"Thời gian chờ nộp (giây, vd: 15 hoặc 10-15, mặc định 12-15): ").strip()
    if not delay_input:
        claim_min, claim_max = 12, 15
    elif "-" in delay_input:
        parts = delay_input.split("-")
        try:
            claim_min = int(parts[0].strip())
            claim_max = int(parts[1].strip())
            if claim_min > claim_max:
                claim_min, claim_max = claim_max, claim_min
        except ValueError:
            claim_min, claim_max = 12, 15
    else:
        try:
            claim_min = int(delay_input)
            claim_max = claim_min
        except ValueError:
            claim_min, claim_max = 12, 15

    # 5. Thời gian nghỉ giữa 2 job
    interval_input = input(f"Nghỉ giữa 2 job (giây, mặc định 4): ").strip()
    job_interval = int(interval_input) if interval_input.isdigit() else 4

    # 6. Tự động mở App trên điện thoại
    auto_open_input = input(f"Tự mở ứng dụng ({platform['name']}) trên điện thoại? (y/n, mặc định y): ").strip().lower()
    auto_open_link = (auto_open_input != "n")

    # 7. Tự động bỏ qua khi nộp lỗi
    auto_skip_input = input(f"Tự động bỏ qua job nếu nộp thưởng lỗi? (y/n, mặc định y): ").strip().lower()
    auto_skip_failed = (auto_skip_input != "n")

    # 8. Giới hạn số job
    max_jobs_input = input(f"Số job muốn làm (nhập 0 = chạy không giới hạn, mặc định 0): ").strip()
    max_jobs = int(max_jobs_input) if max_jobs_input.isdigit() else 0

    new_cfg = {
        "token": token,
        "platform": platform["key"],
        "account_id": account_id,
        "account_name": account_name,
        "claim_delay_min": claim_min,
        "claim_delay_max": claim_max,
        "job_interval": job_interval,
        "auto_open_link": auto_open_link,
        "auto_skip_failed": auto_skip_failed,
        "max_jobs": max_jobs,
        "max_retries": 3,
        "retry_delay": 4,
    }

    ConfigManager.save(new_cfg)
    return new_cfg


def check_environment() -> None:
    """Kiểm tra cục bộ, không đọc token hoặc gọi API."""
    if sys.version_info < (3, 9):
        raise ValueError("Cần Python 3.9 trở lên. Trong Termux: pkg install python")
    ssl.create_default_context()
    print("Python:", sys.version.split()[0])
    print("TLS:", ssl.OPENSSL_VERSION)
    print("Mã nguồn:", Path(__file__).resolve())
    print("Cấu hình:", CONFIG_FILE)
    print("g-version:", os.environ.get("GOLIKE_APP_VERSION", APP_VERSION))
    print("g-client:", os.environ.get("GOLIKE_APP_CLIENT", APP_CLIENT))
    print("Môi trường:", "Termux/Android" if is_termux_env() else "Máy tính")
    if is_termux_env():
        for command in ("termux-open-url", "am", "termux-wake-lock"):
            print(command + ":", "có" if shutil.which(command) else "không có")
    print("Kiểm tra cục bộ hoàn tất; chưa xác minh API hoặc mở ứng dụng thật.")


def validate_config(cfg: Dict[str, Any]) -> None:
    if not isinstance(cfg.get("token"), str) or not cfg["token"].strip():
        raise ValueError("Thiếu token. Chạy bash run.sh --config để thiết lập.")
    if cfg.get("platform") not in {p["key"] for p in PLATFORMS.values()}:
        raise ValueError("Nền tảng không hợp lệ. Chạy bash run.sh --config.")
    try:
        if int(cfg.get("account_id") or 0) <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("Chưa chọn tài khoản hợp lệ. Chạy bash run.sh --config.") from None
    for key in ("claim_delay_min", "claim_delay_max", "job_interval", "max_jobs", "max_retries", "retry_delay"):
        if key in cfg:
            try:
                if isinstance(cfg[key], bool) or int(cfg[key]) < 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError(f"{key} phải là số nguyên không âm. Chạy bash run.sh --config.") from None
    if int(cfg.get("claim_delay_min", 12)) > int(cfg.get("claim_delay_max", 15)):
        raise ValueError("Thời gian chờ nhỏ nhất phải không lớn hơn thời gian lớn nhất.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Golike Auto Job & Auto Submit Bot for Termux & PC (Zero Dependencies)")
    parser.add_argument("--token", help="Golike Authorization Token")
    parser.add_argument("--platform", choices=["tiktok", "instagram", "facebook", "youtube", "threads", "twitter"])
    parser.add_argument("--account-id", type=int, help="Account ID làm nhiệm vụ")
    parser.add_argument("--delay", type=int, help="Thời gian chờ auto submit cố định (giây)")
    parser.add_argument("--interval", type=int, help="Thời gian nghỉ giữa các nhiệm vụ (giây)")
    parser.add_argument("--max-jobs", type=int, help="Số nhiệm vụ tối đa cần làm (0 = vô hạn)")
    parser.add_argument("--open-link", action="store_true", help="Tự động mở App trên điện thoại")
    parser.add_argument("--config", action="store_true", help="Vào cài đặt cấu hình mới")
    parser.add_argument("--check", action="store_true", help="Kiểm tra môi trường, không gọi API hoặc đọc token")
    args = parser.parse_args()
    if args.check:
        check_environment()
        return
    for name in ("delay", "interval", "max_jobs"):
        value = getattr(args, name)
        if value is not None and value < 0:
            parser.error(f"--{name.replace('_', '-')} phải không âm")
    if args.account_id is not None and args.account_id <= 0:
        parser.error("--account-id phải lớn hơn 0")

    cfg = ConfigManager.load()
    if args.token:
        cfg["token"] = args.token

    if args.config or not cfg.get("token") or not cfg.get("account_id"):
        cfg = setup_interactive()
    else:
        if args.token:
            cfg["token"] = args.token
        if args.platform:
            cfg["platform"] = args.platform
        if args.account_id:
            cfg["account_id"] = args.account_id
        if args.delay is not None:
            cfg["claim_delay_min"] = args.delay
            cfg["claim_delay_max"] = args.delay
        if args.interval is not None:
            cfg["job_interval"] = args.interval
        if args.max_jobs is not None:
            cfg["max_jobs"] = args.max_jobs
        if args.open_link:
            cfg["auto_open_link"] = True

        if len(sys.argv) == 1:
            print_banner()
            print(f"{Fore.CYAN}Đã tìm thấy cấu hình đã lưu (Chế độ Auto Submit - Không hỏi lại):")
            print(f"  • Token          : {Fore.YELLOW}Đã lưu (ẩn)")
            print(f"  • Nền tảng       : {Fore.GREEN}{cfg.get('platform', 'tiktok')}")
            print(f"  • Tài khoản      : {Fore.GREEN}{cfg.get('account_name', '')} (ID: {cfg.get('account_id')})")
            d_min = cfg.get("claim_delay_min", 12)
            d_max = cfg.get("claim_delay_max", 15)
            print(f"  • Chờ Auto Submit: {Fore.YELLOW}{d_min if d_min == d_max else f'{d_min}-{d_max}'} giây")
            print(f"  • Tự mở App      : {Fore.YELLOW}{'Bật' if cfg.get('auto_open_link') else 'Tắt'}")
            print(f"{Fore.YELLOW}Tip: Nếu muốn đổi tài khoản hoặc cài đặt lại, hãy chạy: python golike_bot.py --config")
            print(f"{Fore.GREEN}🚀 Tự động khởi động bot ngay...\n")
            time.sleep(1)

    validate_config(cfg)
    bot = GolikeBot(cfg)
    bot.run()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nĐã dừng. Chạy bash run.sh để mở lại.")
        sys.exit(130)
    except (ValueError, OSError) as exc:
        print(f"[LỖI] {exc}", file=sys.stderr)
        sys.exit(1)
