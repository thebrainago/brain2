# -*- coding: utf-8 -*-
"""Chấm điểm tín hiệu công khai.
CỔNG ĐẠT (duy nhất): max DD < 80% VÀ CAGR > 10%/năm. Không thêm tiêu chí nào khác.
diem_xep_hang(): CHỈ dùng để sắp thứ tự giữa các tín hiệu đã ĐẠT — không bao giờ là cổng."""
from __future__ import annotations

DD_MAX = 80.0
CAGR_MIN = 10.0
TUAN_MOT_NAM = 52.1775


def cagr_tu_tang_truong(tang_truong_pct, so_thang):
    """CAGR %/năm từ tăng trưởng tích lũy (%) và tuổi (tháng). None nếu thiếu dữ liệu."""
    if tang_truong_pct is None or not so_thang or so_thang <= 0:
        return None
    hs = 1 + tang_truong_pct / 100.0
    if hs <= 0:
        return -100.0
    return round((hs ** (12.0 / so_thang) - 1) * 100, 2)


def dat(dd_pct, cagr_pct) -> str:
    """'DAT' / 'KHONG_DAT' / 'CHUA_DO' (thiếu số đo)."""
    if dd_pct is None or cagr_pct is None:
        return "CHUA_DO"
    return "DAT" if (dd_pct < DD_MAX and cagr_pct > CAGR_MIN) else "KHONG_DAT"


def diem_xep_hang(t: dict) -> float:
    """CHỈ ĐỂ XẾP HẠNG giữa các tín hiệu đã ĐẠT: tuổi dài hơn, tài khoản thật, DD thấp hơn xếp trên.
    CAGR bị chặn trần 200%/năm để tín hiệu tuổi ngắn tăng vọt không chiếm đầu bảng."""
    tuoi = min(t.get("tuoi_thang") or 0, 60) / 60.0          # 0..1
    that = 1.0 if t.get("that_demo") == "that" else 0.0
    dd = t.get("dd_pct"); dd_diem = 0 if dd is None else max(0.0, 1 - dd / DD_MAX)
    c = t.get("cagr_pct") or 0; c_diem = min(max(c, 0), 200) / 200.0
    return round(100 * (0.40 * tuoi + 0.25 * that + 0.20 * dd_diem + 0.15 * c_diem), 2)
