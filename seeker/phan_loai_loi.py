# -*- coding: utf-8 -*-
"""Phân loại kết quả nguồn SEEKER.

Một lần đọc chỉ được kết thúc bằng một loại rõ, không được trả danh sách rỗng
rồi coi là thành công. Bản chụp cũ là `stale`, chưa đo là `unknown`, feed rỗng
thật là `no_data`. Challenge thì dừng miền: không đổi User-Agent, không đổi IP,
không tắt kiểm TLS.

Loại: ok, auth, challenge, network, parse, not_implemented, no_data, stale,
unknown, robots.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

LOAI = (
    "ok", "auth", "challenge", "network", "parse", "not_implemented",
    "no_data", "stale", "unknown", "robots",
)

_CHALLENGE = (
    "just a moment", "cf-chl", "cf_chl", "challenge-platform", "attention required",
    "are you a robot", "ddos-guard", "please enable js", "checking your browser",
    "anubis", "cf-browser-verification",
)
_LOGIN = (
    "log in to continue", "please log in", "sign in to continue", "login required",
    "you must be logged in", "to see trades in realtime, please log in",
    "authorization required",
)
_LOGIN_DUONG = re.compile(r"/(login|signin|sign-in|account/login|auth)\b", re.I)


def _gia_thuyet_dns(chu: str) -> str:
    if "198.18.0." in (chu or ""):
        return (" | giả thuyết: máy phân giải/proxy trả 198.18.0.1 (fake-ip, thường gặp khi WARP). "
                "Chưa chứng minh website hỏng. Không tắt TLS, không đổi DNS, không đi proxy khác để vượt.")
    return ""


def phan_loai_http(ma, text: str = "", url: str = "", url_cuoi: str | None = None,
                   loi: str | None = None, content_type: str = "") -> dict:
    """Phân loại một phản hồi HTTP hoặc một lỗi kết nối. Không tải gì thêm."""
    than = text or ""
    dau = than[:8000].lower()
    cuoi = url_cuoi or url
    # robots.txt thật hay nhắc Disallow: /captcha/ . Đó không phải trang chặn.
    if ma == 200 and "user-agent:" in dau and ("disallow:" in dau or "allow:" in dau) \
            and "just a moment" not in dau and "cf-chl" not in dau and "<html" not in dau[:500]:
        return {"loai": "ok", "ly_do": "robots.txt", "http": ma, "dung_mien": False, "stale": False}
    if ma is None or ma == 0:
        ly = loi or "không kết nối"
        return {"loai": "network", "ly_do": (ly[:800] + _gia_thuyet_dns(ly + than)),
                "http": None, "dung_mien": False, "stale": False}
    if ma in (401, 407):
        return {"loai": "auth", "ly_do": f"HTTP {ma}", "http": ma, "dung_mien": False, "stale": False}
    manh = any(d in dau for d in _CHALLENGE)
    # Chữ "captcha" một mình không đủ: robots.txt và bài diễn đàn đều có thể nhắc từ này.
    if ma in (403, 429, 503) or (ma in (200, 202) and manh and len(than) < 30000) or (ma == 202 and "captcha" in dau and manh):
        dau_thay = next((d for d in _CHALLENGE if d in dau), "captcha" if "captcha" in dau else "")
        ly = f"HTTP {ma}" + (f" + dấu hiệu '{dau_thay}'" if dau_thay else "")
        if ma == 429:
            ly += " — giới hạn tốc độ; chỉ được chờ rồi dừng, không đổi danh tính"
        return {"loai": "challenge", "ly_do": ly, "http": ma, "dung_mien": True, "stale": False}
    if cuoi and url and cuoi != url and _LOGIN_DUONG.search(urlparse(cuoi).path or ""):
        return {"loai": "auth", "ly_do": "chuyển hướng sang trang đăng nhập " + urlparse(cuoi).path,
                "http": ma, "dung_mien": False, "stale": False}
    if any(d in dau for d in _LOGIN):
        return {"loai": "auth", "ly_do": "trang yêu cầu đăng nhập", "http": ma, "dung_mien": False, "stale": False}
    if ma == 404:
        return {"loai": "no_data", "ly_do": "HTTP 404 — URL không có tài nguyên, không phải 0 chiến lược đã đo",
                "http": ma, "dung_mien": False, "stale": False}
    if ma == 200:
        if "html" in (content_type or "").lower() and "csv" in (url or "").lower():
            return {"loai": "auth", "ly_do": "URL CSV trả HTML — thường là trang đăng nhập",
                    "http": ma, "dung_mien": False, "stale": False}
        return {"loai": "ok", "ly_do": "HTTP 200", "http": ma, "dung_mien": False, "stale": False}
    if 500 <= ma <= 599:
        return {"loai": "network", "ly_do": f"HTTP {ma}", "http": ma, "dung_mien": False, "stale": False}
    return {"loai": "parse", "ly_do": f"HTTP {ma} không khớp bộ đọc", "http": ma, "dung_mien": False, "stale": False}


def ket_qua_boc(trang_thai: str, ly_do: str, cach: str | None, ky_tu: int, so_muc: int,
                noi_dung: str, can_dang_nhap: bool) -> tuple[str, str, str]:
    """Gắn loại cho một lần quét sổ nguồn. 0 mục sau HTTP 200 không còn là ĐỌC ĐƯỢC."""
    bang = {
        "BỊ CHẶN — cần chạy máy nhà": "challenge",
        "CẦN ĐĂNG NHẬP": "auth",
        "LỖI MẠNG / HẾT HẠN": "network",
        "ROBOTS.TXT CẤM — không đọc": "robots",
        "CHƯA CÓ URL": "not_implemented",
        "THỦ CÔNG (chủ dự án)": "not_implemented",
    }
    if trang_thai in bang:
        return trang_thai, ly_do, bang[trang_thai]
    if trang_thai != "ĐỌC ĐƯỢC":
        return trang_thai, ly_do, "unknown"
    if so_muc > 0:
        return "ĐỌC ĐƯỢC", ly_do, "ok"
    if can_dang_nhap:
        return "CẦN ĐĂNG NHẬP", "trang công khai không có mục (nội dung sau đăng nhập hoặc JS)", "auth"
    dau = (noi_dung or "")[:1500].lower()
    if (cach or "") == "rss" or "<rss" in dau or "<feed" in dau or "<atom" in dau:
        return ("KHÔNG CÓ MỤC",
                "feed phân tích được, 0 mục — no_data, không phải thành công im và không phải bản chụp cũ",
                "no_data")
    return ("LỖI PHÂN TÍCH",
            f"HTTP 200, {ky_tu} ký tự, không bóc được mục (parser hoặc trang JS) — không ghi nhận 0 kết quả",
            "parse")
