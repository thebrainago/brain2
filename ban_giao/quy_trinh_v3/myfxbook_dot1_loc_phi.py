#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng 0 XM trên 6 hệ Myfxbook đợt 1 (sau 3534905). Không commit."""
from __future__ import annotations

import json
import statistics as st
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

import sys
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
    _PHI_CACHE,
)

OUT = Path("/workspace/quy_trinh_v3")
DIR = Path("/workspace/myfxbook")

SYSTEMS = [
    ("11204017", "NoPain MT5", "tec_daniel/nopain-mt5"),
    ("8016551", "R Factor Portfolio Mean Reversal", "johnmacknamara/r-factor-portfolio-mean-reversal"),
    ("8365278", "R Factor JM Portfolio", "johnmacknamara/r-factor-jm-portfolio"),
    ("11576068", "Rainy Strategies Multi-Strategy", "Furuku/rainy-strategies--multi-strategy"),
    ("11730585", "MidasAlgo", "MidasAlgo/midasalgo"),
    ("11583686", "Bitcoin Adi FBS", "Bitcoin Adi"),
]


def pip_size(sym: str) -> float:
    s = (sym or "").upper()
    if s in ("XAUUSD", "GOLD"):
        return 0.01
    if s in ("BTCUSD", "ETHUSD"):
        return 1.0
    if s in ("US30", "US100", "US500", "NAS100", "GER40"):
        return 1.0
    if s.endswith("JPY"):
        return 0.01
    return 0.0001


def _f(v, default=0.0):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return default
        s = str(v).strip()
        if s == "" or s.lower() in ("nan", "none"):
            return default
        return float(s)
    except Exception:
        return default


def parse_myfxbook(path: Path) -> list[Trade]:
    df = pd.read_csv(path, low_memory=False)
    cols = {c: c for c in df.columns}
    trades: list[Trade] = []
    for _, r in df.iterrows():
        act = str(r.get("Action") or "").strip()
        if act not in ("Buy", "Sell"):
            continue
        raw = str(r.get("Symbol") or "").strip().upper()
        if not raw or raw in ("NAN", "SUMMAR", "NONE"):
            continue
        mapped = map_symbol(raw) or raw
        if mapped.startswith("OTHER:"):
            mapped = mapped.split(":", 1)[1]
        try:
            t0 = datetime.strptime(str(r["Open Date"]).strip(), "%m/%d/%Y %H:%M")
            t1 = datetime.strptime(str(r["Close Date"]).strip(), "%m/%d/%Y %H:%M")
        except Exception:
            continue
        chieu = 1 if act == "Buy" else -1
        vol = _f(r.get("Units/Lots"))
        po = _f(r.get("Open Price"))
        pc = _f(r.get("Close Price"))
        if po <= 0 or pc <= 0:
            continue
        sl = _f(r.get("SL")) if "SL" in cols else 0.0
        tp = _f(r.get("TP")) if "TP" in cols else 0.0
        has_sl = abs(sl) > 1e-12
        has_tp = abs(tp) > 1e-12
        comm = _f(r.get("Commission")) if "Commission" in cols else 0.0
        swap = _f(r.get("Swap")) if "Swap" in cols else 0.0
        profit = _f(r.get("Profit")) if "Profit" in cols else 0.0
        comment = str(r.get("Comment") or "") if "Comment" in cols else ""
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
                sl=sl if has_sl else None,
                tp=tp if has_tp else None,
                commission=comm,
                swap=swap,
                profit=profit,
                comment=comment,
                has_sl=has_sl,
                has_tp=has_tp,
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
    buy_n = sum(1 for t in trades if t.chieu > 0)
    buy_pct = 100.0 * buy_n / len(trades)

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

    ic_profit = sum(t.profit for t in trades)
    ic_comm = sum(t.commission for t in trades)
    ic_swap = sum(t.swap for t in trades)
    ic_net = ic_profit + ic_comm + ic_swap
    ic_e_profit = st.mean([t.profit for t in trades])
    ic_e_comm = st.mean([t.commission for t in trades])
    ic_e_swap = st.mean([t.swap for t in trades])
    ic_e_net = ic_e_profit + ic_e_comm + ic_e_swap

    pips = []
    for t in trades:
        ps = pip_size(t.symbol)
        pips.append(t.chieu * (t.price_close - t.price_open) / ps)

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
    lots = [t.volume for t in trades if t.volume > 0]
    lot_med = float(st.median(lots)) if lots else 0.0
    comm_per_lot = []
    for t in trades:
        if t.volume > 0 and abs(t.commission) > 0:
            comm_per_lot.append(abs(t.commission) / t.volume)
    ic_comm_per_lot_med = float(st.median(comm_per_lot)) if comm_per_lot else None

    # Require meaningful fee cover; if many missing (crypto/index) report CHUA_DO when cover < 50%
    if len(nets) < max(10, 0.5 * len(trades)):
        ket = "CHUA_DO"
        ly = f"phí cover {len(nets)}/{len(trades)}; thiếu {dict(missing)}"
        net_e = ratio = None
        sp_e = sw_e = cost_e = None
        gross_e = None
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
        if V > 0 and V / V0 <= 1e6:
            cagr_ff = ((V / V0) ** (1 / years) - 1) * 100
            dd_ff = maxdd
        if ket == "PASS" and cagr_ff is not None and dd_ff is not None:
            if not (cagr_ff > CAGR_MIN and dd_ff < DD_MAX):
                ket = "REJECT"
                ly = (ly + "; " if ly else "") + f"CAGR_ff={cagr_ff:.2f}/DD_ff={dd_ff:.2f} không đạt 10%/80%"

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

    # also report fee-covered-only subset metrics when partial cover
    covered_only = None
    if missing and nets and fee_cover >= 0.1 and fee_cover < 0.999:
        covered_trades = [t for t in trades if load_phi(t.symbol) is not None]
        if covered_trades and label == "ALL":
            covered_only = analyze_subset(covered_trades, "COVERED_ONLY")

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
        ic_sum_profit=round(ic_profit, 2),
        ic_sum_commission=round(ic_comm, 2),
        ic_sum_swap=round(ic_swap, 2),
        ic_sum_net=round(ic_net, 2),
        ic_E_profit=round(ic_e_profit, 4),
        ic_E_commission=round(ic_e_comm, 4),
        ic_E_swap=round(ic_e_swap, 4),
        ic_E_net=round(ic_e_net, 4),
        ic_comm_per_lot_med=round(ic_comm_per_lot_med, 4) if ic_comm_per_lot_med is not None else None,
        lot_med=round(lot_med, 4),
        fee_cover_pct=round(100 * fee_cover, 1),
        xm_spread_p90_price=round(xm_sp90_price, 8) if xm_sp90_price is not None else None,
        xm_spread_p90_pips=round(xm_sp90_pips, 3) if xm_sp90_pips is not None else None,
        xm_E_spread_price=round(sp_e, 8) if sp_e is not None else None,
        xm_E_swap_price=round(sw_e, 8) if sw_e is not None else None,
        xm_E_cost_price=round(cost_e, 8) if cost_e is not None else None,
        xm_E_gross_price=round(gross_e, 8) if gross_e is not None else None,
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
        covered_only=covered_only,
        top_symbols=dict(sym_counts.most_common(12)),
    )


def run_one(oid: str, ten: str, url_hint: str) -> dict:
    _PHI_CACHE.clear()
    path = DIR / f"{oid}.csv"
    trades = parse_myfxbook(path)
    print(f"\n=== {oid} {ten} parsed={len(trades)} ===")
    overall = analyze_subset(trades, "ALL")
    print(
        "ALL", overall["ket_luan"], "net_E", overall["net_E_price"],
        "e/c", overall["edge_cost_ratio"], "hang", overall["hang"],
        "cover", overall["fee_cover_pct"], "CAGR", overall["CAGR_ff"], "DD", overall["DD_ff"],
    )
    per = []
    for sym, n in Counter(t.symbol for t in trades).most_common():
        ts = [t for t in trades if t.symbol == sym]
        r = analyze_subset(ts, sym)
        per.append(r)
        print(
            f"  {sym}: n={r['n']} avg_pips={r['avg_pips']} net_E={r['net_E_price']} "
            f"e/c={r['edge_cost_ratio']} hang={r['hang']} ket={r['ket_luan']} "
            f"CAGR={r['CAGR_ff']} DD={r['DD_ff']}"
        )
    survivors = [r for r in per if r["ket_luan"] == "PASS"]
    soft = [
        r for r in per
        if (r.get("net_E_price") or -1) > 0 and (r.get("edge_cost_ratio") or 0) >= EDGE_COST_MIN
    ]
    surv_all = None
    if survivors:
        surv_syms = {r["symbol"] for r in survivors}
        surv_all = analyze_subset([t for t in trades if t.symbol in surv_syms], "SUBSET_PASS_SYMS")
    else:
        surv_syms = set()
    soft_all = None
    if soft:
        soft_syms = {r["symbol"] for r in soft}
        soft_all = analyze_subset([t for t in trades if t.symbol in soft_syms], "SUBSET_NET_AND_EC")
    else:
        soft_syms = set()

    return dict(
        account=oid,
        ten=ten,
        url_hint=url_hint,
        csv=str(path),
        n_trades=len(trades),
        overall=overall,
        per_symbol=per,
        survivors_pass=sorted(surv_syms),
        survivor_combo=surv_all,
        soft_syms=sorted(soft_syms),
        soft_combo=soft_all,
    )


def main():
    results = []
    for oid, ten, url in SYSTEMS:
        results.append(run_one(oid, ten, url))
    out = dict(
        ngay_do="2026-11-09",
        zone="Asia/Bangkok UTC+7",
        he_thong=results,
        tong_hop=[
            dict(
                account=r["account"],
                ten=r["ten"],
                n=r["overall"]["n"],
                years=r["overall"].get("years"),
                hang=r["overall"].get("hang"),
                max_cung=r["overall"].get("max_cung_chieu"),
                grid=r["overall"].get("grid"),
                martingale=r["overall"].get("martingale"),
                fee_cover_pct=r["overall"].get("fee_cover_pct"),
                net_E_price=r["overall"].get("net_E_price"),
                edge_cost=r["overall"].get("edge_cost_ratio"),
                CAGR_ff=r["overall"].get("CAGR_ff"),
                DD_ff=r["overall"].get("DD_ff"),
                ket_luan=r["overall"].get("ket_luan"),
                ly_do=r["overall"].get("ly_do"),
                survivors=r["survivors_pass"],
                soft=r["soft_syms"],
            )
            for r in results
        ],
    )
    (OUT / "myfxbook_dot1_loc_phi.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("\nWROTE myfxbook_dot1_loc_phi.json")
    for row in out["tong_hop"]:
        print(
            row["account"], row["ten"][:28], row["ket_luan"],
            "net", row["net_E_price"], "e/c", row["edge_cost"],
            "hang", row["hang"], "PASS_syms", row["survivors"],
        )
    return out


if __name__ == "__main__":
    main()
