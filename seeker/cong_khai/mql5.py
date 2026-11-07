# -*- coding: utf-8 -*-
"""Bộ đọc trang công khai MQL5 Signals (https://www.mql5.com/en/signals/<id>).
Lưu ý: 'Growth' của MQL5 tính theo lợi nhuận giao dịch, BỎ QUA nạp/rút (không phải lợi nhuận trên vốn ròng).
Lịch sử CSV (/export/history) đòi đăng nhập → không tải (không vượt)."""
from __future__ import annotations
import html as _html, re
from datetime import datetime

GOC = "https://www.mql5.com"
DS_LIST = ("/en/signals/mt5/list", "/en/signals/mt4/list")
# Các cách sắp danh sách (giảm thiên lệch sống sót): mặc định (xếp hạng), mới nhất, cũ nhất, DD cao/thấp, lãi, số lệnh, hoạt động
SAP_XEP = ("", "orderby=weeks&dir=up", "orderby=weeks", "orderby=drawdown", "orderby=drawdown&dir=up",
           "orderby=gain", "orderby=trades", "orderby=activity", "orderby=balance&dir=up")


def url_danh_sach(mt: str, trang: int, sap: str = "") -> str:
    u = f"{GOC}/en/signals/{mt}/list" + (f"/page{trang}" if trang > 1 or sap else "")
    return u + (f"?{sap}" if sap else "")


def duong_cong(h: str) -> dict:
    """Đường cong Growth công khai mà trang nhúng sẵn: bảng năm/tháng (phân số → %) của biểu đồ Growth
    và chuỗi (thời điểm, Growth %) lấy mẫu ≤ 40 điểm."""
    i = h.find("window.growthChart(")
    if i < 0:
        return {}
    m = re.search(r"table:\{years:\[(.*?)\],total", h[i:i + 20000], re.S)
    nam = {}
    if m:
        for y, yr, mo in re.findall(r"\{year:(\d{4}),yearly:(-?[\d.]+),months:\{([^}]*)\}", m.group(1)):
            nam[int(y)] = {"nam_pct": round(float(yr) * 100, 2),
                           "thang": {int(k) + 1: round(float(v) * 100, 2) for k, v in re.findall(r'"(\d+)":(-?[\d.]+)', mo)}}
    mm = re.search(r"\[([-\d.,\s]+)\]\);\s*$", h[max(0, i - 400000):i])
    diem = []
    if mm:
        so = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", mm.group(1))]
        cap = list(zip(so[0::2], so[1::2]))
        if cap and cap[0][0] > 1e9:
            buoc = max(1, len(cap) // 40)
            from datetime import datetime as _d, timezone as _tz
            diem = [(_d.fromtimestamp(t, _tz.utc).strftime("%Y-%m-%d"), g) for t, g in cap[::buoc]] + \
                   [(_d.fromtimestamp(cap[-1][0], _tz.utc).strftime("%Y-%m-%d"), cap[-1][1])]
    chuoi = [v for y in sorted(nam) for _, v in sorted(nam[y]["thang"].items())]
    ra = {"theo_nam_pct": {y: nam[y]["nam_pct"] for y in sorted(nam)}, "thang_pct": chuoi, "growth_mau": diem}
    if chuoi:
        ra.update({"so_thang": len(chuoi), "thang_am_pct": round(100 * sum(x < 0 for x in chuoi) / len(chuoi), 1),
                   "thang_te_nhat_pct": min(chuoi), "thang_tot_nhat_pct": max(chuoi)})
    return ra


def phong_cach(t: dict, van_ban: str) -> dict:
    """Suy phong cách từ số công khai (gợi ý, không phải cổng)."""
    tf = sorted(set(re.findall(r"\b(M1|M5|M15|M30|H1|H4|D1|W1)\b", van_ban)))
    giu = t.get("giu_lenh") or ""; goi_y = []
    if re.search(r"minute|second", giu): goi_y.append("scalping")
    elif re.search(r"hour", giu): goi_y.append("intraday")
    elif re.search(r"day|week", giu): goi_y.append("swing/giữ nhiều ngày")
    tai = t.get("tai_ky_quy_max_pct")
    if tai is not None and tai > 50: goi_y.append("tải ký quỹ cao (>50%) — dễ là lưới/martingale")
    dc = t.get("duong_cong") or {}
    if dc.get("thang_am_pct") is not None and dc["thang_am_pct"] < 10 and (t.get("dd_von_pct") or 0) > 2 * (t.get("dd_so_du_pct") or 0) + 5:
        goi_y.append("tháng hầu như luôn dương nhưng DD vốn ≫ DD số dư — dấu hiệu giữ lệnh âm (lưới/DCA)")
    return {"khung_nhac_den": tf, "goi_y": goi_y + [k for k in t.get("kieu") or []]}


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


def phan_loai_xuat_csv(http, than: str, url: str, url_cuoi: str | None = None, content_type: str = "") -> dict:
    """Phân loại phản hồi /export/history. Chuyển hướng đăng nhập không phải 0 lệnh."""
    from seeker.phan_loai_loi import phan_loai_http
    pl = phan_loai_http(http, than or "", url, url_cuoi, content_type=content_type)
    if pl["loai"] != "ok":
        pl["so_dong"] = None
        pl["khong_phai_khong_lenh"] = True
        return pl
    dau = (than or "").lstrip("\ufeff")
    if "<html" in dau[:600].lower() or "log in" in dau[:2500].lower():
        return {"loai": "auth", "ly_do": "history trả HTML/đăng nhập — không phải 0 lệnh",
                "http": http, "so_dong": None, "dung_mien": False, "stale": False, "khong_phai_khong_lenh": True}
    dong = [x for x in dau.splitlines() if x.strip()]
    if not dong or "symbol" not in dong[0].lower():
        return {"loai": "parse", "ly_do": "HTTP 200 nhưng không phải CSV lệnh",
                "http": http, "so_dong": None, "dung_mien": False, "stale": False}
    if len(dong) == 1:
        return {"loai": "no_data", "ly_do": "CSV hợp lệ, 0 dòng lệnh",
                "http": http, "so_dong": 0, "dung_mien": False, "stale": False}
    return {"loai": "ok", "ly_do": f"{len(dong) - 1} dòng lệnh", "http": http,
            "so_dong": len(dong) - 1, "dung_mien": False, "stale": False}


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
    giu = _sau(t, "Avg holding time:", r"([^\n]+)")
    tai = _so(_sau(t, "Max deposit load:", r"([\d.,]+)%"))
    tuan_lenh = _so(_sau(t, "Trades per week:"))
    mo_ta = ""
    mm2 = re.search(r"\nDescription\n(.*?)\n(?:Reviews|What's new)\n", t, re.S)
    i_mt = t.rfind("Please follow") if "Please follow" in t else -1
    mo_ta = (mm2.group(1) if mm2 else "") + (t[i_mt:i_mt + 3000] if i_mt >= 0 else "")
    ra = {
        "nen_tang": "MQL5", "id": sid, "url": f"{GOC}/en/signals/{sid}", "ten": ten, "mt": nen,
        "that_demo": that_demo, "may_chu": may_chu, "tuoi_thang": tuoi, "bat_dau": bat_dau,
        "tang_truong_pct": g, "cagr_pct": cagr_tu_tang_truong(g, tuoi), "dd_pct": dd,
        "dd_so_du_pct": dd_b, "dd_von_pct": dd_e, "so_lenh": int(so_lenh) if so_lenh else None,
        "symbol": sym, "kieu": kieu, "cap_nhat_cuoi": cuoi, "von_dau": von, "nap": nap, "rut": rut,
        "csv_cong_khai": False,
        "ghi_chu": "Growth MQL5 bỏ qua nạp/rút; thật/demo suy từ tên máy chủ; kiểu (grid/martingale/hedge) chỉ là từ có trong trang",
        "giu_lenh": giu, "tai_ky_quy_max_pct": tai, "lenh_moi_tuan": tuan_lenh, "duong_cong": duong_cong(h),
    }
    ra["phong_cach"] = phong_cach(ra, mo_ta)
    return ra
