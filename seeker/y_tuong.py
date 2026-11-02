# -*- coding: utf-8 -*-
"""Chuẩn hóa 'ý tưởng' từ một bài viết: phương pháp, tham số nhắc tới, bằng chứng, độ tin cậy."""
from __future__ import annotations
import hashlib, re

THAM_SO = [
    ("buoc_luoi_pip", r"(\d+(?:[.,]\d+)?)\s*(?:pips?|пунктов|点|ピップス?)\s*(?:grid|step|spacing|apart|шаг|间距)?"),
    ("he_so_lot", r"(?:multiplier|множитель|倍数|hệ số|x)\s*(\d(?:[.,]\d+)?)\b"),
    ("lot", r"(\d+(?:[.,]\d+)?)\s*(?:lots?|лот|手|ロット)"),
    ("rui_ro_pct", r"(\d+(?:[.,]\d+)?)\s*%\s*(?:risk|rủi ro|риск|风险)"),
    ("rsi", r"\bRSI\s*\(?\s*(\d{1,3})"),
    ("ma", r"\b(?:EMA|SMA|MA)\s*\(?\s*(\d{1,3})"),
    ("tp_pip", r"\b(?:TP|take ?profit)\s*[:=]?\s*(\d+)"),
    ("sl_pip", r"\b(?:SL|stop ?loss)\s*[:=]?\s*(\d+)"),
    ("khung", r"\b(M1|M5|M15|M30|H1|H4|D1)\b"),
    ("cap", r"\b(XAUUSD|EURUSD|GBPUSD|USDJPY|AUDCAD|AUDNZD|NZDCAD|GBPJPY|EURJPY|US30|NAS100|BTCUSD)\b"),
]
BANG_CHUNG = re.compile(r"https?://(?:www\.)?(?:myfxbook\.com/members|mql5\.com/\w\w/signals/\d+|fxblue\.com/users|"
                        r"darwinex\.com/darwin)[^\s\"'<>)]*", re.I)
CHUNG_TU = re.compile(r"statement|track record|live account|отчет|стейтмент|实盘|리얼|lịch sử giao dịch|trade history", re.I)


def rut(van_ban: str, khai_niem: list[str], nguon: str, ngon_ngu: str, url: str, ngay: str | None, tieu_de: str = "") -> dict | None:
    if not khai_niem:
        return None
    ts = {}
    for ten, mau in THAM_SO:
        g = [m.group(1) for m in re.finditer(mau, van_ban, re.I)][:5]
        if g:
            ts[ten] = sorted(set(g))
    bc = sorted(set(BANG_CHUNG.findall(van_ban)))[:10]
    ct = bool(CHUNG_TU.search(van_ban))
    tin = min(1.0, 0.2 + 0.1 * len(ts) + (0.3 if bc else 0) + (0.1 if ct else 0) + 0.05 * (len(khai_niem) - 1))
    # tóm tắt: câu đầu tiên có chứa khái niệm/tham số
    cau = re.split(r"(?<=[.!?。！？])\s+", van_ban)
    tom = next((c for c in cau if any(k.replace("_", " ") in c.lower() for k in khai_niem) or re.search(r"\d", c)), cau[0] if cau else "")
    return {"id": hashlib.sha1(url.encode()).hexdigest()[:16], "nguon": nguon, "ngon_ngu": ngon_ngu, "url": url,
            "ngay": ngay, "tieu_de": tieu_de[:200], "phuong_phap": khai_niem, "tom_tat": tom[:400],
            "tham_so": ts, "bang_chung": {"lien_ket": bc, "co_nhac_chung_tu": ct}, "do_tin_cay": round(tin, 2)}
