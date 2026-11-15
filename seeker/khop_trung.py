# -*- coding: utf-8 -*-
"""Khử trùng thận trọng.

Chắc (được gộp khi so sánh): cùng id tín hiệu, cùng URL chuẩn, cùng repo id, cùng blob sha.
Nghi: cùng token tên không phổ biến VÀ cùng mã (máy chủ giống hay khác đều chỉ là nghi).
Khớp tên đơn độc — kể cả 70% — không phải chứng minh và không đủ để đánh nghi.
Không xóa bản ghi. Lưới/DCA không bị loại ở đây.
"""
from __future__ import annotations

import re

_CHUNG = {
    "gold", "live", "pro", "signal", "trader", "trading", "account", "expert", "advisor",
    "scalper", "robot", "system", "free", "best", "high", "risk", "real", "demo",
}


def _token(ten: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{5,}", (ten or "").lower()) if t not in _CHUNG}


def trung_chac(a: dict, b: dict) -> str | None:
    if a is b:
        return None
    for khoa, nhan in (("id", "cùng id"), ("url", "cùng URL"), ("repo_id", "cùng repo id"), ("blob_sha", "cùng blob sha")):
        x, y = a.get(khoa), b.get(khoa)
        if x and y and str(x) == str(y):
            return nhan
    return None


def la_chung_minh_vi_khop_ten(_ty_le: float) -> bool:
    """Khớp tên, dù 70% hay 100%, không chứng minh hai hệ là một."""
    return False


def trung_nghi(a: dict, b: dict) -> str | None:
    if trung_chac(a, b):
        return None
    te = a.get("ten_tep")
    if te and te == b.get("ten_tep") and a.get("repo") and b.get("repo") and a.get("repo") != b.get("repo"):
        return "nghi: cùng tên tệp, khác repo — không gộp"
    giao = _token(a.get("ten") or "") & _token(b.get("ten") or "")
    ma = {str(x).upper() for x in (a.get("ma") or [])} & {str(x).upper() for x in (b.get("ma") or [])}
    if not giao or not ma:
        return None
    may = (a.get("may_chu") or "").strip().lower()
    cung_may = bool(may) and may == (b.get("may_chu") or "").strip().lower()
    return "nghi: token %s, mã %s%s" % (
        ",".join(sorted(giao)), " ".join(sorted(ma)), ", cùng máy chủ" if cung_may else ", máy chủ khác hoặc thiếu")


def gan_nghi(ds: list[dict], khoa: str = "id") -> list[dict]:
    """Gắn `trung_nghi_ngo` (id khác) lên từng bản. Không xóa."""
    for i, a in enumerate(ds):
        nghi = []
        for b in ds:
            if a is b:
                continue
            ly = trung_nghi(a, b)
            if ly:
                nghi.append({"id": b.get(khoa), "ly_do": ly})
        a["trung_nghi_ngo"] = nghi
    return ds
