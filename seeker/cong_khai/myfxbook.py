# -*- coding: utf-8 -*-
"""Bộ đọc trang công khai Myfxbook (myfxbook.com/members/<user>/<system>/<id> và bảng xếp hạng /systems).
Đo 03/11/2026: cả robots.txt lẫn trang đều trả Cloudflare 'Just a moment...' (HTTP 403) cho box → BỊ CHẶN,
không vượt. Bộ phân tích giữ sẵn để chạy khi trang trả HTML thật (vd. máy nhà)."""
from __future__ import annotations
import re
from .mql5 import _van_ban, _so

DS = ("https://www.myfxbook.com/systems",)


def link_he_thong(h: str) -> list[str]:
    return sorted(set("https://www.myfxbook.com" + x for x in re.findall(r'href="(/members/[^"/]+/[^"/]+/\d+)"', h)))


def phan_tich(h: str, url: str) -> dict:
    from seeker.phan_loai_loi import phan_loai_http
    from .cham_diem import cagr_tu_tang_truong
    pl = phan_loai_http(200, h or "", url)
    if pl["loai"] == "challenge":
        return {"nen_tang": "Myfxbook", "id": None, "url": url, "ten": None, "loai": "challenge",
                "da_danh_gia": False, "dd_pct": None, "cagr_pct": None, "tuoi_thang": None,
                "tang_truong_pct": None, "that_demo": "CHƯA ĐO ĐƯỢC", "symbol": [], "kieu": [],
                "ly_do": pl["ly_do"], "ghi_chu": "trang challenge — không tạo hồ sơ giả"}
    t = _van_ban(h)
    def lay(n, mau=r"(-?[\d.,]+)"):
        m = re.search(re.escape(n) + r"\s*\n?\s*" + mau, t); return m.group(1) if m else None
    g = _so(lay("Gain", r"(-?[\d.,]+)%")); dd = _so(lay("Drawdown", r"([\d.,]+)%"))
    tuoi = None
    m = re.search(r"Started[^\n]*\n?\s*(\d{2})/(\d{2})/(\d{4})", t)
    if m:
        from datetime import datetime
        tuoi = round((datetime.now() - datetime(int(m.group(3)), int(m.group(1)), int(m.group(2)))).days / 30.4375, 2)
    td = "demo" if re.search(r"\bDemo\b", t[:20000]) else ("that" if re.search(r"\bReal\b", t[:20000]) else "CHƯA ĐO ĐƯỢC")
    sid = url.rstrip("/").split("/")[-1]
    return {"nen_tang": "Myfxbook", "id": sid, "url": url, "ten": url.split("/")[-2], "that_demo": td,
            "tuoi_thang": tuoi, "tang_truong_pct": g, "cagr_pct": cagr_tu_tang_truong(g, tuoi), "dd_pct": dd,
            "so_lenh": None, "symbol": [], "kieu": [], "cap_nhat_cuoi": None,
            "csv_cong_khai": False, "ghi_chu": "Gain Myfxbook là TWR (đã loại nạp/rút)"}
