# -*- coding: utf-8 -*-
"""phan_tich_dca.py - Bóc module DCA/recovery từ lịch sử lệnh (martingale/grid/DCA).

Không loại bỏ hệ martingale/grid. Tách:
  - entry ban đầu (điểm chọn lệnh đầu basket)
  - khoảng cách add-on (pips / ATR)
  - hệ số lot
  - số lớp tối đa
  - luật chốt basket / cắt lỗ
  - thời gian recovery
→ hồ sơ gọn cho hang_cho dich_boc với loai=dca_go_lenh (module tái sử dụng).

Pip/point: dùng cỡ pip theo lớp tài sản (XM specs), KHÔNG mặc định forex 0.0001
cho chỉ số/dầu/crypto. Hậu tố .sp/.prs/.ptb/# được chuẩn hoá trước khi gom basket.
"""
from __future__ import annotations

import json
import math
import os
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# ----- ngưỡng gom basket -----
# Chỉ gộp khi lệnh mới mở chồng lên lệnh đang mở, hoặc mở trong cửa sau khi basket đóng.
GAP_DONG_BASKET_GIAY = 2 * 3600
# Cửa tối đa giữa hai lần mở liên tiếp trong cùng basket (tránh dồn nhiều sóng độc lập).
GAP_MO_LIEN_TIEP_GIAY = 6 * 3600

# Hậu tố broker / account-type thường gặp trên FXBlue / XM
_SUFFIX_RE = re.compile(
    r"[\.#]?(cash|m|mini|micro|ecn|raw|pro|sp|prs|pri|ptb|std|cent)$",
    re.I,
)

# Pip theo trader (không phải MT5 point). XM: point chỉ số = 0.01 nhưng 1 pip chỉ số ≈ 1.0 điểm.
# Nguồn: config/chi_phi_do.json (XM) + quy ước FXBlue pips trên GER30/USOIL.
PIP_THEO_SYMBOL: dict[str, float] = {
    # Forex
    "EURUSD": 0.0001, "GBPUSD": 0.0001, "AUDUSD": 0.0001, "NZDUSD": 0.0001,
    "USDCAD": 0.0001, "USDCHF": 0.0001, "EURGBP": 0.0001, "EURCHF": 0.0001,
    "EURAUD": 0.0001, "EURCAD": 0.0001, "GBPAUD": 0.0001, "GBPCAD": 0.0001,
    "AUDCAD": 0.0001, "AUDCHF": 0.0001, "AUDNZD": 0.0001, "NZDCAD": 0.0001,
    "NZDCHF": 0.0001, "CADCHF": 0.0001,
    "USDJPY": 0.01, "EURJPY": 0.01, "GBPJPY": 0.01, "AUDJPY": 0.01,
    "CADJPY": 0.01, "CHFJPY": 0.01, "NZDJPY": 0.01,
    # Metals (pip truyền thống)
    "XAUUSD": 0.1, "GOLD": 0.1, "XAU": 0.1,
    "XAGUSD": 0.01, "SILVER": 0.01,
    # Indices — 1 pip = 1 index point (khớp FXBlue; XM point=0.01)
    "GER30": 1.0, "GER40": 1.0, "GER40CASH": 1.0, "DE40": 1.0, "DAX": 1.0,
    "US30": 1.0, "US30CASH": 1.0, "DJ30": 1.0, "WALLSTREET": 1.0,
    "US500": 1.0, "US500CASH": 1.0, "SPX": 1.0, "SP500": 1.0,
    "US100": 1.0, "NAS100": 1.0, "NAS100CASH": 1.0, "USTEC": 1.0,
    "UK100": 1.0, "UK100CASH": 1.0, "FTSE": 1.0,
    "FRA40": 1.0, "FRA40CASH": 1.0, "CAC": 1.0,
    "JP225": 1.0, "JP225CASH": 1.0, "NI225": 1.0, "JPN225": 1.0,
    "AUS200": 1.0, "AUS200CASH": 1.0, "HK50": 1.0, "HK50CASH": 1.0,
    "EU50": 1.0, "STOXX50": 1.0, "IT40": 1.0, "SPAIN35": 1.0,
    # Oil — XM OILCASH point=0.01 → 1 pip = 0.01
    "USOIL": 0.01, "UKOIL": 0.01, "WTI": 0.01, "BRENT": 0.01,
    "OIL": 0.01, "OILCASH": 0.01, "XTIUSD": 0.01, "XBRUSD": 0.01,
    "CRUDOIL": 0.01, "NGAS": 0.001,
    # Crypto
    "BTCUSD": 1.0, "BTC": 1.0, "XBTUSD": 1.0,
    "ETHUSD": 0.1, "ETH": 0.1,
}

# Ngưỡng sanity — flag/drop hồ sơ không đáng tin
SANITY_KHOANG_PIP_MAX = 500.0
SANITY_KHOANG_PIP_MIN = 0.05
SANITY_TP_PIP_ABS_MAX = 2000.0
SANITY_LOP_MAX = 40
SANITY_GIU_H_MAX = 24 * 30  # 30 ngày
SANITY_LOP_WARN = 25


def _iso_to_ts(s: str | None) -> float | None:
    if not s:
        return None
    t = str(s).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(t).timestamp()
    except ValueError:
        return None


def chuan_hoa_symbol(symbol: str | None) -> str:
    """Bỏ hậu tố broker (.sp/.prs/# /Cash…) → mã gốc để gom basket + pip."""
    s = (symbol or "").strip().upper()
    if not s:
        return ""
    # Tách # trước (USOIL#)
    s = s.replace("#", "")
    # Lặp bỏ hậu tố sau dấu . hoặc dính cuối
    for _ in range(4):
        if "." in s:
            base, suf = s.rsplit(".", 1)
            if _SUFFIX_RE.match(suf) or _SUFFIX_RE.match("." + suf):
                s = base
                continue
            # Hậu tố lạ ngắn (sp/prs/pri/ptb đã cover) — giữ nếu dài
            if len(suf) <= 4 and suf.isalpha():
                s = base
                continue
        m = _SUFFIX_RE.search(s)
        if m and m.start() > 0:
            s = s[: m.start()]
            continue
        break
    # Alias chỉ số / dầu
    aliases = {
        "GER40CASH": "GER40", "DE40": "GER40", "DAX": "GER40", "GER30": "GER30",
        "US500CASH": "US500", "SPX500": "US500", "SP500": "US500",
        "US30CASH": "US30", "DJ30": "US30",
        "NAS100CASH": "US100", "USTEC": "US100", "NAS100": "US100",
        "UK100CASH": "UK100", "FTSE100": "UK100",
        "FRA40CASH": "FRA40", "CAC40": "FRA40",
        "JP225CASH": "JP225", "NI225": "JP225",
        "OILCASH": "USOIL", "WTI": "USOIL", "XTIUSD": "USOIL", "CRUDOIL": "USOIL",
        "BRENT": "UKOIL", "XBRUSD": "UKOIL",
        "GOLD": "XAUUSD", "SILVER": "XAGUSD",
    }
    return aliases.get(s, s)


def _tai_pip_xm() -> dict[str, float]:
    """Đọc point XM từ chi_phi_do.json → quy đổi sang pip trader (point×10 FX, ×1 chỉ số lớn)."""
    cands = []
    env = os.environ.get("BRAIN_CHI_PHI_DO") or ""
    if env:
        cands.append(Path(env))
    here = Path(__file__).resolve().parent.parent
    cands += [
        here / "config" / "chi_phi_do.json",
        here.parent / "brain2" / "config" / "chi_phi_do.json",
    ]
    ra: dict[str, float] = {}
    for p in cands:
        if not p.is_file():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for k, v in d.items():
            if not isinstance(v, dict):
                continue
            if v.get("san") != "XM":
                continue
            pt = v.get("point")
            if not isinstance(pt, (int, float)) or pt <= 0:
                continue
            ten = chuan_hoa_symbol(str(k))
            # FX: 1 pip = 10 point (5/3 digits). Chỉ số/hàng hoá point nhỏ: pip ≈ 100×point
            # (0.01 → 1.0) trừ dầu/kim loại đã có trong bảng cứng.
            if ten in PIP_THEO_SYMBOL:
                continue
            gia = float(v.get("gia_luc_do") or 0)
            if ten.endswith("JPY") or "JPY" in ten:
                ra[ten] = float(pt) * 10.0  # 0.001 → 0.01
            elif gia and gia < 50 and float(pt) <= 1e-4:
                ra[ten] = float(pt) * 10.0  # FX
            elif float(pt) <= 0.01 and gia and gia > 50:
                ra[ten] = 1.0  # chỉ số
            else:
                ra[ten] = float(pt) * 10.0 if float(pt) < 0.01 else float(pt)
        break
    return ra


_PIP_XM_CACHE: dict[str, float] | None = None


def _pip_xm() -> dict[str, float]:
    global _PIP_XM_CACHE
    if _PIP_XM_CACHE is None:
        _PIP_XM_CACHE = _tai_pip_xm()
    return _PIP_XM_CACHE


def _pip_size(symbol: str) -> float:
    s = chuan_hoa_symbol(symbol)
    if not s:
        return 0.0001
    if s in PIP_THEO_SYMBOL:
        return PIP_THEO_SYMBOL[s]
    xm = _pip_xm()
    if s in xm:
        return xm[s]
    # Heuristic theo lớp
    if s.endswith("JPY") or "JPY" in s:
        return 0.01
    if s.startswith("XAU") or s in ("GOLD",):
        return 0.1
    if s.startswith("XAG"):
        return 0.01
    if any(x in s for x in ("OIL", "WTI", "BRENT", "XTI", "XBR")):
        return 0.01
    if any(x in s for x in ("BTC", "XBT")):
        return 1.0
    if any(x in s for x in ("ETH",)):
        return 0.1
    if any(x in s for x in (
            "GER", "US30", "US500", "US100", "NAS", "UK100", "FRA", "JP225",
            "AUS", "HK50", "DAX", "CAC", "FTSE", "STOXX", "NI225", "DJ")):
        return 1.0
    if len(s) >= 6 and s.isalpha():
        return 0.0001
    # Giá lớn → chỉ số/crypto
    return 0.0001


def _pips(symbol: str, a: float, b: float) -> float:
    ps = _pip_size(symbol)
    if ps <= 0:
        return 0.0
    return abs(float(a) - float(b)) / ps


def _tai_khoan(t: dict) -> str:
    for k in ("tai_khoan", "account", "login", "account_id", "mae"):
        # mae is not account — skip misleading
        pass
    for k in ("tai_khoan", "account", "login", "account_id"):
        v = t.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _gop_partial_close(lenh: list[dict]) -> list[dict]:
    """Gộp partial close: cùng symbol+chiều+gia_vao+luc_vao (hoặc cùng ticket) → 1 lớp.

    Lot = tổng; luc_ra/gia_ra = lần đóng cuối; loi = tổng.
    """
    if not lenh:
        return []
    nhom: dict[tuple, list] = defaultdict(list)
    for t in lenh:
        ticket = t.get("ticket")
        if ticket is not None and str(ticket).strip():
            key = ("t", str(ticket))
        else:
            key = (
                "p",
                chuan_hoa_symbol(t.get("symbol")),
                t.get("chieu"),
                round(float(t.get("gia_vao") or 0), 8),
                t.get("luc_vao") or "",
            )
        nhom[key].append(t)
    ra: list[dict] = []
    for ds in nhom.values():
        if len(ds) == 1:
            ra.append(ds[0])
            continue
        ds = sorted(ds, key=lambda x: x.get("luc_ra") or x.get("luc_vao") or "")
        goc = dict(ds[0])
        goc["lot"] = round(sum(float(x.get("lot") or 0) for x in ds), 4)
        goc["loi"] = round(sum(float(x.get("loi") or 0) for x in ds), 4)
        # đóng cuối
        cuoi = ds[-1]
        goc["luc_ra"] = cuoi.get("luc_ra")
        goc["gia_ra"] = cuoi.get("gia_ra")
        goc["_partial_n"] = len(ds)
        ra.append(goc)
    return sorted(ra, key=lambda x: x.get("luc_vao") or "")


def gom_basket(trades: list[dict]) -> list[dict]:
    """Gom lệnh thành basket theo account+symbol chuẩn+chiều, overlap / gap ngắn.

    Mỗi basket: {symbol, chieu, lenh[], mo_dau, dong_cuoi, so_lop, ...}.
    """
    theo: dict[tuple, list] = defaultdict(list)
    for t in sorted(trades, key=lambda x: x.get("luc_vao") or ""):
        sym = chuan_hoa_symbol(t.get("symbol"))
        ch = t.get("chieu")
        if not sym or ch not in (1, -1):
            continue
        tt = dict(t)
        tt["_sym_goc"] = t.get("symbol")
        tt["symbol"] = sym  # chuẩn hoá trong basket
        theo[(_tai_khoan(t), sym, ch)].append(tt)

    baskets: list[dict] = []
    for (acc, sym, ch), ds in theo.items():
        ds = _gop_partial_close(ds)
        cur: list[dict] = []
        cur_dong_max = 0.0
        cur_mo_cuoi = 0.0
        for t in ds:
            tv = _iso_to_ts(t.get("luc_vao")) or 0.0
            tr = _iso_to_ts(t.get("luc_ra")) or tv
            if cur:
                # Còn lệnh đang mở khi lệnh mới vào?
                con_mo = any(
                    (_iso_to_ts(x.get("luc_vao")) or 0) <= tv
                    and tv <= (_iso_to_ts(x.get("luc_ra")) or tv + 1e9)
                    for x in cur
                )
                gap_sau_dong = tv <= cur_dong_max + GAP_DONG_BASKET_GIAY
                gap_mo = (tv - cur_mo_cuoi) <= GAP_MO_LIEN_TIEP_GIAY
                if not (con_mo or (gap_sau_dong and gap_mo)):
                    baskets.append(_tom_tat_basket(sym, ch, cur, account=acc))
                    cur = []
                    cur_dong_max = 0.0
                    cur_mo_cuoi = 0.0
            cur.append(t)
            cur_dong_max = max(cur_dong_max, tr)
            cur_mo_cuoi = max(cur_mo_cuoi, tv)
        if cur:
            baskets.append(_tom_tat_basket(sym, ch, cur, account=acc))
    return [b for b in baskets if b.get("so_lop", 0) >= 1]


def _tom_tat_basket(sym: str, ch: int, lenh: list[dict], *, account: str = "") -> dict:
    lenh = sorted(lenh, key=lambda x: x.get("luc_vao") or "")
    lots = [float(x["lot"]) for x in lenh if x.get("lot")]
    gias = [float(x["gia_vao"]) for x in lenh if x.get("gia_vao") is not None]
    he_so = []
    for i in range(1, len(lots)):
        if lots[i - 1] > 0:
            he_so.append(lots[i] / lots[i - 1])
    khoang = []
    for i in range(1, len(gias)):
        kp = _pips(sym, gias[i], gias[i - 1])
        if kp > 1e-9:  # bỏ khoảng 0 (còn sót partial)
            khoang.append(kp)
    tv0 = _iso_to_ts(lenh[0].get("luc_vao"))
    trs = [_iso_to_ts(x.get("luc_ra")) for x in lenh]
    tr_max = max([t for t in trs if t], default=tv0)
    giu_h = ((tr_max - tv0) / 3600.0) if (tv0 and tr_max) else None
    loi = sum(float(x.get("loi") or 0) for x in lenh)
    co_rec = False
    if len(lenh) >= 2 and loi > 0 and any((x.get("loi") or 0) < 0 for x in lenh[:-1]):
        co_rec = True
    if he_so and statistics.median(he_so) >= 1.3:
        co_rec = True
    dong_gias = [(float(x["gia_ra"]), float(x["lot"])) for x in lenh
                 if x.get("gia_ra") is not None and x.get("lot")]
    if dong_gias and lots:
        gia_dong_tb = sum(g * l for g, l in dong_gias) / sum(l for _, l in dong_gias)
        n = min(len(gias), len(lots))
        gia_vao_tb = sum(gias[i] * lots[i] for i in range(n)) / sum(lots[:n])
        sign = 1 if (ch > 0 and gia_dong_tb >= gia_vao_tb) or (ch < 0 and gia_dong_tb <= gia_vao_tb) else -1
        tp_pip = _pips(sym, gia_dong_tb, gia_vao_tb) * sign
    else:
        tp_pip = None
    # Cờ partial: lot giảm mạnh + có khoảng 0 đã lọc
    partial = any(x.get("_partial_n") for x in lenh)
    if he_so and lots and lots[-1] < lots[0] * 0.5 and statistics.median(he_so) < 1.0:
        partial = True
    return {
        "symbol": sym,
        "chieu": ch,
        "account": account or None,
        "so_lop": len(lenh),
        "lot_dau": lots[0] if lots else None,
        "lot_cuoi": lots[-1] if lots else None,
        "he_so_lot_tb": round(statistics.median(he_so), 3) if he_so else 1.0,
        "he_so_lot_max": round(max(he_so), 3) if he_so else 1.0,
        "khoang_pip_tb": round(statistics.median(khoang), 1) if khoang else None,
        "khoang_pip_min": round(min(khoang), 1) if khoang else None,
        "khoang_pip_max": round(max(khoang), 1) if khoang else None,
        "loi_tong": round(loi, 2),
        "thoi_gian_giu_h": round(giu_h, 2) if giu_h is not None else None,
        "co_recovery": co_rec,
        "tp_basket_pip": round(tp_pip, 1) if tp_pip is not None else None,
        "pip_size": _pip_size(sym),
        "partial_close": partial,
        "mo_dau": lenh[0].get("luc_vao"),
        "dong_cuoi": max((x.get("luc_ra") or "") for x in lenh) or lenh[-1].get("luc_ra"),
        "lenh": lenh,
    }


def _basket_ok(b: dict) -> tuple[bool, list[str]]:
    """True nếu basket đủ tin để đưa vào thống kê module."""
    ly: list[str] = []
    k = b.get("khoang_pip_tb")
    if k is not None and k > SANITY_KHOANG_PIP_MAX:
        ly.append("khoang_pip_qua_lon")
    if k is not None and 0 < k < SANITY_KHOANG_PIP_MIN and b.get("so_lop", 0) >= 3:
        ly.append("khoang_pip_qua_nho")
    tp = b.get("tp_basket_pip")
    if tp is not None and abs(tp) > SANITY_TP_PIP_ABS_MAX:
        ly.append("tp_pip_qua_lon")
    if b.get("so_lop", 0) > SANITY_LOP_MAX:
        ly.append("qua_nhieu_lop")
    giu = b.get("thoi_gian_giu_h")
    if giu is not None and giu > SANITY_GIU_H_MAX and b.get("so_lop", 0) > SANITY_LOP_WARN:
        ly.append("giu_qua_lau_nhieu_lop")
    if b.get("partial_close") and (k is None or k == 0):
        ly.append("partial_close_khoang0")
    # Drop cứng: artifact rõ
    drop = any(x in ly for x in (
        "khoang_pip_qua_lon", "tp_pip_qua_lon", "qua_nhieu_lop", "partial_close_khoang0"))
    return (not drop), ly


def kiem_tra_sanity_ho_so(ho: dict) -> dict:
    """Gắn cờ sanity cấp hồ sơ; có thể đánh dau_do_tin=THAP/LOAI."""
    m = ho.get("module") or {}
    ly: list[str] = list(ho.get("sanity_ly_do") or [])
    if (m.get("khoang_pip_med") or 0) > SANITY_KHOANG_PIP_MAX:
        ly.append("module_khoang_pip_med_qua_lon")
    if abs(m.get("tp_basket_pip_med") or 0) > SANITY_TP_PIP_ABS_MAX:
        ly.append("module_tp_med_qua_lon")
    if (m.get("toi_da_lop_max") or 0) > SANITY_LOP_MAX:
        ly.append("module_lop_max_qua_lon")
    if (m.get("khoang_pip_med") is None) and (m.get("so_multi") or 0) >= 2:
        ly.append("module_thieu_khoang_pip")
    do_tin = "CAO"
    if ly:
        do_tin = "THAP"
    drop_keys = {"module_khoang_pip_med_qua_lon", "module_tp_med_qua_lon", "module_lop_max_qua_lon"}
    if drop_keys & set(ly):
        do_tin = "LOAI"
    return {"do_tin": do_tin, "ly_do": ly}


def thong_ke_dca(trades: list[dict]) -> dict:
    """Hồ sơ module DCA/recovery từ toàn bộ lệnh."""
    baskets = gom_basket(trades)
    multi_all = [b for b in baskets if b["so_lop"] >= 2]
    single = [b for b in baskets if b["so_lop"] == 1]

    flagged = []
    multi = []
    for b in multi_all:
        ok, ly = _basket_ok(b)
        if not ok:
            flagged.append({k: b[k] for k in b if k != "lenh"} | {"sanity_ly_do": ly})
        else:
            if ly:
                b = dict(b)
                b["sanity_canh_bao"] = ly
            multi.append(b)

    if not baskets:
        return {"so_basket": 0, "so_multi": 0, "module": {}, "do_tin": "LOAI",
                "sanity_ly_do": ["khong_co_basket"]}

    so_lop = [b["so_lop"] for b in multi] or [1]
    he_so = [b["he_so_lot_tb"] for b in multi if b.get("he_so_lot_tb")]
    khoang = [b["khoang_pip_tb"] for b in multi if b.get("khoang_pip_tb") is not None]
    tp = [b["tp_basket_pip"] for b in multi if b.get("tp_basket_pip") is not None]
    giu = [b["thoi_gian_giu_h"] for b in multi if b.get("thoi_gian_giu_h") is not None]
    rec = [b for b in multi if b.get("co_recovery")]
    loi_m = [b["loi_tong"] for b in multi]
    entry0 = []
    for b in multi:
        if b["lenh"]:
            entry0.append(b["lenh"][0])
    gio = Counter()
    for e in entry0:
        ts = _iso_to_ts(e.get("luc_vao"))
        if ts is not None:
            gio[datetime.fromtimestamp(ts, tz=timezone.utc).hour] += 1

    cat = [b for b in multi if b["loi_tong"] < 0]
    sym_pip = sorted({(b["symbol"], b.get("pip_size")) for b in multi_all})
    module = {
        "toi_da_lop_p90": _percentile(so_lop, 90) if multi else 0,
        "toi_da_lop_max": max(so_lop) if multi else 0,
        "he_so_lot_med": round(statistics.median(he_so), 3) if he_so else 1.0,
        "he_so_lot_p75": round(_percentile(he_so, 75), 3) if he_so else 1.0,
        "khoang_pip_med": round(statistics.median(khoang), 1) if khoang else None,
        "khoang_pip_p25": round(_percentile(khoang, 25), 1) if khoang else None,
        "khoang_pip_p75": round(_percentile(khoang, 75), 1) if khoang else None,
        "tp_basket_pip_med": round(statistics.median(tp), 1) if tp else None,
        "recovery_h_med": round(statistics.median(giu), 1) if giu else None,
        "recovery_h_p90": round(_percentile(giu, 90), 1) if giu else None,
        "ty_le_recovery": round(len(rec) / max(1, len(multi)), 3) if multi else 0.0,
        "ty_le_cat_lo": round(len(cat) / max(1, len(multi)), 3) if multi else 0.0,
        "loi_multi_tb": round(statistics.mean(loi_m), 2) if loi_m else 0.0,
        "gio_entry_top": gio.most_common(5),
        "ty_le_multi": round(len(multi_all) / max(1, len(baskets)), 3),
        "so_single": len(single),
        "so_multi": len(multi),
        "so_multi_raw": len(multi_all),
        "so_multi_loai": len(flagged),
        "pip_theo_symbol": [{"symbol": s, "pip": p} for s, p in sym_pip[:20]],
    }
    mau = []
    for b in sorted(multi, key=lambda x: -x["so_lop"])[:12]:
        mau.append({k: b[k] for k in b if k != "lenh"})
    ho = {
        "so_basket": len(baskets),
        "so_multi": len(multi),
        "so_multi_raw": len(multi_all),
        "so_flagged": len(flagged),
        "module": module,
        "mau_basket": mau,
        "mau_flagged": flagged[:8],
    }
    san = kiem_tra_sanity_ho_so(ho)
    ho["do_tin"] = san["do_tin"]
    ho["sanity_ly_do"] = san["ly_do"]
    return ho


def _percentile(xs: list, p: float) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    if len(ys) == 1:
        return float(ys[0])
    k = (len(ys) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(ys[int(k)])
    return float(ys[f] * (c - k) + ys[c] * (k - f))


def bang_text_dca(ho: dict, *, nguon: str, he_id: str) -> str:
    m = ho.get("module") or {}
    lines = [
        "## Module DCA/recovery (dich nguoc tu lich su)",
        "nguon=%s/%s so_basket=%s so_multi=%s so_multi_raw=%s do_tin=%s" % (
            nguon, he_id, ho.get("so_basket"), ho.get("so_multi"),
            ho.get("so_multi_raw"), ho.get("do_tin")),
        "toi_da_lop_p90=%s max=%s he_so_lot_med=%s p75=%s" % (
            m.get("toi_da_lop_p90"), m.get("toi_da_lop_max"),
            m.get("he_so_lot_med"), m.get("he_so_lot_p75")),
        "khoang_pip med=%s p25=%s p75=%s" % (
            m.get("khoang_pip_med"), m.get("khoang_pip_p25"), m.get("khoang_pip_p75")),
        "tp_basket_pip_med=%s recovery_h_med=%s p90=%s" % (
            m.get("tp_basket_pip_med"), m.get("recovery_h_med"), m.get("recovery_h_p90")),
        "ty_le_recovery=%s ty_le_cat_lo=%s ty_le_multi=%s loi_multi_tb=%s" % (
            m.get("ty_le_recovery"), m.get("ty_le_cat_lo"), m.get("ty_le_multi"),
            m.get("loi_multi_tb")),
        "gio_entry_top=%s pip_theo_symbol=%s" % (
            m.get("gio_entry_top"), m.get("pip_theo_symbol")),
        "sanity_ly_do=%s so_flagged=%s" % (ho.get("sanity_ly_do"), ho.get("so_flagged")),
        "",
        "## Mau basket (toi da 12, da loc sanity)",
        "sym|chieu|lop|lot0|lotN|he_so|khoang_pip|tp_pip|giu_h|loi|recovery|pip",
    ]
    for b in ho.get("mau_basket") or []:
        lines.append("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
            b.get("symbol"), b.get("chieu"), b.get("so_lop"),
            b.get("lot_dau"), b.get("lot_cuoi"), b.get("he_so_lot_tb"),
            b.get("khoang_pip_tb"), b.get("tp_basket_pip"),
            b.get("thoi_gian_giu_h"), b.get("loi_tong"), b.get("co_recovery"),
            b.get("pip_size")))
    if ho.get("mau_flagged"):
        lines += ["", "## Mau flagged (da loai)", "sym|lop|khoang|tp|ly_do"]
        for b in ho["mau_flagged"][:6]:
            lines.append("%s|%s|%s|%s|%s" % (
                b.get("symbol"), b.get("so_lop"), b.get("khoang_pip_tb"),
                b.get("tp_basket_pip"), b.get("sanity_ly_do")))
    return "\n".join(lines)


HE_THONG_DCA = (
    "Ban la ky su dich MODULE DCA/GO LENH (recovery). Doc HO SO DCA dich nguoc tu lich su "
    "trader cong khai va tra ve DUY NHAT mot JSON dung schema dich_boc, voi loai=\"dca_go_lenh\". "
    "Dien 'luoi' (che_do, buoc_diem, toi_da, he_so_lot, tp_diem, cat_lo_tien) va co_che vai_tro="
    "go_lenh mo ta: khoang add-on (pips/ATR), he so lot, max lop, basket TP, khi cat, cach chon "
    "diem DCA dau. 'spec' chi mo ta DIEU KIEN VAO LENH DAU (neu suy ra duoc); python co the mo ta "
    "ham go_lenh. Khong bia so lieu — dung dung thong ke trong ho so. Neu do_tin=LOAI/THAP, "
    "ghi chua_dich va khong bia buoc_diem. Day la MODULE ghep voi he vao khac, khong phai he full."
)


def tao_nhac_dca(ho: dict, *, nguon: str, he_id: str, url: str = "") -> str:
    bang = bang_text_dca(ho, nguon=nguon, he_id=he_id)
    return (
        "Tra JSON dang:\n"
        '{"loai": "dca_go_lenh",'
        ' "spec": [ /* dieu kien VAO LENH DAU neu co */ ],'
        ' "python": "",'
        ' "luoi": {"che_do": "mot_chieu|luoi_hai_chieu", "chieu": "mua|ban|hai",'
        ' "lot0": 0.01, "buoc_diem": 0, "toi_da": 0, "he_so_lot": 1.0, "tp_diem": 0,'
        ' "cat_lo_tien": 0, "hedge_khi_lo_pct": 0},'
        ' "co_che": [{"vai_tro": "go_lenh", "ten": "dca_recovery", "mo_ta": str, "tham": {}}],'
        ' "quan_tri": {"dca": str, "go_lenh": str, "tp": str, "sl": str},'
        ' "tham_so": {}, "chua_dich": []}\n'
        "NGUON dich nguoc DCA: %s/%s %s\n"
        "HO SO:\n```\n%s\n```"
    ) % (nguon, he_id, url or "", bang)
