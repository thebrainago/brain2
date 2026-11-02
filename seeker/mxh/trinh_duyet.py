# -*- coding: utf-8 -*-
"""Mở trình duyệt riêng với hồ sơ cố định (persistent profile). Anh đăng nhập tay một lần; tool KHÔNG chạm vào mật khẩu."""
from __future__ import annotations
from pathlib import Path


def mo(cau_hinh: dict, an: bool = False):
    from playwright.sync_api import sync_playwright   # cài trên máy nhà: pip install playwright
    pw = sync_playwright().start()
    ho_so = Path(cau_hinh["thu_muc_ho_so"]); ho_so.mkdir(parents=True, exist_ok=True)
    kw = dict(user_data_dir=str(ho_so), headless=an, accept_downloads=True, viewport={"width": 1366, "height": 860},
              locale="vi-VN")
    if cau_hinh.get("kenh_trinh_duyet", "chrome") == "chrome":
        kw["channel"] = "chrome"
    ctx = pw.chromium.launch_persistent_context(**kw)
    return pw, ctx


def van_ban_trang(page) -> str:
    try:
        return page.inner_text("body", timeout=10000)
    except Exception:
        return ""
