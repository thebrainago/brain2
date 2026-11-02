# -*- coding: utf-8 -*-
"""Bộ đọc trang công khai MQL5 Signals (https://www.mql5.com/en/signals/<id>).
Lưu ý: 'Growth' của MQL5 tính theo lợi nhuận giao dịch, BỎ QUA nạp/rút (không phải lợi nhuận trên vốn ròng).
Lịch sử CSV (/export/history) đòi đăng nhập → không tải (không vượt)."""
from __future__ import annotations
import html as _html, re
from datetime import datetime

GOC = "https://www.mql5.com"
DS_LIST = ("/en/signals/mt5/list", "/en/signals/mt4/list")


def _van_ban(h: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = _html.unescape(t).replace("\xa0", " ")
    return re.sub(r"\n\s*\n+", "\n", t)


def _so(s):
    if s is None:
        return None
    s = s.replace(" ", "").replace("\u202f", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _sau(t, nhan, mau=r"(-?[\d  \u202f.,]+)"):
    m = re.search(re.escape(nhan) + r"\s*\n?\s*" + mau, t)
    return m.group(1).strip() if m else None


def id_tu_danh_sach(h: str) -> list[str]:
    return sorted(set(re.findall(r"/en/signals/(\d{5,9})(?![\d/])", h)))


def phan_tich(h: str, sid: str, ngay_doc: datetime | None = None) -> dict:
    from .cham_diem import cagr_tu_tang_truong, TUAN_MOT_NAM
    t = _van_ban(h)
    ten = None
    m = re.search(r"<title>\s*Copy trades of the (.*?) trading signal for (MetaTrader \d)", h, re.S)
    if m:
        ten, nen = _html.unescape(m.group(1)).strip(), m.group(2)
    else:
        m2 = re.search(r"<title>(.*?)</title>", h, re.S)
        ten = _html.unescape(m2.group(1)).strip() if m2 else sid
        nen = "MetaTrader 5" if "MetaTrader 5" in t[:3000] else ("MetaTrader 4" if "MetaTrader 4" in t[:3000] else None)
    g = _so(_sau(t, "Growth:", r"(-?[\d  \u202f.,]+)%"))
    tuan = _so(_sau(t, "Weeks:"))
    bat_dau = _sau(t, "Started:", r"(\d{4}\.\d{2}\.\d{2})")
    tuoi = None
    if tuan:   # Weeks = toàn bộ lịch sử mà Growth bao phủ (có thể trước ngày đăng tín hiệu)
        tuoi = round(tuan / TUAN_MOT_NAM * 12, 2)
    elif bat_dau:
        d0 = datetime.strptime(bat_dau, "%Y.%m.%d"); d1 = ngay_doc or datetime.now()
        tuoi = round((d1 - d0).days / 30.4375, 2)
    dd_b = _so(_sau(t, "By Balance:", r"([\d.,]+)%"))
    dd_e = _so(_sau(t, "By Equity:", r"([\d.,]+)%"))
    dds = [x for x in (dd_b, dd_e) if x is not None]
    dd = max(dds) if dds else None
    so_lenh = _so(_sau(t, "Trades:"))
    # symbol: bảng Distribution
    sym = []
    md = re.search(r"Distribution\nSymbol\nDeals\nSell\nBuy\n(.*?)\n(?:\d+(?:\.\d)?K?\n){3}", t, re.S)
    if md:
        dong = md.group(1).split("\n")
        sym = [x for x in dong if re.fullmatch(r"[A-Za-z][A-Za-z0-9._#+\-]{2,20}", x)]
    may_chu = None
    mm = re.search(r"growth since \d{4}\n[^\n]*\n([^\n]+)\n\s*1:\d+", t)
    if mm:
        may_chu = mm.group(1).strip()
    if may_chu:
        that_demo = "demo" if re.search(r"demo|contest", may_chu, re.I) else "that"
    else:
        that_demo = "CHƯA ĐO ĐƯỢC"
    cuoi = _sau(t, "Latest trade:", r"([^\n]+)")
    mo_ta = t.lower()
    kieu = [k for k, p in (("grid", r"\bgrid\b|lưới"), ("martingale", r"martingale|\bmartin\b"),
                           ("hedge", r"\bhedg"), ("dca", r"\bdca\b|averaging"))
            if re.search(p, mo_ta)]
    nap = _so(_sau(t, "Deposits:")); rut = _so(_sau(t, "Withdrawals:")); von = _so(_sau(t, "Initial Deposit:"))
    return {
        "nen_tang": "MQL5", "id": sid, "url": f"{GOC}/en/signals/{sid}", "ten": ten, "mt": nen,
        "that_demo": that_demo, "may_chu": may_chu, "tuoi_thang": tuoi, "bat_dau": bat_dau,
        "tang_truong_pct": g, "cagr_pct": cagr_tu_tang_truong(g, tuoi), "dd_pct": dd,
        "dd_so_du_pct": dd_b, "dd_von_pct": dd_e, "so_lenh": int(so_lenh) if so_lenh else None,
        "symbol": sym, "kieu": kieu, "cap_nhat_cuoi": cuoi, "von_dau": von, "nap": nap, "rut": rut,
        "csv_cong_khai": False,
        "ghi_chu": "Growth MQL5 bỏ qua nạp/rút; thật/demo suy từ tên máy chủ; kiểu (grid/martingale/hedge) chỉ là từ có trong trang",
    }
