#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng 0 XM trên lịch sử nguồn khác (FX Blue + Collective2). Không commit secrets."""
from __future__ import annotations

import csv
import json
import statistics as st
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/workspace/quy_trinh_v3")
from phan_tich_mql5_hist import (
    Trade,
    load_phi,
    xm_cost_price,
    detect_grid_martingale,
    _merge_partials,
    map_symbol,
    EDGE_COST_MIN,
    CAGR_MIN,
    DD_MAX,
)

OUT = Path("/workspace/quy_trinh_v3")
FXB = Path("/workspace/nguon_khac/fxblue")
C2 = Path("/workspace/nguon_khac/collective2")


def pip_size(sym: str) -> float:
    s = (sym or "").upper()
    if s in ("XAUUSD", "GOLD"):
        return 0.01
    if s in ("BTCUSD", "ETHUSD"):
        return 1.0
    if s in ("US30", "US100", "US500", "NAS100", "GER40", "DE40", "USTEC"):
        return 1.0
    if s.endswith("JPY"):
        return 0.01
    return 0.0001


def _f(v, default=0.0):
    try:
        if v is None:
            return default
        s = str(v).strip().replace(",", "")
        if s == "" or s.lower() in ("nan", "none", "n/a"):
            return default
        return float(s)
    except Exception:
        return default


def _parse_dt(s: str):
    s = (s or "").strip().strip('"')
    if not s or s.startswith("1970"):
        return None
    for fmt in (
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def parse_fxblue(path: Path) -> list[Trade]:
    text = path.read_text(errors="ignore")
    if "Only allowed when logged in" in text[:800]:
        return []
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("sep=")]
    if not lines or "Type,Ticket" not in lines[0]:
        return []
    rows = list(csv.DictReader(lines))
    trades: list[Trade] = []
    for r in rows:
        typ = (r.get("Type") or "").strip().lower()
        if not typ.startswith("closed"):
            continue
        raw = (r.get("Symbol") or "").strip().upper()
        if not raw or raw in ("SUMMARY", "NAN"):
            continue
        # strip broker suffix P (AUDCADP)
        if raw.endswith("P") and len(raw) == 7 and raw[:6].isalpha():
            raw = raw[:-1]
        # strip PRO / MINI / ECN style suffixes
        raw = raw.rstrip(".+")
        for suf in ("PRO", "MINI", "ECN", "RAW", "STD", "INS", "PI", ".A", ".B", ".I", ".P", ".R", ".M", ".S", ".INS", ".PI"):
            if raw.endswith(suf) and len(raw) > len(suf) + 2:
                raw = raw[: -len(suf)].rstrip(".")
                break
        # hậu tố .R / .m còn sót (XAUUSD.R)
        if "." in raw and len(raw.split(".")[0]) >= 6:
            base, _, rest = raw.partition(".")
            if rest.upper() in ("R", "M", "S", "A", "B", "I", "P", "PRO", "MINI", "ECN", "RAW", "INS", "STD", "PI", "C", "Z", "E", "T", "Q"):
                raw = base
        mapped = map_symbol(raw) or raw
        if mapped.startswith("OTHER:"):
            mapped = mapped.split(":", 1)[1]
        t0 = _parse_dt(r.get("Open time") or r.get("Open date") or "")
        t1 = _parse_dt(r.get("Close time") or r.get("Close date") or "")
        if not t0 or not t1 or t1 <= t0:
            continue
        side = (r.get("Buy/sell") or "").strip().lower()
        chieu = 1 if side.startswith("buy") else -1
        po = _f(r.get("Open price"))
        pc = _f(r.get("Close price"))
        if po <= 0 or pc <= 0:
            continue
        sl = _f(r.get("S/L"))
        tp = _f(r.get("T/P"))
        trades.append(
            Trade(
                t_open=t0,
                t_close=t1,
                symbol_raw=raw,
                symbol=mapped,
                chieu=chieu,
                volume=_f(r.get("Lots")),
                price_open=po,
                price_close=pc,
                sl=sl if abs(sl) > 1e-12 else None,
                tp=tp if abs(tp) > 1e-12 else None,
                commission=_f(r.get("Commission")),
                swap=_f(r.get("Swap")),
                profit=_f(r.get("Profit")),
                comment=str(r.get("Order comment") or ""),
                has_sl=abs(sl) > 1e-12,
                has_tp=abs(tp) > 1e-12,
            )
        )
    return trades


def parse_c2(path: Path) -> list[Trade]:
    rows = list(csv.DictReader(path.open(encoding="utf-8", errors="ignore")))
    trades: list[Trade] = []
    for r in rows:
        raw = (r.get("Symbol") or "").strip().upper().replace("/", "")
        if not raw:
            continue
        # skip non-FX (stocks/futures)
        if len(raw) != 6 and raw not in ("XAUUSD", "XAGUSD", "BTCUSD"):
            # allow XXXYYY only
            if not (len(raw) == 6 and raw.isalpha()):
                continue
        mapped = map_symbol(raw) or raw
        t0 = _parse_dt(r.get("Open Time ET") or "")
        t1 = _parse_dt(r.get("Closed Time ET") or "")
        if not t0 or not t1 or t1 <= t0:
            continue
        side = (r.get("Side") or "").strip().upper()
        chieu = 1 if side.startswith("LONG") or side == "BUY" else -1
        po = _f(r.get("Avg Price Open"))
        pc = _f(r.get("Avg Price Closed"))
        if po <= 0 or pc <= 0:
            continue
        qty = abs(_f(r.get("Qty Closed") or r.get("Qty Open") or 1))
        # C2 forex qty often in units (k); treat as micro-lot proxy volume=qty/1000
        vol = qty / 1000.0 if qty >= 1 else qty
        trades.append(
            Trade(
                t_open=t0,
                t_close=t1,
                symbol_raw=raw,
                symbol=mapped,
                chieu=chieu,
                volume=vol,
                price_open=po,
                price_close=pc,
                sl=None,
                tp=None,
                commission=0.0,
                swap=0.0,
                profit=_f(r.get("Trade P/L")),
                comment="",
                has_sl=False,
                has_tp=False,
            )
        )
    return trades


def analyze_subset(trades: list[Trade], label: str) -> dict:
    if not trades:
        return dict(label=label, n=0, ket_luan="CHUA_DO", ly_do="0 lệnh")

    t0 = min(t.t_open for t in trades)
    t1 = max(t.t_close for t in trades)
    years = max((t1 - t0).total_seconds() / (365.25 * 86400), 1e-9)
    holds = [(t.t_close - t.t_open).total_seconds() / 86400 for t in trades]
    buy_pct = 100.0 * sum(1 for t in trades if t.chieu > 0) / len(trades)

    grid = detect_grid_martingale(trades)
    merged = _merge_partials(trades)
    by_sym: dict[str, list] = defaultdict(list)
    for tr in merged:
        by_sym[tr.symbol].append(tr)
    max_same = 0
    for sym, ts in by_sym.items():
        events = []
        for tr in ts:
            events.append((tr.t_open, tr.chieu, 1))
            events.append((tr.t_close, tr.chieu, -1))
        events.sort(key=lambda x: (x[0], -x[2]))
        cur_b = cur_s = 0
        for _, ch, d in events:
            if ch > 0:
                cur_b += d
            else:
                cur_s += d
            max_same = max(max_same, cur_b, cur_s)
    sl_pct = 100.0 * sum(1 for t in trades if t.has_sl) / len(trades)
    if max_same >= 8 or (max_same >= 4 and sl_pct < 20):
        hang = "luoi"
    elif 3 <= max_same <= 7 and sl_pct >= 20:
        hang = "pyramid"
    elif max_same <= 2:
        hang = "don_le"
    else:
        hang = "pyramid" if sl_pct >= 20 else "luoi"

    nets = []
    grosses = []
    costs = []
    sps = []
    sws = []
    missing = Counter()
    for t in trades:
        phi = load_phi(t.symbol)
        if phi is None:
            missing[t.symbol] += 1
            continue
        hold = (t.t_close - t.t_open).total_seconds() / 86400
        gross = t.chieu * (t.price_close - t.price_open)
        sp, sw, cost = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
        net = gross - sp + sw
        nets.append(net)
        grosses.append(gross)
        costs.append(cost)
        sps.append(sp)
        sws.append(sw)

    fee_cover = len(nets) / len(trades) if trades else 0.0
    if len(nets) < max(10, 0.5 * len(trades)):
        ket = "CHUA_DO"
        ly = f"phí cover {len(nets)}/{len(trades)}; thiếu {dict(missing)}"
        net_e = ratio = sp_e = sw_e = cost_e = gross_e = None
    else:
        net_e = float(st.mean(nets))
        gross_e = float(st.mean(grosses))
        cost_e = float(st.mean(costs))
        sp_e = float(st.mean(sps))
        sw_e = float(st.mean(sws))
        ratio = (gross_e / cost_e) if cost_e > 1e-15 else float("inf")
        ket = "PASS"
        ly_parts = []
        if net_e <= 0:
            ket = "REJECT"
            ly_parts.append(f"net_E_price={net_e:.6g}≤0")
        if ratio < EDGE_COST_MIN:
            ket = "REJECT"
            ly_parts.append(f"edge/cost={ratio:.3f}<{EDGE_COST_MIN}")
        ly = "; ".join(ly_parts)

    cagr_ff = dd_ff = None
    if nets and years > 0:
        V0 = 10000.0
        V = V0
        peak = V0
        maxdd = 0.0
        for t in sorted(trades, key=lambda x: x.t_close):
            phi = load_phi(t.symbol)
            if phi is None:
                continue
            hold = (t.t_close - t.t_open).total_seconds() / 86400
            gross = t.chieu * (t.price_close - t.price_open)
            sp, sw, _ = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
            net_price = gross - sp + sw
            usd_1 = net_price * phi.contract
            risk_1 = abs(net_price) * phi.contract if net_price != 0 else (phi.spread_p90 * phi.contract + 1e-9)
            vol_sz = (0.01 * V) / risk_1 if risk_1 > 0 else 0
            V += usd_1 * vol_sz
            if V <= 0:
                V = 0
                maxdd = 100.0
                break
            peak = max(peak, V)
            maxdd = max(maxdd, (peak - V) / peak * 100)
        if V > 0 and V / V0 <= 1e6:
            cagr_ff = ((V / V0) ** (1 / years) - 1) * 100
            dd_ff = maxdd
        if ket == "PASS" and cagr_ff is not None and dd_ff is not None:
            if not (cagr_ff > CAGR_MIN and dd_ff < DD_MAX):
                ket = "REJECT"
                ly = (ly + "; " if ly else "") + f"CAGR_ff={cagr_ff:.2f}/DD_ff={dd_ff:.2f} không đạt 10%/80%"

    # per-symbol don_le PASS list
    by = defaultdict(list)
    for t in trades:
        by[t.symbol].append(t)
    per_sym = []
    for sym, ts in sorted(by.items(), key=lambda x: -len(x[1])):
        if len(ts) < 20:
            continue
        sub = analyze_subset_shallow(ts, sym)
        per_sym.append(sub)

    return {
        "label": label,
        "n": len(trades),
        "years": round(years, 3),
        "per_yr": round(len(trades) / years, 2),
        "t0": t0.isoformat(sep=" "),
        "t1": t1.isoformat(sep=" "),
        "buy_pct": round(buy_pct, 2),
        "hold_med_d": round(float(st.median(holds)), 4),
        "hang": hang,
        "max_same": max_same,
        "grid": bool(grid.get("grid")) if isinstance(grid, dict) else bool(grid),
        "martingale": bool(grid.get("martingale")) if isinstance(grid, dict) else False,
        "sl_pct": round(sl_pct, 1),
        "fee_cover": round(fee_cover, 3),
        "missing": dict(missing),
        "net_E_price": net_e,
        "edge_cost": ratio,
        "E_spread": sp_e,
        "E_swap": sw_e,
        "E_cost": cost_e,
        "E_gross": gross_e,
        "CAGR_ff": cagr_ff,
        "DD_ff": dd_ff,
        "ket_luan": ket,
        "ly_do": ly or ("PASS Cổng 0" if ket == "PASS" else ""),
        "per_sym_top": per_sym[:12],
        "syms": dict(Counter(t.symbol for t in trades).most_common(10)),
    }


def analyze_subset_shallow(trades: list[Trade], label: str) -> dict:
    """Lightweight per-symbol verdict without recursion into per_sym."""
    t0 = min(t.t_open for t in trades)
    t1 = max(t.t_close for t in trades)
    years = max((t1 - t0).total_seconds() / (365.25 * 86400), 1e-9)
    holds = [(t.t_close - t.t_open).total_seconds() / 86400 for t in trades]
    merged = _merge_partials(trades)
    events = []
    for tr in merged:
        events.append((tr.t_open, tr.chieu, 1))
        events.append((tr.t_close, tr.chieu, -1))
    events.sort(key=lambda x: (x[0], -x[2]))
    max_same = cur_b = cur_s = 0
    for _, ch, d in events:
        if ch > 0:
            cur_b += d
        else:
            cur_s += d
        max_same = max(max_same, cur_b, cur_s)
    sl_pct = 100.0 * sum(1 for t in trades if t.has_sl) / len(trades)
    if max_same >= 8 or (max_same >= 4 and sl_pct < 20):
        hang = "luoi"
    elif max_same <= 2:
        hang = "don_le"
    else:
        hang = "pyramid" if sl_pct >= 20 else "luoi"
    nets = []
    grosses = []
    costs = []
    for t in trades:
        phi = load_phi(t.symbol)
        if phi is None:
            continue
        hold = (t.t_close - t.t_open).total_seconds() / 86400
        gross = t.chieu * (t.price_close - t.price_open)
        sp, sw, cost = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
        nets.append(gross - sp + sw)
        grosses.append(gross)
        costs.append(cost)
    if len(nets) < max(10, 0.5 * len(trades)):
        return {"symbol": label, "n": len(trades), "hang": hang, "ket_luan": "CHUA_DO"}
    net_e = float(st.mean(nets))
    gross_e = float(st.mean(grosses))
    cost_e = float(st.mean(costs))
    ratio = (gross_e / cost_e) if cost_e > 1e-15 else float("inf")
    ket = "PASS"
    if net_e <= 0 or ratio < EDGE_COST_MIN:
        ket = "REJECT"
    return {
        "symbol": label,
        "n": len(trades),
        "hold_med_d": round(float(st.median(holds)), 4),
        "hang": hang,
        "max_same": max_same,
        "net_E": net_e,
        "edge_cost": ratio,
        "ket_luan": ket,
    }


SYSTEMS = [
    # (source, id, name, path, parser, min_years_ok)
    ("fxblue", "liehtw", "liehtw", FXB / "liehtw.csv", "fxblue", True),
    ("fxblue", "night-hawk", "night-hawk", FXB / "night-hawk.csv", "fxblue", True),
    ("fxblue", "xmglobal", "xmglobal", FXB / "xmglobal.csv", "fxblue", False),
    ("fxblue", "icmarkets-demo", "icmarkets-demo", FXB / "icmarkets-demo.csv", "fxblue", True),
    ("fxblue", "Public-stats", "Public-stats", FXB / "Public-stats.csv", "fxblue", False),
    ("fxblue", "happy-forex", "happy-forex", FXB / "happy-forex.csv", "fxblue", False),
    ("fxblue", "ibitebyt3s-10k-50r", "ibitebyt3s-10k-50r", FXB / "ibitebyt3s-10k-50r.csv", "fxblue", False),
    ("fxblue", "algobreed-xauusd-1", "algobreed-xauusd-1", FXB / "algobreed-xauusd-1.csv", "fxblue", False),
    ("fxblue", "eatradingacademy", "eatradingacademy", FXB / "eatradingacademy.csv", "fxblue", False),
    ("fxblue", "easyscalper", "easyscalper", FXB / "easyscalper.csv", "fxblue", True),
    ("fxblue", "myforexpath1", "myforexpath1", FXB / "myforexpath1.csv", "fxblue", True),
    ("fxblue", "myforexpath2", "myforexpath2", FXB / "myforexpath2.csv", "fxblue", False),
    ("fxblue", "free-forex-signal", "free-forex-signal", FXB / "free-forex-signal.csv", "fxblue", True),
    ("fxblue", "Metaliq-Gold", "Metaliq-Gold", FXB / "Metaliq-Gold.csv", "fxblue", True),
    ("fxblue", "trend-detector", "trend-detector", FXB / "trend-detector.csv", "fxblue", True),
    ("fxblue", "forex_trend_detector", "forex_trend_detector", FXB / "forex_trend_detector.csv", "fxblue", True),
    ("fxblue", "trend_detector", "trend_detector", FXB / "trend_detector.csv", "fxblue", False),


    ("fxblue", "bullbear", "bullbear", FXB / "bullbear.csv", "fxblue", True),
    ("fxblue", "forex-gold-investor", "forex-gold-investor", FXB / "forex-gold-investor.csv", "fxblue", True),
    ("fxblue", "nsr_gold", "nsr_gold", FXB / "nsr_gold.csv", "fxblue", True),
    ("fxblue", "divisagold", "divisagold", FXB / "divisagold.csv", "fxblue", False),
    ("fxblue", "fx-ekspert-ma-demo", "fx-ekspert-ma-demo", FXB / "fx-ekspert-ma-demo.csv", "fxblue", True),
    ("fxblue", "algo-trading", "algo-trading", FXB / "algo-trading.csv", "fxblue", False),
    ("fxblue", "alphafx", "alphafx", FXB / "alphafx.csv", "fxblue", True),
    ("fxblue", "capitalgrowth", "capitalgrowth", FXB / "capitalgrowth.csv", "fxblue", True),
    ("fxblue", "gold-pips", "gold-pips", FXB / "gold-pips.csv", "fxblue", False),
    ("fxblue", "algobreed-xauusd-2", "algobreed-xauusd-2", FXB / "algobreed-xauusd-2.csv", "fxblue", False),
    ("fxblue", "gold_scalping", "gold_scalping", FXB / "gold_scalping.csv", "fxblue", False),
    ("fxblue", "metaliq_gold", "metaliq_gold", FXB / "metaliq_gold.csv", "fxblue", False),
    ("fxblue", "forexlive", "forexlive", FXB / "forexlive.csv", "fxblue", True),
    ("fxblue", "fx-ea", "fx-ea", FXB / "fx-ea.csv", "fxblue", True),
    ("fxblue", "swingfx", "swingfx", FXB / "swingfx.csv", "fxblue", True),
    ("collective2", "134962085", "FOREX VIX-3", C2 / "134962085.csv", "c2", True),
    ("collective2", "122467834", "Tendency Forex", C2 / "122467834.csv", "c2", True),
    ("collective2", "94987184", "Just Forex Trades", C2 / "94987184.csv", "c2", True),
    ("collective2", "140118626", "ECFXBB", C2 / "140118626.csv", "c2", True),
    ("collective2", "125545530", "Wait4Trade Forex C2Star", C2 / "125545530.csv", "c2", False),
    ("collective2", "128801236", "MULTI FX PURE STRATEGY", C2 / "128801236.csv", "c2", True),
    ("collective2", "128454494", "Deep in the money", C2 / "128454494.csv", "c2", True),
    ("collective2", "117104490", "FX Hedge Fund", C2 / "117104490.csv", "c2", False),
    ("collective2", "123920081", "Multi Timeframe Forex", C2 / "123920081.csv", "c2", False),
    ("collective2", "137931431", "multiprofit", C2 / "137931431.csv", "c2", True),

    ("collective2", "151615755", "FuguSTMGold", C2 / "151615755.csv", "c2", False),
    ("collective2", "151319237", "Goldvantage Pro", C2 / "151319237.csv", "c2", False),
    ("collective2", "116569489", "FX Alpha Signal", C2 / "116569489.csv", "c2", True),
    ("collective2", "148093242", "Forex Currency Trading", C2 / "148093242.csv", "c2", False),
    ("collective2", "111340583", "Ground Swell Forex", C2 / "111340583.csv", "c2", True),
    ("collective2", "24790189", "Gold Survivor Forex", C2 / "24790189.csv", "c2", True),
    ("collective2", "143135149", "RC 105 ForEx", C2 / "143135149.csv", "c2", True),
    ("collective2", "98549641", "TACTICAL GOLD TIMER", C2 / "98549641.csv", "c2", True),
    ("collective2", "150565426", "Gold and Silver", C2 / "150565426.csv", "c2", False),
    ("collective2", "109650444", "Test4710", C2 / "109650444.csv", "c2", False),
    ("fxblue", "robot-forex", "robot-forex", FXB / "robot-forex.csv", "fxblue", True),
    ("fxblue", "supplydemand", "supplydemand", FXB / "supplydemand.csv", "fxblue", True),
    ("fxblue", "fibonacci", "fibonacci", FXB / "fibonacci.csv", "fxblue", True),
    ("collective2", "89703872", "Freedom EURUSD", C2 / "89703872.csv", "c2", False),
    ("collective2", "119679215", "EURUSD ForeXtreme", C2 / "119679215.csv", "c2", False),
    ("collective2", "79862763", "EUR USD Medium Term", C2 / "79862763.csv", "c2", False),
    ("collective2", "14614678", "Vortex II Forex", C2 / "14614678.csv", "c2", False),
    ("collective2", "128013249", "Forex anticrisis", C2 / "128013249.csv", "c2", True),
    ("collective2", "126172384", "Forex Street Wealth", C2 / "126172384.csv", "c2", False),
    ("collective2", "151472571", "151472571", C2 / "151472571.csv", "c2", False),
    ("collective2", "147255777", "147255777", C2 / "147255777.csv", "c2", True),
    ("collective2", "152221526", "152221526", C2 / "152221526.csv", "c2", False),
    ("collective2", "131145247", "131145247", C2 / "131145247.csv", "c2", True),
    ("fxblue", "gold_edge", "gold_edge", FXB / "gold_edge.csv", "fxblue", False),
    ("fxblue", "forex_alpha", "forex_alpha", FXB / "forex_alpha.csv", "fxblue", False),
    ("fxblue", "forex-live", "forex-live", FXB / "forex-live.csv", "fxblue", False),
    ("fxblue", "fx-pro", "fx-pro", FXB / "fx-pro.csv", "fxblue", False),
    ("fxblue", "gold-system", "gold-system", FXB / "gold-system.csv", "fxblue", False),
    ("fxblue", "forex_gold", "forex_gold", FXB / "forex_gold.csv", "fxblue", False),
    ("fxblue", "3propea_xauusd", "3propea_xauusd", FXB / "3propea_xauusd.csv", "fxblue", False),
    ("fxblue", "MT5GoldEA", "MT5GoldEA", FXB / "MT5GoldEA.csv", "fxblue", False),
    ("fxblue", "DynaScalp", "DynaScalp", FXB / "DynaScalp.csv", "fxblue", False),
    ("fxblue", "EasyScalper", "EasyScalper", FXB / "EasyScalper.csv", "fxblue", True),
    ("fxblue", "ForexTrendDetector", "ForexTrendDetector", FXB / "ForexTrendDetector.csv", "fxblue", False),
    ("fxblue", "Seagull_EA", "Seagull_EA", FXB / "Seagull_EA.csv", "fxblue", False),
    ("fxblue", "dynascalp_demo", "dynascalp_demo", FXB / "dynascalp_demo.csv", "fxblue", False),
    ("fxblue", "forex_edge_pro", "forex_edge_pro", FXB / "forex_edge_pro.csv", "fxblue", False),
    ("fxblue", "free-forex-signal_GBPUSD", "free-forex-signal_GBPUSD", FXB / "free-forex-signal_GBPUSD.csv", "fxblue", False),
    ("fxblue", "free-forex-signal_USDJPY", "free-forex-signal_USDJPY", FXB / "free-forex-signal_USDJPY.csv", "fxblue", False),
    ("fxblue", "fundednext", "fundednext", FXB / "fundednext.csv", "fxblue", False),
    ("fxblue", "gold-investor", "gold-investor", FXB / "gold-investor.csv", "fxblue", False),
    ("fxblue", "goldscalping_demo", "goldscalping_demo", FXB / "goldscalping_demo.csv", "fxblue", False),
    ("fxblue", "gpbootcamp", "gpbootcamp", FXB / "gpbootcamp.csv", "fxblue", False),
    ("fxblue", "liehtw_XAUEUR", "liehtw_XAUEUR", FXB / "liehtw_XAUEUR.csv", "fxblue", False),
    ("fxblue", "metaliq-gold", "metaliq-gold", FXB / "metaliq-gold.csv", "fxblue", True),
    ("fxblue", "mt5goldea", "mt5goldea", FXB / "mt5goldea.csv", "fxblue", False),
    ("fxblue", "myforexpath", "myforexpath", FXB / "myforexpath.csv", "fxblue", False),
    ("fxblue", "pepperstonexau", "pepperstonexau", FXB / "pepperstonexau.csv", "fxblue", False),
    ("fxblue", "robots-forex-live", "robots-forex-live", FXB / "robots-forex-live.csv", "fxblue", False),
    ("fxblue", "ruby-forex-ea", "ruby-forex-ea", FXB / "ruby-forex-ea.csv", "fxblue", False),
    ("fxblue", "xauusd11", "xauusd11", FXB / "xauusd11.csv", "fxblue", False),
    ("collective2", "114146885", "114146885", C2 / "114146885.csv", "c2", True),
    ("collective2", "132148218", "132148218", C2 / "132148218.csv", "c2", True),
    ("collective2", "133743692", "133743692", C2 / "133743692.csv", "c2", False),
    ("collective2", "139585165", "139585165", C2 / "139585165.csv", "c2", False),
    ("collective2", "141924124", "141924124", C2 / "141924124.csv", "c2", False),
    ("collective2", "143110798", "143110798", C2 / "143110798.csv", "c2", True),
    ("collective2", "146006468", "146006468", C2 / "146006468.csv", "c2", True),
    ("collective2", "146455121", "146455121", C2 / "146455121.csv", "c2", True),
    ("collective2", "149244504", "149244504", C2 / "149244504.csv", "c2", False),
    ("collective2", "149476882", "149476882", C2 / "149476882.csv", "c2", True),
    ("collective2", "150373429", "150373429", C2 / "150373429.csv", "c2", False),
    ("collective2", "150377786", "150377786", C2 / "150377786.csv", "c2", False),
    ("collective2", "150759166", "150759166", C2 / "150759166.csv", "c2", False),
    ("collective2", "151330723", "151330723", C2 / "151330723.csv", "c2", False),
    ("collective2", "152169281", "152169281", C2 / "152169281.csv", "c2", False),
    ("collective2", "152305186", "152305186", C2 / "152305186.csv", "c2", False),
    ("collective2", "152305234", "152305234", C2 / "152305234.csv", "c2", False),
    ("collective2", "152701320", "152701320", C2 / "152701320.csv", "c2", False),
    ("collective2", "153204518", "153204518", C2 / "153204518.csv", "c2", False),
    ("collective2", "153432780", "153432780", C2 / "153432780.csv", "c2", False),
    ("collective2", "154330462", "154330462", C2 / "154330462.csv", "c2", False),
    ("collective2", "156716997", "156716997", C2 / "156716997.csv", "c2", False),
    ("collective2", "157135749", "157135749", C2 / "157135749.csv", "c2", False),
]



def main():
    results = []
    for src, sid, name, path, parser, ge2 in SYSTEMS:
        if not path.exists():
            results.append({"source": src, "id": sid, "name": name, "ket_luan": "CHUA_DO", "ly_do": "missing file"})
            continue
        trades = parse_fxblue(path) if parser == "fxblue" else parse_c2(path)
        if not trades:
            results.append(
                {
                    "source": src,
                    "id": sid,
                    "name": name,
                    "path": str(path),
                    "ket_luan": "CHUA_DO",
                    "ly_do": "0 closed trades (login wall or empty)",
                    "ge2y": ge2,
                }
            )
            continue
        r = analyze_subset(trades, name)
        r.update({"source": src, "id": sid, "name": name, "path": str(path), "ge2y_target": ge2, "years_ok": r["years"] >= 2.0})
        results.append(r)
        print(f"{src}/{sid}: n={r['n']} y={r['years']} hang={r['hang']} cover={r['fee_cover']} net={r['net_E_price']} e/c={r['edge_cost']} => {r['ket_luan']}")

    # Darwinex series-level
    sg = Path("/workspace/nguon_khac/darwinex/series_gate.json")
    darwinex = json.loads(sg.read_text()) if sg.exists() else []

    out = {
        "asof": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tz": "Asia/Bangkok",
        "trade_level": results,
        "darwinex_series": darwinex,
    }
    (OUT / "nguon_khac_dot1_loc_phi.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("wrote", OUT / "nguon_khac_dot1_loc_phi.json")


if __name__ == "__main__":
    main()
