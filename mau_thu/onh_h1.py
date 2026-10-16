# -*- coding: utf-8 -*-
"""Lan dau thu setup cua chu du an tren H1 XM US500Cash (xap xi). KHONG SL, giu cho gia quay lai.
ONH = dinh cua phien dem 18:00 NY hom truoc -> 09:00 NY (nua gio truoc mo cua khong tinh vi H1).
Setup (ban hieu): sau 09:00 NY co nen DONG tren ONH ("mo phien tang"); sau do co nen CHAM ONH (low<=ONH) -> BUY tai ONH.
TP theo % gia vao. Thoat: cham TP, hoac sau 30 ngay thi dong theo gia thi truong. Chi phi: spread + swap tung dem.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

SRC = str(Path(__file__).resolve().parents[1] / "reports/mt5_v27/gia_xm/US500Cash_H1.csv.gz")
SPREAD_BPS = 1.0            # ~0,77 diem o gia 7.650 (Ultra Low do ~0,6 diem; Standard uoc cao hon) - GIA DINH
SWAP_NAM = 0.0577           # phi giu lenh MUA XM US500Cash do 13/09/2026 (config/chi_phi_do.json)
TPS = [0.0005, 0.0007, 0.0010, 0.0025, 0.0050]
MAX_NGAY = 30


def nap():
    d = pd.read_csv(SRC, parse_dates=["time"]).set_index("time")
    idx = d.index.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT")   # server XM = EET/EEST
    d = d[~idx.isna()].copy()
    d.index = idx[~idx.isna()]
    ny = d.index.tz_convert("America/New_York")
    d["ny_date"] = ny.normalize().tz_localize(None)
    d["ny_h"] = ny.hour
    d["ny_dow"] = ny.dayofweek
    d["t_ny"] = ny
    return d.reset_index(drop=True)


def tim_setup(d):
    # phien dem -> ngay phien (>=18h tinh cho ngay hom sau)
    sess = d.ny_date + pd.to_timedelta((d.ny_h >= 18).astype(int), unit="D")
    dem = (d.ny_h >= 18) | (d.ny_h < 9)
    onh = d[dem].groupby(sess[dem]).high.max()
    onl = d[dem].groupby(sess[dem]).low.min()
    cash = d[(d.ny_h >= 9) & (d.ny_h <= 15) & (d.ny_dow < 5)]
    out, base = [], []
    for day, g in cash.groupby("ny_date"):
        if day not in onh.index:
            continue
        H = onh[day]
        gi = g.index.tolist()
        # baseline: mua o nen 09:00 NY moi ngay
        if g.iloc[0].ny_h == 9:
            base.append((gi[0], float(g.iloc[0].open)))
        broke = False
        for j in gi:
            r = d.loc[j]
            if not broke:
                if r.close > H:
                    broke = True
                continue
            if r.low <= H:
                out.append((j, float(min(r.open, H)), H, day))
                break
    return out, base


def chay(d, entries, tp):
    kq = []
    n = len(d)
    t = d.t_ny
    for j, e, _H, day in entries:
        tp_gia = e * (1 + tp)
        lo = d.low.values[j]
        hit = None
        k = j + 1
        t_end = t[j] + pd.Timedelta(days=MAX_NGAY)
        last = j
        while k < n and t[k] <= t_end:
            lo = min(lo, d.low.values[k])
            last = k
            if d.high.values[k] >= tp_gia:
                hit = k
                break
            k += 1
        if hit is not None:
            gia_ra, kk = tp_gia, hit
        else:
            gia_ra, kk = float(d.close.values[last]), last
        # dem giu: moi moc 17:00 NY nam giua vao va ra; thu Sau x3
        a, b = t[j], t[kk]
        so = 0.0
        day0 = a.normalize()
        cur = day0 + pd.Timedelta(hours=17)
        while cur <= b + pd.Timedelta(days=1):
            if a < cur <= b and cur.dayofweek < 5:
                so += 3.0 if cur.dayofweek == 4 else 1.0
            cur += pd.Timedelta(days=1)
        gross = (gia_ra / e - 1) * 1e4
        kq.append(dict(ngay=day, nam=day.year, hit=hit is not None, gio_giu=(b - a).total_seconds() / 3600,
                       mae_pct=(e - lo) / e * 100, gross=gross, dem=so,
                       net_swap=gross - SPREAD_BPS - so * SWAP_NAM / 365 * 1e4,
                       net_khong_swap=gross - SPREAD_BPS))
    return pd.DataFrame(kq)


def tom_tat(r, nhan):
    if r.empty:
        return f"{nhan}: khong co lenh"
    ra = r[r.hit]
    return (f"{nhan}: n={len(r)}  chạm TP={r.hit.mean()*100:4.1f}%  "
            f"TP trong ngày(<=7h)={((r.hit)&(r.gio_giu<=7)).mean()*100:4.1f}%  <=5 ngày={((r.hit)&(r.gio_giu<=120)).mean()*100:4.1f}%  "
            f"giữ TB(lệnh chạm TP)={ra.gio_giu.mean():5.1f}h trung vị={ra.gio_giu.median():5.1f}h  "
            f"net/lệnh sau spread+swap={r.net_swap.mean():+5.1f} bps  (không swap {r.net_khong_swap.mean():+5.1f})  "
            f"MAE trung vị={r.mae_pct.median():.2f}% p90={r.mae_pct.quantile(.9):.2f}% p99={r.mae_pct.quantile(.99):.2f}% max={r.mae_pct.max():.2f}%")


if __name__ == "__main__":
    d = nap()
    entries, base = tim_setup(d)
    print(f"Du lieu: {d.t_ny.iloc[0].date()} -> {d.t_ny.iloc[-1].date()}   so setup ONH: {len(entries)}   so ngay baseline: {len(base)}")
    yrs = pd.Series([e[3].year for e in entries]).value_counts().sort_index()
    print("setup/nam:", yrs.to_dict())
    base_e = [(j, p, p, d.ny_date[j]) for j, p in base]
    for tp in TPS:
        print(f"\n=== TP = {tp*100:.2f}% (~{tp*7650:.1f} diem o gia 7.650) ===")
        r = chay(d, entries, tp)
        print(tom_tat(r, "ONH-retest   "))
        rb = chay(d, base_e, tp)
        print(tom_tat(rb, "Mua 09:00 NY  "))
        if abs(tp - 0.0007) < 1e-9:
            print("\n  Theo nam (ONH-retest, TP 0,07%):")
            g = r.groupby("nam").agg(n=("hit", "size"), cham_TP=("hit", "mean"), net_bps=("net_swap", "mean"),
                                     mae_max=("mae_pct", "max"), giu_TB_h=("gio_giu", "mean"))
            g["cham_TP"] = (g.cham_TP * 100).round(1)
            print(g.round(2).to_string())
            w = r.sort_values("mae_pct", ascending=False).head(5)
            print("\n  5 lenh xau nhat (MAE lon nhat):")
            print(w[["ngay", "mae_pct", "gio_giu", "hit", "net_swap"]].to_string(index=False))
            print("\n  Lenh chua cham TP sau 30 ngay:", int((~r.hit).sum()), "/", len(r))
