#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng 0 XM trên Myfxbook 3534905 (IC Markets FERRARI2009)."""
from __future__ import annotations

import json
import statistics as st
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, "/workspace/quy_trinh_v3")
from phan_tich_mql5_hist import (
    Trade,
    load_phi,
    xm_cost_price,
    detect_grid_martingale,
    _merge_partials,
    EDGE_COST_MIN,
    CAGR_MIN,
    DD_MAX,
    _PHI_CACHE,
)

OUT = Path("/workspace/quy_trinh_v3")
CSV = Path("/workspace/myfxbook/3534905.csv")


def parse_myfxbook(path: Path) -> list[Trade]:
    df = pd.read_csv(path)
    trades: list[Trade] = []
    for _, r in df.iterrows():
        act = str(r.get("Action") or "").strip()
        if act not in ("Buy", "Sell"):
            continue
        sym = str(r.get("Symbol") or "").strip().upper()
        if not sym or sym == "NAN" or sym == "SUMMAR":
            continue
        try:
            t0 = datetime.strptime(str(r["Open Date"]).strip(), "%m/%d/%Y %H:%M")
            t1 = datetime.strptime(str(r["Close Date"]).strip(), "%m/%d/%Y %H:%M")
        except Exception:
            continue
        chieu = 1 if act == "Buy" else -1
        vol = float(r["Units/Lots"] or 0)
        po = float(r["Open Price"])
        pc = float(r["Close Price"])
        sl = float(r["SL"] or 0)
        tp = float(r["TP"] or 0)
        has_sl = abs(sl) > 1e-12
        has_tp = abs(tp) > 1e-12
        trades.append(
            Trade(
                t_open=t0,
                t_close=t1,
                symbol_raw=sym,
                symbol=sym,
                chieu=chieu,
                volume=vol,
                price_open=po,
                price_close=pc,
                sl=sl if has_sl else None,
                tp=tp if has_tp else None,
                commission=float(r["Commission"] or 0),
                swap=float(r["Swap"] or 0),
                profit=float(r["Profit"] or 0),
                comment="",
                has_sl=has_sl,
                has_tp=has_tp,
            )
        )
    # attach pips from CSV via parallel list stored on object? keep side table
    return trades


def pip_size(sym: str) -> float:
    s = sym.upper()
    if s == "XAUUSD":
        return 0.01  # Myfxbook gold pip convention (matches CSV Pips scale)
    if s.endswith("JPY"):
        return 0.01
    return 0.0001


def hang_from_grid(g: dict) -> str:
    """Mirror MQL5 recount tiers using detect output + max_same."""
    # recompute max from ly_do or flags
    if g.get("grid"):
        return "luoi"
    if g.get("pyramid_nhe"):
        return "pyramid"
    # detect_grid uses max_same internally; expose via ly or re-derive
    return "don_le"


def analyze_subset(trades: list[Trade], label: str) -> dict:
    if not trades:
        return dict(label=label, n=0, ket_luan="CHUA_DO", ly_do="0 lệnh")

    t0 = min(t.t_open for t in trades)
    t1 = max(t.t_close for t in trades)
    years = max((t1 - t0).total_seconds() / (365.25 * 86400), 1e-9)
    holds = [(t.t_close - t.t_open).total_seconds() / 86400 for t in trades]
    buy_n = sum(1 for t in trades if t.chieu > 0)
    buy_pct = 100.0 * buy_n / len(trades)

    grid = detect_grid_martingale(trades)
    # max_cung for hang
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

    # IC Markets measured costs (EUR account — Profit/Comm/Swap đã EUR)
    ic_profit = sum(t.profit for t in trades)
    ic_comm = sum(t.commission for t in trades)
    ic_swap = sum(t.swap for t in trades)
    ic_net = ic_profit + ic_comm + ic_swap  # profit Myfxbook thường CHƯA gồm comm/swap riêng
    # Check: Myfxbook Profit is typically net of nothing for these columns — Profit is price PnL in account ccy; Comm/Swap separate
    # IC total account PnL = profit + commission + swap
    ic_e_profit = st.mean([t.profit for t in trades])
    ic_e_comm = st.mean([t.commission for t in trades])
    ic_e_swap = st.mean([t.swap for t in trades])
    ic_e_net = ic_e_profit + ic_e_comm + ic_e_swap

    # Pips from price (ĐO lại, không tin cột nếu lệch)
    pips = []
    for t in trades:
        ps = pip_size(t.symbol)
        pips.append(t.chieu * (t.price_close - t.price_open) / ps)

    # XM rebuild price units
    nets = []
    grosses = []
    costs = []
    sps = []
    sws = []
    missing = Counter()
    phi_nguon = Counter()
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
        tag = "phi_xm_micro" if phi.nguon == "phi_xm_micro.json" else "fallback_chi_phi_do+spread_bar"
        phi_nguon[tag] += 1

    fee_cover = len(nets) / len(trades) if trades else 0.0

    # Implied IC spread from open/close vs mid — cannot know mid; report commission RT per lot
    lots = [t.volume for t in trades if t.volume > 0]
    lot_med = float(st.median(lots)) if lots else 0.0
    # commission per 1.0 lot round-turn (EUR)
    comm_per_lot = []
    for t in trades:
        if t.volume > 0:
            comm_per_lot.append(abs(t.commission) / t.volume)
    ic_comm_per_lot_med = float(st.median(comm_per_lot)) if comm_per_lot else None

    if len(nets) < max(10, 0.5 * len(trades)):
        ket = "CHUA_DO"
        ly = f"phí cover {len(nets)}/{len(trades)}; thiếu {dict(missing)}"
        net_e = ratio = None
        sp_e = sw_e = cost_e = None
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

    # CAGR_ff ƯỚC (same as MQL5)
    cagr_ff = dd_ff = None
    if nets and years > 0:
        V0 = 10000.0
        V = V0
        peak = V0
        maxdd = 0.0
        exploded = False
        for t in sorted(trades, key=lambda x: x.t_close):
            phi = load_phi(t.symbol)
            if phi is None:
                continue
            hold = (t.t_close - t.t_open).total_seconds() / 86400
            gross = t.chieu * (t.price_close - t.price_open)
            sp, sw, _ = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
            net_price = gross - sp + sw
            usd_1 = net_price * phi.contract
            if t.has_sl and t.sl is not None and abs(t.price_open - t.sl) > 0:
                risk_1 = abs(t.price_open - t.sl) * phi.contract
            else:
                risk_1 = abs(net_price) * phi.contract if net_price != 0 else (phi.spread_p90 * phi.contract + 1e-9)
            vol_sz = (0.01 * V) / risk_1 if risk_1 > 0 else 0
            V += usd_1 * vol_sz
            if V <= 0:
                V = 0
                maxdd = 100.0
                break
            peak = max(peak, V)
            maxdd = max(maxdd, (peak - V) / peak * 100)
        if V / V0 > 1e6:
            exploded = True
        elif V > 0:
            cagr_ff = ((V / V0) ** (1 / years) - 1) * 100
            dd_ff = maxdd
        if ket == "PASS" and cagr_ff is not None and dd_ff is not None:
            if not (cagr_ff > CAGR_MIN and dd_ff < DD_MAX):
                ket = "REJECT"
                ly = (ly + "; " if ly else "") + f"CAGR_ff={cagr_ff:.2f}/DD_ff={dd_ff:.2f} không đạt 10%/80%"
        if exploded and ket == "PASS":
            # don't auto-pass on bad proxy
            pass

    # XM spread p90 (price) + in pips for report
    # use dominant / single symbol phi
    sym_counts = Counter(t.symbol for t in trades)
    if len(sym_counts) == 1:
        sym = next(iter(sym_counts))
        phi = load_phi(sym)
        xm_sp90_price = phi.spread_p90 if phi else None
        xm_sp90_pips = (phi.spread_p90 / pip_size(sym)) if phi else None
        phi_src = phi.nguon if phi else None
        fallback = phi is not None and phi.nguon != "phi_xm_micro.json"
    else:
        sym = "MULTI"
        xm_sp90_price = float(st.mean(sps)) if sps else None
        xm_sp90_pips = None
        phi_src = dict(phi_nguon)
        fallback = phi_nguon.get("fallback_chi_phi_do+spread_bar", 0) > 0

    return dict(
        label=label,
        symbol=sym if len(sym_counts) == 1 else "ALL",
        n=len(trades),
        years=round(years, 3),
        trades_per_yr=round(len(trades) / years, 2),
        buy_pct=round(buy_pct, 2),
        hold_med_d=round(float(st.median(holds)), 4),
        hold_mean_d=round(float(st.mean(holds)), 4),
        avg_pips=round(float(st.mean(pips)), 3),
        med_pips=round(float(st.median(pips)), 3),
        sl_pct=round(sl_pct, 2),
        hang=hang,
        max_cung_chieu=max_same,
        grid=bool(grid.get("grid")),
        martingale=bool(grid.get("martingale")),
        pyramid_nhe=bool(grid.get("pyramid_nhe")),
        grid_ly=grid.get("ly_do", ""),
        # IC Markets (EUR)
        ic_sum_profit=round(ic_profit, 2),
        ic_sum_commission=round(ic_comm, 2),
        ic_sum_swap=round(ic_swap, 2),
        ic_sum_net=round(ic_net, 2),
        ic_E_profit=round(ic_e_profit, 4),
        ic_E_commission=round(ic_e_comm, 4),
        ic_E_swap=round(ic_e_swap, 4),
        ic_E_net=round(ic_e_net, 4),
        ic_comm_per_lot_med_EUR=round(ic_comm_per_lot_med, 4) if ic_comm_per_lot_med is not None else None,
        lot_med=round(lot_med, 4),
        # XM
        fee_cover_pct=round(100 * fee_cover, 1),
        xm_spread_p90_price=round(xm_sp90_price, 8) if xm_sp90_price is not None else None,
        xm_spread_p90_pips=round(xm_sp90_pips, 3) if xm_sp90_pips is not None else None,
        xm_E_spread_price=round(sp_e, 8) if sp_e is not None else None,
        xm_E_swap_price=round(sw_e, 8) if sw_e is not None else None,
        xm_E_cost_price=round(cost_e, 8) if cost_e is not None else None,
        xm_E_gross_price=round(float(st.mean(grosses)), 8) if grosses else None,
        net_E_price=round(net_e, 8) if net_e is not None else None,
        edge_cost_ratio=round(ratio, 4) if ratio is not None else None,
        CAGR_ff=round(cagr_ff, 3) if cagr_ff is not None else None,
        DD_ff=round(dd_ff, 3) if dd_ff is not None else None,
        phi_nguon=phi_src,
        fallback_fee=fallback,
        missing_phi=dict(missing) if missing else {},
        ket_luan=ket,
        ly_do=ly,
        range=[str(t0), str(t1)],
    )


def main():
    _PHI_CACHE.clear()
    # also keep CSV pips for cross-check
    df = pd.read_csv(CSV)
    trades = parse_myfxbook(CSV)
    print("parsed", len(trades))

    # CSV pips vs recomputed
    df_t = df[df["Action"].isin(["Buy", "Sell"]) & df["Symbol"].notna() & (df["Symbol"] != "SUMMAR")].copy()
    print("csv trade rows", len(df_t))

    overall = analyze_subset(trades, "ALL")
    print("ALL", overall["ket_luan"], "net_E", overall["net_E_price"], "e/c", overall["edge_cost_ratio"],
          "hang", overall["hang"], "grid", overall["grid"], "mart", overall["martingale"])

    per = []
    for sym, n in Counter(t.symbol for t in trades).most_common():
        ts = [t for t in trades if t.symbol == sym]
        r = analyze_subset(ts, sym)
        per.append(r)
        print(f"{sym}: n={r['n']} avg_pips={r['avg_pips']} net_E={r['net_E_price']} e/c={r['edge_cost_ratio']} "
              f"hang={r['hang']} ket={r['ket_luan']} fallback={r['fallback_fee']} src={r['phi_nguon']}")

    # Surviving subset: symbols that PASS alone
    survivors = [r for r in per if r["ket_luan"] == "PASS"]
    # Also try combination of PASS symbols
    if survivors:
        surv_syms = {r["symbol"] for r in survivors}
        surv_trades = [t for t in trades if t.symbol in surv_syms]
        surv_all = analyze_subset(surv_trades, "SUBSET_PASS_SYMS")
    else:
        surv_all = None
        surv_syms = set()

    # Try drop worst (EURSGD fallback + high cost) — measured experiment: symbols with e/c>=1.5 and net_E>0 even if CAGR fails
    soft = [r for r in per if (r.get("net_E_price") or -1) > 0 and (r.get("edge_cost_ratio") or 0) >= EDGE_COST_MIN]
    if soft:
        soft_syms = {r["symbol"] for r in soft}
        soft_all = analyze_subset([t for t in trades if t.symbol in soft_syms], "SUBSET_NET_AND_EC")
    else:
        soft_all = None
        soft_syms = set()

    # Fee source table
    fee_table = []
    for sym in sorted(set(t.symbol for t in trades)):
        phi = load_phi(sym)
        if phi is None:
            fee_table.append(dict(symbol=sym, status="THIEU", nguon=None))
        else:
            in_micro = phi.nguon == "phi_xm_micro.json"
            fee_table.append(dict(
                symbol=sym,
                status="OK",
                nguon=phi.nguon,
                in_phi_xm_micro=in_micro,
                spread_p90_price=phi.spread_p90,
                spread_p90_pips=round(phi.spread_p90 / pip_size(sym), 3),
                swap_mua=phi.swap_mua,
                swap_ban=phi.swap_ban,
                point=phi.point,
                contract=phi.contract,
                swap_mode=phi.swap_mode,
                nhan=("ĐO phi_xm_micro" if in_micro else "FALLBACK chi_phi_do MICRO + spread_bar XM"),
            ))

    out = dict(
        account="3534905",
        ten="IC Markets FERRARI2009",
        currency="EUR",
        n_trades=len(trades),
        overall=overall,
        per_symbol=per,
        survivors_pass=sorted(surv_syms),
        survivor_combo=surv_all,
        soft_syms=sorted(soft_syms),
        soft_combo=soft_all,
        fee_table=fee_table,
        ic_vs_xm_note=dict(
            ic="Raw spread (nằm trong Open/Close) + Commission ĐO từ CSV + Swap ĐO từ CSV; tài khoản EUR",
            xm="Spread p90 + swap POINTS (hoa hồng XM micro ĐO = 0); rebuild net = chieu*(close-open) - spread_p90 + swap_xm(hold)",
            ic_comm_per_lot_med_EUR=overall.get("ic_comm_per_lot_med_EUR"),
            ic_sum_commission=overall.get("ic_sum_commission"),
            ic_sum_swap=overall.get("ic_sum_swap"),
            ic_sum_net=overall.get("ic_sum_net"),
        ),
    )
    (OUT / "myfxbook_3534905_loc_phi.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("WROTE json")
    print("PASS symbols", sorted(surv_syms))
    print("soft symbols", sorted(soft_syms))
    return out


if __name__ == "__main__":
    main()
