# -*- coding: utf-8 -*-
"""Kiem nhe dem short / hedge chong len core long US100 (D1, phi XM ca 2 chieu).

IS: < 2016-01-01. OOS: >= 2016-01-01. Khong p-placebo, khong tien dang ky — khong goi la pass.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# tai lai ham / hang so tu script loc truoc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from loc_xu_huong_chi_so import (  # noqa: E402
    ANN,
    FRI,
    OOS,
    find_csv,
    load_costs,
    load_daily,
    metrics,
    pack,
    precompute_bar_units,
    rollover_units,
    rsi_wilder,
    split_metrics,
    fmt,
)

# swap_short > 0 tren XM index cash = tai khoan duoc cong khi short
# fin_short_annual = -swap_short / mid * 365  (am = credit ~0.9%/nam)
FIN_SHORT = {
    "US500": -0.00920,
    "US100": -0.00905,
}


def costs_on_pos_signed(pos, r_fill, fill, spread_pts, fin_long, fin_short, bar_units):
    """pos co the am/duong/leverage. Moi lan |delta| thu mot nua-spread (mot vong = 1 spread)."""
    n = len(pos)
    pos = np.asarray(pos, float)
    px = np.where(np.asarray(fill) > 0, fill, np.nan)
    prev = np.empty(n, dtype=float)
    prev[0] = 0.0
    prev[1:] = pos[:-1]
    delta = pos - prev
    half = (spread_pts / 2.0) / px
    half = np.where(np.isfinite(half), half, 0.0)
    costs = np.abs(delta) * half
    if fin_long:
        costs = costs + np.where(pos > 0, pos * fin_long * bar_units / 365.0, 0.0)
    if fin_short:
        costs = costs + np.where(pos < 0, (-pos) * fin_short * bar_units / 365.0, 0.0)
    pnl = pos * r_fill - costs
    pnl[-1] = 0.0
    return np.where(np.isfinite(pnl), pnl, 0.0)


def apply_short(s, sig_close, hold=None, exit_sig=None, size=1.0, fin_short=None):
    """sig_close[t] => short tu open ke (pos[t+1] = -size). hold: toi da so bar.
    exit_sig[t] (neu co) = thoat o open ke. Khong chong lenh."""
    n = s["n"]
    sig = np.asarray(sig_close, dtype=bool)
    ex = np.asarray(exit_sig, dtype=bool) if exit_sig is not None else np.zeros(n, dtype=bool)
    pos = np.zeros(n, dtype=float)
    t = 0
    while t < n - 2:
        if sig[t]:
            a = t + 1
            b = n - 1
            if hold is not None:
                b = min(a + int(hold), n - 1)
            for k in range(a, b):
                # thoat neu exit_sig o close truoc open k+? exit o close k-1 -> ra open k
                if k > a and ex[k - 1]:
                    b = k
                    break
            pos[a:b] = -abs(size)
            t = b
        else:
            t += 1
    fl = 0.0  # hedge chuan la short-only
    fs = FIN_SHORT.get("US100", -0.009) if fin_short is None else fin_short
    # symbol-specific passed in
    pnl = costs_on_pos_signed(pos, s["r_open"], s["open"], s["spread"], 0.0, fs, s["units"])
    return pos, pnl


def rule_ema_cross_sell(s, fin_short, size=1.0):
    c = pd.Series(s["close"])
    e1 = c.ewm(span=21, adjust=False).mean().to_numpy()
    e2 = c.ewm(span=55, adjust=False).mean().to_numpy()
    cross = np.zeros(s["n"], dtype=bool)
    cross[55:] = (e1[55:] < e2[55:]) & (e1[54:-1] >= e2[54:-1])
    return apply_short(s, cross, hold=1, size=size, fin_short=fin_short)


def rule_z_swap_short_d1(s, fin_short, size=1.0):
    """Dich D1 cua z_swap_meter_short (goc H1): RSI(14) cheo xuong 70 va close < EMA21;
    ra khi RSI cheo len 30, giu toi da 3 bar."""
    rsi = rsi_wilder(s["close"], 14)
    ema = pd.Series(s["close"]).ewm(span=21, adjust=False).mean().to_numpy()
    sig = np.zeros(s["n"], dtype=bool)
    ex = np.zeros(s["n"], dtype=bool)
    for i in range(21, s["n"]):
        if not np.isfinite(rsi[i]) or not np.isfinite(rsi[i - 1]):
            continue
        if rsi[i] < 70 <= rsi[i - 1] and s["close"][i] < ema[i]:
            sig[i] = True
        if rsi[i] > 30 >= rsi[i - 1]:
            ex[i] = True
    return apply_short(s, sig, hold=3, exit_sig=ex, size=size, fin_short=fin_short)


def rule_short_below_sma200(s, fin_short, size=1.0):
    sma = pd.Series(s["close"]).rolling(200, min_periods=200).mean().to_numpy()
    sig = (s["close"] < sma) & np.isfinite(sma)
    # stay short while below: signal every bar below, but apply_short khong chong lenh
    # => dung pos truc tiep
    n = s["n"]
    pos = np.zeros(n, dtype=float)
    pos[1:] = np.where(sig[:-1], -abs(size), 0.0)
    pnl = costs_on_pos_signed(pos, s["r_open"], s["open"], s["spread"], 0.0, fin_short, s["units"])
    return pos, pnl


def rule_short_donchian20_sma200(s, fin_short, size=1.0):
    """Vao short khi close pha day 20 phien va close < SMA200; ra khi close > SMA200."""
    n = s["n"]
    low = s["low"]
    sma = pd.Series(s["close"]).rolling(200, min_periods=200).mean().to_numpy()
    dlow = pd.Series(low).shift(1).rolling(20, min_periods=20).min().to_numpy()
    raw = (s["close"] < dlow) & (s["close"] < sma) & np.isfinite(sma) & np.isfinite(dlow)
    ex = (s["close"] > sma) & np.isfinite(sma)
    return apply_short(s, raw, hold=None, exit_sig=ex, size=size, fin_short=fin_short)


def long_bh(s, size, fin_long):
    pos = np.zeros(s["n"], dtype=float)
    pos[1:] = size
    pnl = costs_on_pos_signed(pos, s["r_open"], s["open"], s["spread"], fin_long, 0.0, s["units"])
    return pos, pnl


def long_sma200(s, size, fin_long):
    sma = pd.Series(s["close"]).rolling(200, min_periods=200).mean().to_numpy()
    sig = (s["close"] > sma) & np.isfinite(sma)
    pos = np.zeros(s["n"], dtype=float)
    pos[1:] = np.where(sig[:-1], size, 0.0)
    pnl = costs_on_pos_signed(pos, s["r_open"], s["open"], s["spread"], fin_long, 0.0, s["units"])
    return pos, pnl


def align_pnl(dates_a, pnl_a, dates_b, pnl_b):
    a = pd.Series(pnl_a, index=pd.DatetimeIndex(dates_a).normalize())
    b = pd.Series(pnl_b, index=pd.DatetimeIndex(dates_b).normalize())
    both = a.index.intersection(b.index)
    return both, a.reindex(both).to_numpy(float), b.reindex(both).to_numpy(float)


def n_trades_signed(pos):
    pos = np.asarray(pos, float)
    prev = np.r_[0.0, pos[:-1]]
    return int(np.sum((np.abs(pos) > 1e-12) & (np.abs(prev) <= 1e-12)))


def split_combo(pnl, dates, times=None):
    dates = pd.DatetimeIndex(dates)
    if times is None:
        times = (dates + pd.Timedelta(hours=9, minutes=30)).to_numpy()
    pos_dummy = np.ones(len(pnl))  # chi de metrics co exp; se ghi de
    out = {}
    for name, m in (("IS", dates < OOS), ("OOS", dates >= OOS)):
        if m.sum() < 20:
            out[name] = dict(n=int(m.sum()), cagr=np.nan, sharpe=np.nan, dd=np.nan,
                             tot=np.nan, exp=np.nan, trades=0, years=np.nan)
            continue
        out[name] = metrics(pnl[m], np.ones(int(m.sum())), times[m])
    return out


def main():
    costs, cost_src = load_costs()
    series = {}
    fins = {}
    for name, fname in (("US500", "gspc_daily.csv"), ("US100", "ndx_daily.csv")):
        c = costs[name]
        df = load_daily(fname)
        s = pack(df, c["spread_pts_median"], c["fin_long_annual"])
        series[name] = s
        fins[name] = dict(long=float(c["fin_long_annual"]), short=FIN_SHORT[name],
                          spread=float(c["spread_pts_median"]))
        d0, d1 = s["dates"][0].date(), s["dates"][-1].date()
        print("loaded %s %s..%s n=%d spread=%s finL=%.4f finS=%.4f" % (
            name, d0, d1, s["n"], c["spread_pts_median"], c["fin_long_annual"], FIN_SHORT[name]))

    us100, us500 = series["US100"], series["US500"]
    fl100, fs100 = fins["US100"]["long"], fins["US100"]["short"]
    fl500, fs500 = fins["US500"]["long"], fins["US500"]["short"]

    cores = {
        "US100_BH_1x": long_bh(us100, 1.0, fl100),
        "US100_BH_1.5x": long_bh(us100, 1.5, fl100),
        "US100_SMA200_1x": long_sma200(us100, 1.0, fl100),
    }
    hedges = {
        "US500_ema_cross_sell_giu1": (us500, *rule_ema_cross_sell(us500, fs500)),
        "US500_zswap_short_D1": (us500, *rule_z_swap_short_d1(us500, fs500)),
        "US100_short_duoi_sma200": (us100, *rule_short_below_sma200(us100, fs100)),
        "US100_short_donchian20_sma200": (us100, *rule_short_donchian20_sma200(us100, fs100)),
    }

    lines = []
    lines.append("# Dem short / hedge chong core long US100 (D1, phi XM 2 chieu)")
    lines.append(f"Phi: {cost_src}; fin_short US100={fs100:.4f} US500={fs500:.4f} (am = credit).")
    lines.append("IS < 2016-01-01; OOS >= 2016-01-01. Khong p-placebo, khong tien dang ky — khong goi la pass.")
    lines.append("Drag = CAGR to hop − CAGR core. Tran ke hoach: keo <= 2%/nam neu hedge la chi phi.")
    lines.append("")

    # standalone cores + hedges
    lines.append("## Chan long (core)")
    core_split = {}
    for name, (pos, pnl) in cores.items():
        sm = split_metrics(pnl, pos, us100["t_open"], us100["dates"])
        core_split[name] = sm
        lines.append(f"### {name}")
        for part in ("IS", "OOS"):
            lines.append(f"  {part:3} {fmt(sm[part])}")
    lines.append("")
    lines.append("## Hedge dung mot (khong core)")
    hedge_split = {}
    hedge_store = {}
    for name, (s, pos, pnl) in hedges.items():
        sm = split_metrics(pnl, pos, s["t_open"], s["dates"])
        hedge_split[name] = sm
        hedge_store[name] = (s, pos, pnl)
        lines.append(f"### {name}  trades IS/OOS={sm['IS']['trades']}/{sm['OOS']['trades']}")
        for part in ("IS", "OOS"):
            lines.append(f"  {part:3} {fmt(sm[part])}")
    lines.append("")

    lines.append("## To hop core + hedge 1× (cong pnl theo ngay chung)")
    lines.append("cot: CAGR / Sharpe / DD / drag_vs_core (diem %/nam)")
    rows = []
    for cname, (cpos, cpnl) in cores.items():
        cdates = us100["dates"]
        for hname, (hs, hpos, hpnl) in hedge_store.items():
            dates, a, b = align_pnl(cdates, cpnl, hs["dates"], hpnl)
            port = a + b
            times = (dates + pd.Timedelta(hours=9, minutes=30)).to_numpy()
            sm = split_combo(port, dates, times)
            # drag vs core on the SAME aligned window
            c_al = split_combo(a, dates, times)
            lines.append(f"### {cname}  +  {hname}")
            for part in ("IS", "OOS"):
                m, c = sm[part], c_al[part]
                drag = (m["cagr"] - c["cagr"]) if np.isfinite(m["cagr"]) and np.isfinite(c["cagr"]) else np.nan
                dd_imp = (c["dd"] - m["dd"]) if np.isfinite(m["dd"]) and np.isfinite(c["dd"]) else np.nan
                sh_imp = (m["sharpe"] - c["sharpe"]) if np.isfinite(m["sharpe"]) and np.isfinite(c["sharpe"]) else np.nan
                cagr_ok = (m["cagr"] + 1e-6 >= c["cagr"] - 0.5) if np.isfinite(m["cagr"]) else False
                better = (dd_imp is not np.nan and (dd_imp >= 1.0 or sh_imp >= 0.02) and cagr_ok)
                flag = "CAI_THIEN_THO" if better else "—"
                lines.append(
                    f"  {part:3} CAGR {m['cagr']:+6.1f}% (core {c['cagr']:+5.1f}, drag {drag:+5.1f}pp)  "
                    f"Sh {m['sharpe']:+5.2f} (core {c['sharpe']:+5.2f}, {sh_imp:+5.2f})  "
                    f"DD {m['dd']:5.1f}% (core {c['dd']:5.1f}, {dd_imp:+5.1f}pp)  {flag}"
                )
                rows.append(dict(core=cname, hedge=hname, part=part,
                                 cagr=m["cagr"], sh=m["sharpe"], dd=m["dd"],
                                 core_cagr=c["cagr"], core_sh=c["sharpe"], core_dd=c["dd"],
                                 drag=drag, dd_imp=dd_imp, sh_imp=sh_imp))
    text = "\n".join(lines) + "\n"
    repo = Path(__file__).resolve().parents[3]
    out = repo / "docs" / "evo" / "loc_xu_huong_dem_bang.txt"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
