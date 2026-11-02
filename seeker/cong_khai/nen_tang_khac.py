# -*- coding: utf-8 -*-
"""LiteFinance (my.litefinance.org/traders) và Exness Social Trading.
Đo 03/11/2026 từ box:
- my.litefinance.vn: lỗi TLS (kết nối bị đóng) → không tới được. my.litefinance.org/<ngôn ngữ>/traders/info?id=... chuyển
  hướng về /traders (danh sách) → trang chi tiết không công khai cho client không đăng nhập. Danh sách chỉ có
  'Profitability (All time)' + mức rủi ro 1–10 → KHÔNG có DD % và tuổi → CHƯA ĐO ĐƯỢC, không thể ĐẠT.
- social-trading.exness.com: lỗi TLS từ box → không tới được."""
from __future__ import annotations
import re
from .mql5 import _van_ban, _so

LITEFINANCE_DS = "https://my.litefinance.org/en/traders"
LITEFINANCE_CT = "https://my.litefinance.org/en/traders/info?id={id}"
EXNESS_CT = "https://social-trading.exness.com/strategy/{id}"


def litefinance_danh_sach(h: str) -> list[dict]:
    t = _van_ban(h)
    ids = list(dict.fromkeys(re.findall(r"traders/info\?id=(\d+)", h)))
    the = re.findall(r"\n(@[^\n]+)\n(?:[^\n]*\n)?\s*(-?[\d.,]+)%\nProfitability \(All time\)\n\s*(\d+)\s*\nRisk", t)
    ra = []
    for i, (ten, g, rui_ro) in enumerate(the):
        sid = ids[i] if i < len(ids) else None
        ra.append({"nen_tang": "LiteFinance", "id": sid, "ten": ten.strip(),
                   "url": LITEFINANCE_CT.format(id=sid) if sid else LITEFINANCE_DS,
                   "that_demo": "CHƯA ĐO ĐƯỢC", "tuoi_thang": None, "tang_truong_pct": _so(g), "cagr_pct": None,
                   "dd_pct": None, "so_lenh": None, "symbol": [], "kieu": [], "cap_nhat_cuoi": None,
                   "csv_cong_khai": False,
                   "ghi_chu": f"chỉ có lợi nhuận toàn thời gian và rủi ro {rui_ro}/10 trên danh sách; DD và tuổi CHƯA ĐO ĐƯỢC"})
    return ra
