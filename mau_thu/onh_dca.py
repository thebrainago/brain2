# -*- coding: utf-8 -*-
"""Kieu KHONG SL: cho gia quay lai (khong gioi han thoi gian) va DCA. Dung lai nap()/tim_setup() cua onh_h1.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd
import onh_h1 as O

def dem_swap(a, b):
    so = 0.0
    cur = a.normalize() + pd.Timedelta(hours=17)
    while cur <= b + pd.Timedelta(days=1):
        if a < cur <= b and cur.dayofweek < 5:
            so += 3.0 if cur.dayofweek == 4 else 1.0
        cur += pd.Timedelta(days=1)
    return so

def chay(d, entries, tp, step=None, adds=0, swap_nam=O.SWAP_NAM):
    lo_v, hi_v, t, n = d.low.values, d.high.values, d.t_ny, len(d)
    close_v = d.close.values
    res = []
    for j, e, _H, day in entries:
        fills = [e]
        lv = [e * (1 - step * m) for m in range(1, adds + 1)] if step else []
        float_max = (e - lo_v[j]) / e * 100            # % cua 1 don vi
        hit = None; k = j + 1
        while k < n:
            avg = sum(fills) / len(fills)
            if hi_v[k] >= avg * (1 + tp):
                hit = k; break
            while lv and lo_v[k] <= lv[0]:               # lap DCA sau khi kiem TP (bao thu)
                fills.append(lv.pop(0))
            fl = sum((f - lo_v[k]) for f in fills) / e * 100
            float_max = max(float_max, fl)
            k += 1
        res_k = hit if hit is not None else n - 1
        avg = sum(fills) / len(fills)
        gia_ra = avg * (1 + tp) if hit is not None else close_v[res_k]
        a, b = t[j], t[res_k]
        nights = dem_swap(a, b)
        u = len(fills)
        gross = sum((gia_ra - f) / e for f in fills) * 1e4
        net = gross - u * O.SPREAD_BPS - u * nights * swap_nam / 365 * 1e4
        res.append(dict(ngay=day, nam=day.year, hit=hit is not None, units=u, ngay_giu=(b - a).total_seconds() / 86400,
                        float_max=float_max, net_bps=net, net_ko_swap=gross - u * O.SPREAD_BPS))
    return pd.DataFrame(res)

def tom(r, nhan):
    ra = r[r.hit]
    return (f"{nhan:34s} n={len(r)} cham_TP={r.hit.mean()*100:5.1f}%  chua_TP_den_het_du_lieu={int((~r.hit).sum())}  "
            f"ngay_giu: TB={ra.ngay_giu.mean():5.1f} p90={ra.ngay_giu.quantile(.9):5.1f} p99={ra.ngay_giu.quantile(.99):6.1f} max={ra.ngay_giu.max():6.0f}  "
            f"lo_treo_max(%1don_vi): TB={r.float_max.mean():4.2f} p99={r.float_max.quantile(.99):5.1f} max={r.float_max.max():5.1f}  "
            f"don_vi_max={int(r.units.max())}  net/lenh={r.net_bps.mean():+6.1f}bps  (khong swap {r.net_ko_swap.mean():+6.1f})  tong={r.net_bps.sum():+8.0f}bps")

if __name__ == "__main__":
    d = O.nap(); entries, base = O.tim_setup(d)
    base_e = [(j, p, p, d.ny_date[j]) for j, p in base]
    for tp in (0.0007, 0.0025):
        print(f"\n===== TP {tp*100:.2f}%  (~{tp*7650:.0f} diem o gia 7.650) =====")
        print(tom(chay(d, entries, tp), "ONH-retest, 1 lenh, cho den cung"))
        print(tom(chay(d, base_e, tp), "Mua 09:00 NY, 1 lenh, cho den cung"))
        for step in (0.005, 0.01):
            print(tom(chay(d, entries, tp, step, 3), f"ONH-retest + DCA {step*100:.1f}% x3"))
            print(tom(chay(d, base_e, tp, step, 3), f"Mua 09:00 + DCA {step*100:.1f}% x3"))
    r = chay(d, entries, 0.0007)
    print("\nLenh giu lau nhat (ONH-retest, TP 0,07%, 1 lenh):")
    print(r.sort_values("ngay_giu", ascending=False).head(6)[["ngay","ngay_giu","float_max","net_bps"]].to_string(index=False))
    rr = r.groupby("nam").agg(n=("hit","size"), cham=("hit","mean"), giu_max_ngay=("ngay_giu","max"), lo_treo_max_pct=("float_max","max"), net_bps=("net_bps","mean"))
    print("\nTheo nam (1 lenh, cho den cung, swap 5,77%/nam):"); print(rr.round(2).to_string())
