# -*- coding: utf-8 -*-
"""Bộ lọc chất lượng nguồn: GIỮ / ƯU TIÊN nguồn chia sẻ chiến lược/EA dùng ngay được kèm lịch sử kiểm chứng.
Bậc (khai báo trong web.yaml bằng khóa `chat_luong`, nếu thiếu thì suy theo id):
  co_lich_su  — chiến lược/EA + lịch sử kiểm chứng công khai (MQL5 Signals/Code Base, GitHub, Myfxbook) → hệ số 1.3
  chien_luoc  — chia sẻ chiến lược/EA/tệp nhưng không có lịch sử kiểm chứng                           → hệ số 1.0
  thao_luan   — chủ yếu thảo luận/tin tức                                                               → hệ số 0.5, bỏ khi --chi-chat-luong
Đây là bộ lọc NGUỒN cho Seeker, KHÔNG phải tiêu chí ĐẠT của hệ (tiêu chí ĐẠT vẫn chỉ là DD<80% & CAGR>10%)."""
from __future__ import annotations

HE_SO = {"co_lich_su": 1.3, "chien_luoc": 1.0, "thao_luan": 0.5}
_CO_LICH_SU = ("mql5_signals", "mql5_codebase", "github", "myfxbook")
_CHIEN_LUOC = ("mql5_forum", "forexfactory", "babypips", "tradingview_scripts", "telegram", "tg_", "elitetrader",
               "traderviet", "kaskus", "note_com", "juejin")


def bac(nid: str, n: dict | None = None) -> str:
    if n and n.get("chat_luong") in HE_SO:
        return n["chat_luong"]
    if any(nid.startswith(x) for x in _CO_LICH_SU):
        return "co_lich_su"
    if any(nid.startswith(x) for x in _CHIEN_LUOC):
        return "chien_luoc"
    return "thao_luan"


def giu(nid: str, n: dict | None = None, chi_chat_luong: bool = False) -> bool:
    return not (chi_chat_luong and bac(nid, n) == "thao_luan")


def uu_tien(nid: str, n: dict | None, goc: float) -> float:
    return round(goc * HE_SO[bac(nid, n)], 4)
