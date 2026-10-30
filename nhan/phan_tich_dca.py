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
"""
from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Iterable

# ----- ngưỡng gom basket -----
CUA_SO_BASKET_GIAY = 14 * 24 * 3600   # lệnh cùng symbol+chiều trong 14 ngày có thể cùng basket
GAP_DONG_BASKET_GIAY = 2 * 3600      # đóng trong cửa 2h → cùng exit basket
PIP_THEO_SYMBOL = {
    "XAUUSD": 0.1, "XAGUSD": 0.01, "BTCUSD": 1.0, "US500": 0.1, "US500CASH": 0.1,
}


def _iso_to_ts(s: str | None) -> float | None:
    if not s:
        return None
    t = str(s).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(t).timestamp()
    except ValueError:
        return None


def _pip_size(symbol: str) -> float:
    s = (symbol or "").upper().split(".")[0].split("#")[0]
    if s in PIP_THEO_SYMBOL:
        return PIP_THEO_SYMBOL[s]
    if s.endswith("JPY") or "JPY" in s:
        return 0.01
    if len(s) >= 6:
        return 0.0001
    return 0.0001


def _pips(symbol: str, a: float, b: float) -> float:
    return abs(float(a) - float(b)) / _pip_size(symbol)


def gom_basket(trades: list[dict]) -> list[dict]:
    """Gom lệnh thành basket theo symbol+chiều, mở chồng / đóng gần nhau.

    Mỗi basket: {symbol, chieu, lenh[], mo_dau, dong_cuoi, so_lop, lot_dau, lot_cuoi,
                 he_so_lot_tb, khoang_pip, loi_tong, thoi_gian_giu_h, co_recovery}.
    """
    theo: dict[tuple, list] = defaultdict(list)
    for t in sorted(trades, key=lambda x: x.get("luc_vao") or ""):
        theo[(t.get("symbol"), t.get("chieu"))].append(t)

    baskets: list[dict] = []
    for (sym, ch), ds in theo.items():
        if not sym or ch not in (1, -1):
            continue
        # Chia chuỗi: gap mở > CUA_SO → basket mới; hoặc sau khi mọi lệnh trước đã đóng
        cur: list[dict] = []
        cur_dong_max = 0.0
        for t in ds:
            tv = _iso_to_ts(t.get("luc_vao")) or 0.0
            tr = _iso_to_ts(t.get("luc_ra")) or tv
            if cur and tv - (_iso_to_ts(cur[0].get("luc_vao")) or 0) > CUA_SO_BASKET_GIAY:
                baskets.append(_tom_tat_basket(sym, ch, cur))
                cur = []
            elif cur and tv > cur_dong_max + GAP_DONG_BASKET_GIAY and all(
                    _iso_to_ts(x.get("luc_ra")) for x in cur):
                # tất cả đã đóng và lệnh mới mở sau
                baskets.append(_tom_tat_basket(sym, ch, cur))
                cur = []
            cur.append(t)
            cur_dong_max = max(cur_dong_max, tr)
        if cur:
            baskets.append(_tom_tat_basket(sym, ch, cur))
    return [b for b in baskets if b.get("so_lop", 0) >= 1]


def _tom_tat_basket(sym: str, ch: int, lenh: list[dict]) -> dict:
    lenh = sorted(lenh, key=lambda x: x.get("luc_vao") or "")
    lots = [float(x["lot"]) for x in lenh if x.get("lot")]
    gias = [float(x["gia_vao"]) for x in lenh if x.get("gia_vao") is not None]
    he_so = []
    for i in range(1, len(lots)):
        if lots[i - 1] > 0:
            he_so.append(lots[i] / lots[i - 1])
    khoang = []
    for i in range(1, len(gias)):
        khoang.append(_pips(sym, gias[i], gias[i - 1]))
    tv0 = _iso_to_ts(lenh[0].get("luc_vao"))
    trs = [_iso_to_ts(x.get("luc_ra")) for x in lenh]
    tr_max = max([t for t in trs if t], default=tv0)
    giu_h = ((tr_max - tv0) / 3600.0) if (tv0 and tr_max) else None
    loi = sum(float(x.get("loi") or 0) for x in lenh)
    # recovery: có lệnh lỗ rồi basket kết thúc dương, hoặc lot tăng sau lỗ
    co_rec = False
    if len(lenh) >= 2 and loi > 0 and any((x.get("loi") or 0) < 0 for x in lenh[:-1]):
        co_rec = True
    if he_so and statistics.median(he_so) >= 1.3:
        co_rec = True
    # điểm chốt: giá đóng trung bình gia quyền lot vs giá vào TB
    dong_gias = [(float(x["gia_ra"]), float(x["lot"])) for x in lenh
                 if x.get("gia_ra") is not None and x.get("lot")]
    if dong_gias and lots:
        gia_dong_tb = sum(g * l for g, l in dong_gias) / sum(l for _, l in dong_gias)
        gia_vao_tb = sum(gias[i] * lots[i] for i in range(min(len(gias), len(lots)))) / sum(lots[:len(gias)])
        tp_pip = _pips(sym, gia_dong_tb, gia_vao_tb) * (1 if (ch > 0 and gia_dong_tb >= gia_vao_tb) or (ch < 0 and gia_dong_tb <= gia_vao_tb) else -1)
    else:
        tp_pip = None
    return {
        "symbol": sym,
        "chieu": ch,
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
        "mo_dau": lenh[0].get("luc_vao"),
        "dong_cuoi": lenh[-1].get("luc_ra"),
        "lenh": lenh,
    }


def thong_ke_dca(trades: list[dict]) -> dict:
    """Hồ sơ module DCA/recovery từ toàn bộ lệnh."""
    baskets = gom_basket(trades)
    multi = [b for b in baskets if b["so_lop"] >= 2]
    single = [b for b in baskets if b["so_lop"] == 1]
    if not baskets:
        return {"so_basket": 0, "so_multi": 0, "module": {}}

    so_lop = [b["so_lop"] for b in multi] or [1]
    he_so = [b["he_so_lot_tb"] for b in multi if b.get("he_so_lot_tb")]
    khoang = [b["khoang_pip_tb"] for b in multi if b.get("khoang_pip_tb")]
    tp = [b["tp_basket_pip"] for b in multi if b.get("tp_basket_pip") is not None]
    giu = [b["thoi_gian_giu_h"] for b in multi if b.get("thoi_gian_giu_h") is not None]
    rec = [b for b in multi if b.get("co_recovery")]
    loi_m = [b["loi_tong"] for b in multi]
    # entry đầu: phân bố phiên / chiều
    entry0 = []
    for b in multi:
        if b["lenh"]:
            entry0.append(b["lenh"][0])
    gio = Counter()
    for e in entry0:
        ts = _iso_to_ts(e.get("luc_vao"))
        if ts is not None:
            gio[datetime.fromtimestamp(ts, tz=timezone.utc).hour] += 1

    # cắt lỗ: basket multi lỗ
    cat = [b for b in multi if b["loi_tong"] < 0]
    module = {
        "toi_da_lop_p90": _percentile(so_lop, 90),
        "toi_da_lop_max": max(so_lop),
        "he_so_lot_med": round(statistics.median(he_so), 3) if he_so else 1.0,
        "he_so_lot_p75": round(_percentile(he_so, 75), 3) if he_so else 1.0,
        "khoang_pip_med": round(statistics.median(khoang), 1) if khoang else None,
        "khoang_pip_p25": round(_percentile(khoang, 25), 1) if khoang else None,
        "khoang_pip_p75": round(_percentile(khoang, 75), 1) if khoang else None,
        "tp_basket_pip_med": round(statistics.median(tp), 1) if tp else None,
        "recovery_h_med": round(statistics.median(giu), 1) if giu else None,
        "recovery_h_p90": round(_percentile(giu, 90), 1) if giu else None,
        "ty_le_recovery": round(len(rec) / max(1, len(multi)), 3),
        "ty_le_cat_lo": round(len(cat) / max(1, len(multi)), 3),
        "loi_multi_tb": round(statistics.mean(loi_m), 2) if loi_m else 0.0,
        "gio_entry_top": gio.most_common(5),
        "ty_le_multi": round(len(multi) / max(1, len(baskets)), 3),
        "so_single": len(single),
        "so_multi": len(multi),
    }
    # mẫu basket (gọn, bỏ list lệnh đầy đủ)
    mau = []
    for b in sorted(multi, key=lambda x: -x["so_lop"])[:12]:
        mau.append({k: b[k] for k in b if k != "lenh"})
    return {
        "so_basket": len(baskets),
        "so_multi": len(multi),
        "module": module,
        "mau_basket": mau,
    }


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
        "nguon=%s/%s so_basket=%s so_multi=%s" % (nguon, he_id, ho.get("so_basket"), ho.get("so_multi")),
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
        "gio_entry_top=%s" % (m.get("gio_entry_top"),),
        "",
        "## Mau basket (toi da 12)",
        "sym|chieu|lop|lot0|lotN|he_so|khoang_pip|tp_pip|giu_h|loi|recovery",
    ]
    for b in ho.get("mau_basket") or []:
        lines.append("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
            b.get("symbol"), b.get("chieu"), b.get("so_lop"),
            b.get("lot_dau"), b.get("lot_cuoi"), b.get("he_so_lot_tb"),
            b.get("khoang_pip_tb"), b.get("tp_basket_pip"),
            b.get("thoi_gian_giu_h"), b.get("loi_tong"), b.get("co_recovery")))
    return "\n".join(lines)


HE_THONG_DCA = (
    "Ban la ky su dich MODULE DCA/GO LENH (recovery). Doc HO SO DCA dich nguoc tu lich su "
    "trader cong khai va tra ve DUY NHAT mot JSON dung schema dich_boc, voi loai=\"dca_go_lenh\". "
    "Dien 'luoi' (che_do, buoc_diem, toi_da, he_so_lot, tp_diem, cat_lo_tien) va co_che vai_tro="
    "go_lenh mo ta: khoang add-on (pips/ATR), he so lot, max lop, basket TP, khi cat, cach chon "
    "diem DCA dau. 'spec' chi mo ta DIEU KIEN VAO LENH DAU (neu suy ra duoc); python co the mo ta "
    "ham go_lenh. Khong bia so lieu — dung dung thong ke trong ho so. Day la MODULE ghep voi he "
    "vao khac, khong phai he full."
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
