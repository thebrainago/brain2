#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng 0 — lọc phí nhanh XM trước V1/V3.

Nguồn phí mặc định: /workspace/brain2/config/phi_xm_micro.json (ĐO).
NZDUSD thiếu trong file đó → fallback /workspace/brain2/config/chi_phi_do.json
khóa NZDUSDMICRO (cũng ĐO, ngày khác) và gắn nhãn NGUON_PHI.

Chấp nhận:
  - CSV lệnh MT5 (;): thoi_gian;deal;position;vao_ra;chieu;khoi_luong;gia;loi;swap;hoa_hong;phu
  - JSON tóm tắt: trades_per_yr, avg_hold_days, avg_gross_usd (hoặc avg_win_pips),
    symbol, side_buy_pct, lot, von, dd_pct (tuỳ chọn), cagr_pct (tuỳ chọn)

Loại khi:
  1) net expectancy sau phí ≤ 0
  2) edge/cost < 1.5
  3) không thể đạt CAGR kép > 10%/năm với DD < 80% (dùng số đo nếu có;
     không thì ƯỚC thô annual_net/von, gắn nhãn UOC)

Chạy:
  python3 loc_phi_nhanh.py --tu-ung-vien-v3
  python3 loc_phi_nhanh.py --lenh PATH --symbol GBPNZD --lot 10
  python3 loc_phi_nhanh.py --tom-tat PATH.json
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

BRAIN = Path("/workspace/brain2")
PHI_MICRO = BRAIN / "config" / "phi_xm_micro.json"
CHI_PHI_DO = BRAIN / "config" / "chi_phi_do.json"
EDGE_COST_MIN = 1.5
CAGR_MIN = 10.0
DD_MAX = 80.0
HOA_HONG_LOT = 0.0  # ĐO trong phi_xm_micro.json


@dataclass
class PhiSymbol:
    symbol: str
    swap_mua_diem: float
    swap_ban_diem: float
    spread_p90_gia: float
    point: float
    hop_dong: float
    nguon: str
    thieu_spread: bool = False


def _point_mac_dinh(sym: str) -> float:
    return 0.001 if sym.upper().endswith("JPY") else 1e-5


def load_phi(symbol: str) -> PhiSymbol:
    """Ưu tiên phi_xm_micro.json; fallback chi_phi_do cho symbol thiếu."""
    sym = symbol.upper().replace("MICRO", "").replace("#", "")
    micro = json.loads(PHI_MICRO.read_text(encoding="utf-8"))
    hoa = float(micro.get("_hoa_hong_lot") or 0.0)
    global HOA_HONG_LOT
    HOA_HONG_LOT = hoa

    if sym in micro and isinstance(micro[sym], dict):
        r = micro[sym]
        return PhiSymbol(
            symbol=sym,
            swap_mua_diem=float(r["swap_mua_diem"]),
            swap_ban_diem=float(r["swap_ban_diem"]),
            spread_p90_gia=float(r["spread_p90_gia"]),
            point=_point_mac_dinh(sym),
            hop_dong=1000.0,  # XM micro
            nguon="phi_xm_micro.json",
        )

    # fallback chi_phi_do
    do = json.loads(CHI_PHI_DO.read_text(encoding="utf-8"))
    key = sym + "MICRO"
    r = do.get(key) or do.get(sym)
    if not r:
        raise KeyError(f"Không có phí cho {sym} trong phi_xm_micro.json lẫn chi_phi_do.json")
    # spread: lấy từ _spread_bar_mt5 nếu có NZDUSDmicro
    spread = None
    sb = (do.get("_spread_bar_mt5") or {}).get("XM") or do.get("_spread_bar_mt5") or {}
    # cấu trúc có thể lồng; thử vài khóa
    for cand in (sym + "micro", sym, key):
        node = sb.get(cand) if isinstance(sb, dict) else None
        if isinstance(node, dict) and "chung" in node:
            spread = float(node["chung"])
            break
    # phi_xm thiếu NZDUSD — dùng H1 bps từ reports nếu cần
    thieu = spread is None
    if spread is None:
        # ước từ NZDUSD standard tick_spread_bps_p90 ~5.178 bps → giá ≈ bps/1e4 * mid
        # không bịa mid: nếu có gia_luc_do dùng nó
        gia = float(r.get("gia_luc_do") or 0) or None
        # không có bps trong chi_phi_do entry; để 0 và gắn thieu_spread
        spread = 0.0
    return PhiSymbol(
        symbol=sym,
        swap_mua_diem=float(r["swap_long"]),
        swap_ban_diem=float(r["swap_short"]),
        spread_p90_gia=float(spread),
        point=float(r.get("point") or _point_mac_dinh(sym)),
        hop_dong=float(r.get("contract_size") or 1000.0),
        nguon=f"chi_phi_do.json:{key}",
        thieu_spread=thieu,
    )


_QD_CACHE: dict[str, float] = {}


def _load_qd_rates() -> dict[str, float]:
    """Tỷ giá quote→USD từ chi_phi_do.json gia_luc_do (ĐO 13/09/2026)."""
    global _QD_CACHE
    if _QD_CACHE:
        return _QD_CACHE
    do = json.loads(CHI_PHI_DO.read_text(encoding="utf-8"))
    def gia(*keys):
        for k in keys:
            v = do.get(k) or {}
            if isinstance(v, dict) and v.get("gia_luc_do"):
                return float(v["gia_luc_do"])
        return None
    usdjpy = gia("USDJPYMICRO", "USDJPY")
    usdcad = gia("USDCADMICRO", "USDCAD")
    gbpusd = gia("GBPUSDMICRO", "GBPUSD")
    eurusd = gia("EURUSDMICRO", "EURUSD")
    nzdusd = gia("NZDUSDMICRO", "NZDUSD")
    audusd = gia("AUDUSDMICRO", "AUDUSD")
    # qd[quote_ccy] = nhân tố để ra USD
    qd = {"USD": 1.0}
    if usdjpy:
        qd["JPY"] = 1.0 / usdjpy
    if usdcad:
        qd["CAD"] = 1.0 / usdcad
    if gbpusd:
        qd["GBP"] = gbpusd
    if eurusd:
        qd["EUR"] = eurusd
    if nzdusd:
        qd["NZD"] = nzdusd
    if audusd:
        qd["AUD"] = audusd
    _QD_CACHE = qd
    return qd


def quote_ccy(symbol: str) -> str:
    s = symbol.upper().replace("MICRO", "").replace("#", "")
    if len(s) >= 6:
        return s[3:6]
    return "USD"


def qd_to_usd(symbol: str) -> float:
    q = quote_ccy(symbol)
    rates = _load_qd_rates()
    if q not in rates:
        raise KeyError(f"Chưa có tỷ giá ĐO quote→USD cho {q} (symbol {symbol})")
    return rates[q]


def spread_cost_usd(phi: PhiSymbol, lot: float, gia_tham_chieu: Optional[float] = None) -> float:
    """Chi phí spread 1 vòng (mở trả spread), quy về USD bằng gia_luc_do ĐO."""
    raw = abs(phi.spread_p90_gia) * phi.hop_dong * lot  # đơn vị quote
    return raw * qd_to_usd(phi.symbol)


def swap_cost_uoc_usd(phi: PhiSymbol, lot: float, hold_days: float, chieu: int) -> float:
    """ƯỚC swap POINTS → USD: diem * point * lot * hop_dong * dem * qd.
    dem ≈ hold_days * (7/5) vì Wed x3 (7 night-units / 5 đêm GD).
    """
    dem = max(hold_days, 0.0) * (7.0 / 5.0)
    diem = phi.swap_mua_diem if chieu > 0 else phi.swap_ban_diem
    raw = diem * phi.point * lot * phi.hop_dong * dem  # quote
    return raw * qd_to_usd(phi.symbol)


def parse_lenh_mt5(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    if not text:
        return []
    header = text[0].split(";")
    out = []
    for line in text[1:]:
        parts = line.split(";")
        if len(parts) < len(header):
            continue
        out.append(dict(zip(header, parts)))
    return out


def baskets_from_lenh(rows: list[dict]) -> list[dict]:
    pos: dict[str, list] = defaultdict(list)
    for r in rows:
        pos[r.get("position", "")].append(r)
    baskets = []
    for pid, deals in pos.items():
        ins = [d for d in deals if d.get("vao_ra") == "in"]
        outs = [d for d in deals if d.get("vao_ra") == "out"]
        if not ins or not outs:
            continue
        t0 = datetime.strptime(ins[0]["thoi_gian"], "%Y.%m.%d %H:%M:%S")
        t1 = datetime.strptime(outs[-1]["thoi_gian"], "%Y.%m.%d %H:%M:%S")
        hold = (t1 - t0).total_seconds() / 86400.0
        sw = sum(float(d.get("swap") or 0) for d in deals)
        pr = sum(float(d.get("loi") or 0) for d in outs)
        hh = sum(float(d.get("hoa_hong") or 0) for d in deals)
        lot = sum(float(d.get("khoi_luong") or 0) for d in ins)
        chieu = int(float(ins[0].get("chieu") or 1))
        baskets.append(
            dict(hold_days=hold, swap=sw, profit=pr, hoa_hong=hh, lot=lot, chieu=chieu, t0=t0, t1=t1)
        )
    return baskets


def danh_gia_tu_lenh(
    path: Path,
    symbol: str,
    von: float = 1000.0,
    cagr_pct: Optional[float] = None,
    dd_pct: Optional[float] = None,
    nhan: str = "",
) -> dict[str, Any]:
    phi = load_phi(symbol)
    rows = parse_lenh_mt5(path)
    baskets = baskets_from_lenh(rows)
    if not baskets:
        return {"he": nhan or path.name, "symbol": symbol, "ket_luan": "CHUA_DO", "ly_do": "0 rổ trong CSV lệnh"}

    holds = [b["hold_days"] for b in baskets]
    profits = [b["profit"] for b in baskets]
    swaps = [b["swap"] for b in baskets]
    lots = [b["lot"] for b in baskets]
    sides = [b["chieu"] for b in baskets]
    t0 = min(b["t0"] for b in baskets)
    t1 = max(b["t1"] for b in baskets)
    years = max((t1 - t0).total_seconds() / (365.25 * 86400.0), 1e-9)
    n = len(baskets)
    lot_med = st.median(lots)
    hold_med = st.median(holds)
    e_profit = st.mean(profits)
    e_swap = st.mean(swaps)
    net_e = e_profit + e_swap  # hoa hồng XM micro ĐO = 0
    buy_pct = 100.0 * sum(1 for s in sides if s > 0) / n

    # Ước spread p90 theo lot median (đã nằm trong profit MT5; dùng để tính tỉ lệ edge/cost)
    sp_cost = spread_cost_usd(phi, lot_med)
    # Ước swap từ file phí (đối chiếu với swap ĐO)
    swap_uoc_mua = swap_cost_uoc_usd(phi, lot_med, hold_med, +1)
    swap_uoc_ban = swap_cost_uoc_usd(phi, lot_med, hold_med, -1)
    swap_uoc = (buy_pct / 100.0) * swap_uoc_mua + (1 - buy_pct / 100.0) * swap_uoc_ban

    # cost = spread (ước) + |swap âm đo| trung bình + hoa hồng
    swap_cost_do = max(-e_swap, 0.0)
    total_cost = sp_cost + swap_cost_do + abs(HOA_HONG_LOT) * lot_med
    # gross edge ≈ profit (đã trừ spread) + spread_cost + (-swap nếu swap âm đã trừ riêng?)
    # profit MT5 chưa trừ swap (swap cột riêng) → gross trước mọi phí = profit + spread_cost
    gross_edge = e_profit + sp_cost
    ratio = (gross_edge / total_cost) if total_cost > 1e-12 else float("inf")

    trades_per_yr = n / years
    annual_net = net_e * trades_per_yr
    # CAGR đạt được?
    if cagr_pct is not None and dd_pct is not None:
        cagr_ok = cagr_pct > CAGR_MIN and dd_pct < DD_MAX
        cagr_nguon = "DO_tu_lot_json"
    else:
        # ƯỚC thô: nếu annual_net/von đủ lớn giả sử DD cho phép scale
        # Không bịa DD — chỉ kiểm tra annual_net > 0.10 * von
        cagr_ok = annual_net > 0.10 * von
        cagr_nguon = "UOC_annual_net_vs_10pct_von"
        cagr_pct = None
        dd_pct = None

    ly_do = []
    ket = "PASS"
    if net_e <= 0:
        ket = "REJECT"
        ly_do.append(f"net_E={net_e:.4f}≤0")
    if ratio < EDGE_COST_MIN:
        ket = "REJECT"
        ly_do.append(f"edge/cost={ratio:.3f}<{EDGE_COST_MIN}")
    if not cagr_ok:
        ket = "REJECT"
        ly_do.append("không đạt ngưỡng CAGR>10% & DD<80% (theo cổng)")
    if phi.thieu_spread:
        ly_do.append("THIEU_SPREAD_P90 trong nguồn phí (spread_cost=0)")

    return {
        "he": nhan or path.stem,
        "symbol": phi.symbol,
        "nguon_phi": phi.nguon,
        "ket_luan": ket,
        "ly_do": "; ".join(ly_do) if ly_do else "ok",
        "n_ro": n,
        "years": round(years, 3),
        "trades_per_yr": round(trades_per_yr, 2),
        "buy_pct": round(buy_pct, 1),
        "lot_med": lot_med,
        "hold_med_days": round(hold_med, 3),
        "hold_p90_days": round(sorted(holds)[max(int(0.9 * n) - 1, 0)], 3),
        "hold_max_days": round(max(holds), 3),
        "E_profit_usd": round(e_profit, 4),
        "E_swap_usd_DO": round(e_swap, 4),
        "net_E_usd": round(net_e, 4),
        "spread_cost_uoc_usd": round(sp_cost, 4),
        "swap_cost_uoc_file_usd": round(swap_uoc, 4),
        "total_cost_usd": round(total_cost, 4),
        "gross_edge_usd": round(gross_edge, 4),
        "edge_cost_ratio": round(ratio, 3),
        "annual_net_usd": round(annual_net, 2),
        "cagr_pct": cagr_pct,
        "dd_pct": dd_pct,
        "cagr_nguon": cagr_nguon,
        "von": von,
        "hoa_hong_lot": HOA_HONG_LOT,
    }


def danh_gia_tu_tom_tat(spec: dict[str, Any]) -> dict[str, Any]:
    """spec: symbol, trades_per_yr, avg_hold_days, avg_gross_usd|avg_win_pips,
    side_buy_pct, lot, von, cagr_pct?, dd_pct?"""
    phi = load_phi(spec["symbol"])
    lot = float(spec.get("lot") or 1.0)
    hold = float(spec["avg_hold_days"])
    buy_pct = float(spec.get("side_buy_pct") or 50.0)
    von = float(spec.get("von") or 1000.0)
    tpy = float(spec["trades_per_yr"])

    if "avg_gross_usd" in spec:
        gross = float(spec["avg_gross_usd"])
    elif "avg_win_pips" in spec:
        # 1 pip FX 5-digit = 10*point; tiền ≈ pips*10*point*hop_dong*lot
        pips = float(spec["avg_win_pips"])
        gross = pips * 10 * phi.point * phi.hop_dong * lot
    else:
        raise ValueError("cần avg_gross_usd hoặc avg_win_pips")

    sp = spread_cost_usd(phi, lot)
    sw = (buy_pct / 100.0) * swap_cost_uoc_usd(phi, lot, hold, +1) + (
        1 - buy_pct / 100.0
    ) * swap_cost_uoc_usd(phi, lot, hold, -1)
    hh = abs(HOA_HONG_LOT) * lot
    # gross ở đây = trước phí; net = gross - spread - (-swap nếu swap âm) - hh
    # swap_cost_uoc đã mang dấu (âm = trả)
    net_e = gross - sp + sw - hh  # sw âm → trừ
    total_cost = sp + max(-sw, 0.0) + hh
    ratio = (gross / total_cost) if total_cost > 1e-12 else float("inf")
    annual_net = net_e * tpy

    cagr_pct = spec.get("cagr_pct")
    dd_pct = spec.get("dd_pct")
    if cagr_pct is not None and dd_pct is not None:
        cagr_ok = float(cagr_pct) > CAGR_MIN and float(dd_pct) < DD_MAX
        cagr_nguon = "DO_tu_input"
    else:
        cagr_ok = annual_net > 0.10 * von
        cagr_nguon = "UOC_annual_net_vs_10pct_von"

    ly_do = []
    ket = "PASS"
    if net_e <= 0:
        ket = "REJECT"
        ly_do.append(f"net_E={net_e:.4f}≤0")
    if ratio < EDGE_COST_MIN:
        ket = "REJECT"
        ly_do.append(f"edge/cost={ratio:.3f}<{EDGE_COST_MIN}")
    if not cagr_ok:
        ket = "REJECT"
        ly_do.append("không đạt ngưỡng CAGR>10% & DD<80%")
    if phi.thieu_spread:
        ly_do.append("THIEU_SPREAD_P90")

    return {
        "he": spec.get("he") or spec.get("id") or phi.symbol,
        "symbol": phi.symbol,
        "nguon_phi": phi.nguon,
        "ket_luan": ket,
        "ly_do": "; ".join(ly_do) if ly_do else "ok",
        "trades_per_yr": tpy,
        "buy_pct": buy_pct,
        "lot_med": lot,
        "hold_med_days": hold,
        "E_gross_usd": round(gross, 4),
        "spread_cost_uoc_usd": round(sp, 4),
        "swap_cost_uoc_file_usd": round(sw, 4),
        "net_E_usd": round(net_e, 4),
        "total_cost_usd": round(total_cost, 4),
        "edge_cost_ratio": round(ratio, 3),
        "annual_net_usd": round(annual_net, 2),
        "cagr_pct": cagr_pct,
        "dd_pct": dd_pct,
        "cagr_nguon": cagr_nguon,
        "von": von,
    }


# --- ứng viên V3 cố định -------------------------------------------------
V3_LENH = [
    # he, path, symbol, von, cagr_k1, dd_k1 (từ hang_doi/da_test lot_*.json k=1)
    ("skea61c", BRAIN / "reports/ong_dan/ket_qua_mt5/od_skea61c21a2049_XM_CSV_vao.csv_lenh_mt5.csv", "CADJPY", 1000, 13.3, 10.74),
    ("ghep_0bf2", BRAIN / "reports/ong_dan/ket_qua_mt5/od_ghep0bf2c31fbfc9dea0_XM_CSV_vao.csv_lenh_mt5.csv", "GBPCAD", 1000, 65.079, 47.16),
    ("ghepe9b4", BRAIN / "reports/ong_dan/ket_qua_mt5/od_ghepe9b41c33d4deee54_XM_CSV_vao.csv_lenh_mt5.csv", "GBPNZD", 1000, 129.595, 31.46),
    ("ghep60ff", BRAIN / "reports/ong_dan/ket_qua_mt5/od_ghep60ff9350c26c63ee_XM_CSV_vao.csv_lenh_mt5.csv", "GBPCAD", 1000, 64.529, 20.18),
    ("2600ea39", BRAIN / "reports/ong_dan/ket_qua_mt5/od_2600ea39abbd7b0f_XM_CSV_vao.csv_lenh_mt5.csv", "GBPNZD", 1000, 38.28, 15.8),
    ("mql5344", BRAIN / "reports/ong_dan/ket_qua_mt5/od_mql5344ed0d8ab12c7f0_XM_CSV_vao.csv_lenh_mt5.csv", "NZDUSD", 1000, 17.485, 44.82),
    ("3279", BRAIN / "reports/ong_dan/ket_qua_mt5/od_skea3279057100_XM_CSV_vao.csv_lenh_mt5.csv", "EURGBP", 1000, 71.615, 52.14),
]


def chay_v3() -> list[dict]:
    ra = []
    for he, path, sym, von, cagr, dd in V3_LENH:
        if not path.exists():
            ra.append({"he": he, "symbol": sym, "ket_luan": "CHUA_DO", "ly_do": f"thiếu file {path}"})
            continue
        ra.append(danh_gia_tu_lenh(path, sym, von=von, cagr_pct=cagr, dd_pct=dd, nhan=he))
    # brainxlmrz: không có CSV lệnh trong repo; dùng TRI_NHO
    tri = BRAIN / "TRI_NHO/dac_diem_he/brainxlmrz.json"
    if tri.exists():
        d = json.loads(tri.read_text(encoding="utf-8"))
        chay0 = (d.get("chay") or [{}])[0]
        # Không có hold/trades đủ → chỉ cổng CAGR/DD đã đo; phí CHƯA tách được
        cagr = chay0.get("cagr_pct")
        dd = chay0.get("dd_pct")
        ket = "PASS" if (cagr is not None and dd is not None and cagr > CAGR_MIN and dd < DD_MAX) else "REJECT"
        ly = "không có CSV lệnh để tách spread/swap; chỉ cổng CAGR/DD salvage"
        if cagr is None or dd is None:
            ket = "CHUA_DO"
        elif not (cagr > CAGR_MIN and dd < DD_MAX):
            ly = f"cagr={cagr} dd={dd} không đạt"
        ra.append(
            {
                "he": "brainxlmrz",
                "symbol": "GBPUSD",
                "nguon_phi": "CHUA_TACH (salvage MT5 đã gồm phí)",
                "ket_luan": ket,
                "ly_do": ly,
                "cagr_pct": cagr,
                "dd_pct": dd,
                "cagr_nguon": "DO_tu_TRI_NHO_salvage",
                "edge_cost_ratio": None,
                "net_E_usd": None,
            }
        )
    else:
        ra.append({"he": "brainxlmrz", "ket_luan": "CHUA_DO", "ly_do": "thiếu TRI_NHO"})
    # EMA_Cross_Demo: chưa có kết quả
    ra.append(
        {
            "he": "EMA_Cross_Demo",
            "symbol": "?",
            "ket_luan": "CHUA_DO",
            "ly_do": "chưa có CSV lệnh / lot_*.json trong repo (mới từ nhánh Seeker, chờ V1)",
        }
    )
    return ra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tu-ung-vien-v3", action="store_true")
    ap.add_argument("--lenh", type=Path)
    ap.add_argument("--symbol", type=str)
    ap.add_argument("--lot", type=float, default=None)
    ap.add_argument("--von", type=float, default=1000.0)
    ap.add_argument("--cagr", type=float, default=None)
    ap.add_argument("--dd", type=float, default=None)
    ap.add_argument("--tom-tat", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    results = []
    if args.tu_ung_vien_v3:
        results = chay_v3()
    elif args.lenh:
        if not args.symbol:
            raise SystemExit("--symbol bắt buộc với --lenh")
        results = [
            danh_gia_tu_lenh(
                args.lenh, args.symbol, von=args.von, cagr_pct=args.cagr, dd_pct=args.dd
            )
        ]
    elif args.tom_tat:
        spec = json.loads(args.tom_tat.read_text(encoding="utf-8"))
        results = [danh_gia_tu_tom_tat(spec)]
    else:
        ap.print_help()
        raise SystemExit(2)

    text = json.dumps(results, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"# wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
