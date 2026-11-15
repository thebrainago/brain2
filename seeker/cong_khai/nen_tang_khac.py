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


def litefinance_danh_sach_ro(h: str) -> dict:
    """Không biến 0 hồ sơ bóc được thành 'không có trader', và không biến hồ sơ thiếu DD thành ĐẠT."""
    from seeker.phan_loai_loi import phan_loai_http
    pl = phan_loai_http(200, h or "", LITEFINANCE_DS)
    if pl["loai"] == "challenge":
        return {**pl, "ho_so": [], "da_danh_gia": 0, "so_ho_so": 0}
    ho = litefinance_danh_sach(h)
    if ho:
        return {"loai": "no_data",
                "ly_do": ("%d hồ sơ trên danh sách (lợi nhuận + rủi ro) nhưng không có DD%% và tuổi — "
                          "chưa đánh giá; không phải 0 trader; không phải ĐẠT") % len(ho),
                "http": 200, "dung_mien": False, "ho_so": ho, "da_danh_gia": 0, "so_ho_so": len(ho)}
    return {"loai": "parse",
            "ly_do": "HTTP 200 nhưng không bóc được hồ sơ (vỏ JS hoặc HTML khác mẫu) — không ghi 0 trader",
            "http": 200, "dung_mien": False, "ho_so": [], "da_danh_gia": 0, "so_ho_so": 0}


def _sau_nhan(t: str, nhan: str):
    m = re.search(re.escape(nhan) + r"\s*\n?\s*(-?[\d.,]+)", t, re.I)
    return _so(m.group(1)) if m else None


def litefinance_chi_tiet(h: str, url_yeu_cau: str, url_cuoi: str | None = None, http: int | None = 200) -> dict:
    """Trang info?id=. Chuyển hướng về danh sách = auth, không đánh giá. Thiếu DD = parse."""
    from seeker.phan_loai_loi import phan_loai_http
    from .cham_diem import cagr_tu_tang_truong
    cuoi = url_cuoi or url_yeu_cau
    m = re.search(r"[?&]id=(\d+)", url_yeu_cau)
    sid = m.group(1) if m else None
    nen = {"nen_tang": "LiteFinance", "id": sid, "url": url_yeu_cau, "url_cuoi": cuoi,
           "da_danh_gia": False, "dd_pct": None, "cagr_pct": None, "tuoi_thang": None,
           "tang_truong_pct": None, "symbol": [], "ten": None}
    pl = phan_loai_http(http, h or "", url_yeu_cau, cuoi)
    if pl["loai"] != "ok":
        return {**nen, **pl, "da_danh_gia": False}
    if sid and f"id={sid}" not in cuoi and "/traders/info" not in cuoi:
        return {**nen, "loai": "auth", "http": http, "dung_mien": False,
                "ly_do": "trang chi tiết chuyển hướng khỏi id — không công khai khi chưa đăng nhập; không đánh giá"}
    t = _van_ban(h or "")
    if sid and "Max drawdown" not in t and "Profitability (All time)" in t and f"id={sid}" not in (h or ""):
        return {**nen, "loai": "auth", "http": http, "dung_mien": False,
                "ly_do": "nội dung là danh sách, không phải hồ sơ của id này; không đánh giá"}
    dd = _sau_nhan(t, "Max drawdown")
    if dd is None:
        return {**nen, "loai": "parse", "http": http, "dung_mien": False,
                "ly_do": "ở URL chi tiết nhưng không có Max drawdown — không đánh giá, không phải DD=0"}
    g = _sau_nhan(t, "Profitability (All time)")
    tuoi = None
    tm = re.search(r"(\d+)\s*months", t, re.I)
    if tm:
        tuoi = float(tm.group(1))
    sym = re.findall(r"\b[A-Z]{6}\b", t)
    ten = None
    tm2 = re.search(r"@([A-Za-z0-9_.-]{2,})", t)
    if tm2:
        ten = "@" + tm2.group(1)
    return {**nen, "loai": "ok", "http": http, "dung_mien": False, "da_danh_gia": True, "ten": ten,
            "dd_pct": dd, "tang_truong_pct": g, "tuoi_thang": tuoi, "symbol": sym,
            "cagr_pct": cagr_tu_tang_truong(g, tuoi),
            "ly_do": "có DD và lợi nhuận trên trang chi tiết; vẫn là lịch sử người khác, chưa phải hệ của mình"}
