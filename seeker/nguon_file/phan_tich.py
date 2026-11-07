# -*- coding: utf-8 -*-
"""Bóc HTML/JSON đã có sẵn cho Code Base, GitHub, TradingView, diễn đàn.

Hàm thuần: không tải mạng. Lỗi trả về bản ghi có `loai`, không trả list rỗng.
Pine Script chỉ được trích khi nằm trong HTML tĩnh; không dịch sang MQL và không
coi bản trích là luật đã giải mã.
"""
from __future__ import annotations

import html
import json
import re

from seeker.phan_loai_loi import phan_loai_http

_PINE = re.compile(r"(//@version=\d[\s\S]{0,20000}?strategy\s*\()", re.I)
_CHU_DE = re.compile(r"viewtopic\.php\?[^\"']*t=(\d+)", re.I)


def _loi(loai: str, ly_do: str, http=None, dung_mien: bool = False) -> dict:
    return {"loai": loai, "ly_do": ly_do, "http": http, "dung_mien": dung_mien, "ban_ghi": []}


def boc_github_tim(http: int | None, than: str, url: str = "") -> dict:
    """API search repositories. 403/rate-limit là challenge, không phải 0 repo."""
    pl = phan_loai_http(http, than or "", url)
    if pl["loai"] != "ok":
        return {**pl, "items": [], "tong": None}
    try:
        obj = json.loads(than or "")
    except json.JSONDecodeError:
        return {**_loi("parse", "HTTP 200 nhưng JSON GitHub không đọc được", http), "items": [], "tong": None}
    if not isinstance(obj, dict) or "items" not in obj:
        msg = ""
        if isinstance(obj, dict):
            msg = str(obj.get("message") or "")
        if "rate limit" in msg.lower():
            return {**_loi("challenge", "GitHub: " + msg[:180], http, True), "items": [], "tong": None}
        return {**_loi("parse", "JSON GitHub không có khóa items", http), "items": [], "tong": None}
    items = obj.get("items") or []
    tong = obj.get("total_count")
    if not items:
        return {"loai": "no_data", "ly_do": f"API hợp lệ, total_count={tong}, 0 repo — không phải lỗi im",
                "http": http, "dung_mien": False, "items": [], "tong": tong}
    return {"loai": "ok", "ly_do": "HTTP 200", "http": http, "dung_mien": False, "items": items, "tong": tong}


def boc_tradingview(http: int | None, than: str, url: str) -> dict:
    pl = phan_loai_http(http, than or "", url)
    if pl["loai"] != "ok":
        return {**pl, "script": []}
    script = []
    thay = {}
    for m in re.finditer(
            r'href="((?:https://www\.tradingview\.com)?/script/([A-Za-z0-9]+-[^"/]+)/)"[^>]*>([^<]{3,160})<',
            than or "", re.I):
        slug = m.group(2)
        if slug in thay:
            continue
        thay[slug] = html.unescape(m.group(3)).strip()
        script.append({
            "nguon": "tradingview", "id": "tv_" + slug.split("-")[0],
            "url": "https://www.tradingview.com/script/%s/" % slug,
            "ten": thay[slug], "loai": "not_implemented",
            "ly_do": "có link script mở; Pine nằm trong JS nên chưa tải và chưa dịch — không phải luật chạy được",
            "da_dich": False, "lan": "dich_phuong_phap",
        })
    if script:
        return {"loai": "ok", "ly_do": f"{len(script)} link script; phần Pine chưa dịch", "http": http,
                "dung_mien": False, "script": script}
    if re.search(r"enable javascript|noscript|just a moment", (than or "")[:4000], re.I):
        return {**_loi("parse", "HTTP 200 nhưng danh sách TradingView là vỏ JS/chống bot — không phải 0 script", http),
                "script": []}
    return {**_loi("parse", "HTTP 200, không thấy thẻ script mở (href tương đối lẫn tuyệt đối)", http), "script": []}


def boc_pine(than: str) -> dict:
    """Trích Pine nếu HTML tĩnh chứa //@version và strategy(. Không dịch."""
    pl = phan_loai_http(200, than or "", "https://www.tradingview.com/script/x/")
    if pl["loai"] == "challenge":
        return {**pl, "pine": None, "da_dich": False}
    m = _PINE.search(than or "")
    if not m:
        thoat = (than or "").replace("\\n", "\n").replace('\\"', '"')
        m = _PINE.search(thoat)
    if not m:
        return {"loai": "not_implemented", "ly_do": "không có Pine trong HTML tĩnh; trang vẽ bằng JS. Không tải, không dịch.",
                "http": 200, "dung_mien": False, "pine": None, "da_dich": False}
    return {"loai": "ok", "ly_do": "trích Pine từ HTML tĩnh; CHƯA dịch sang MQL/Python; chưa phải luật đã giải mã",
            "http": 200, "dung_mien": False, "pine": m.group(1)[:20000], "da_dich": False}


def boc_dien_dan(http: int | None, than: str, url: str, nguon: str) -> dict:
    pl = phan_loai_http(http, than or "", url)
    if pl["loai"] != "ok":
        return {**pl, "nguon": nguon, "url": url, "so_chu_de": None, "lan": "loi"}
    ids = set(_CHU_DE.findall(than or ""))
    if not ids:
        return {"loai": "parse", "ly_do": "HTTP 200 nhưng 0 chủ đề — không phải bằng chứng diễn đàn rỗng (JS hoặc chống bot)",
                "http": http, "dung_mien": False, "nguon": nguon, "url": url, "so_chu_de": 0, "lan": "loi"}
    return {"loai": "ok", "ly_do": f"{len(ids)} chủ đề", "http": http, "dung_mien": False,
            "nguon": nguon, "url": url, "so_chu_de": len(ids), "lan": "chi_danh_muc"}


def boc_trang_codebase(http: int | None, than: str, cid: str) -> dict:
    pl = phan_loai_http(http, than or "", f"https://www.mql5.com/en/code/{cid}")
    if pl["loai"] != "ok":
        return {**pl, "id": "cb" + str(cid)}
    tit = re.search(r"<title>Free download of the &#x27;(.*?)&#x27; expert by &#x27;(.*?)&#x27;", than or "")
    tep = sorted(set(re.findall(r'href="(/en/code/download/%s/[^"]+\.mq5)"' % re.escape(str(cid)), than or "")))
    if not tit and not tep:
        return {"loai": "parse", "ly_do": "HTTP 200 nhưng không có tiêu đề expert hay link .mq5 — không ghi EA rỗng",
                "http": http, "dung_mien": False, "id": "cb" + str(cid)}
    rv = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)', than or "")
    dl = re.search(r"Downloads:\s*([\d\s,]+)", than or "")
    return {
        "loai": "ok", "ly_do": "HTTP 200", "http": http, "dung_mien": False,
        "id": "cb" + str(cid), "url": f"https://www.mql5.com/en/code/{cid}",
        "ten": html.unescape(tit.group(1)) if tit else str(cid),
        "tac_gia": html.unescape(tit.group(2)) if tit else None,
        "rating": float(rv.group(1)) if rv else None,
        "tai_ve": int(re.sub(r"\D", "", dl.group(1))) if dl else None,
        "tep_mq5": tep,
    }
