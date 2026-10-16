# -*- coding: utf-8 -*-
"""Setup ONH-retest, KHONG SL, chot co dinh N DIEM GIA (nhu chu du an: "loi 5-6 gia di"). Tinh bang DIEM, khong bang %.
Dung nap()/tim_setup() cua onh_h1.py. Swap/dem tinh theo gia luc vao (5,77%/nam). H1 xap xi - Grok lam lai o M1.
python mau_thu/onh_diem.py [TP_diem=5.5]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd
import onh_h1 as O
from onh_dca import dem_swap


def chay_diem(d, entries, tp_pts, spread_pts, swap_nam=O.SWAP_NAM):
    lo_v, hi_v, cl, t, n = d.low.values, d.high.values, d.close.values, d.t_ny, len(d)
    out = []
    for j, e, _H, day in entries:
        tp = e + tp_pts
        lo = lo_v[j]; hit = None; k = j + 1
        while k < n:
            lo = min(lo, lo_v[k])
            if hi_v[k] >= tp:
                hit = k; break
            k += 1
        kk = hit if hit is not None else n - 1
        gia_ra = tp if hit is not None else cl[kk]
        nights = dem_swap(t[j], t[kk])
        swap_pts = nights * swap_nam / 365 * e
        out.append(dict(ngay=day, nam=day.year, gia_vao=e, hit=hit is not None, gio=(t[kk] - t[j]).total_seconds() / 3600,
                        dem=nights, treo_pts=e - lo, swap_pts=swap_pts,
                        net_pts=(gia_ra - e) - spread_pts - swap_pts))
    return pd.DataFrame(out)


def bang(r, nhan):
    if r.empty:
        return f"{nhan}: khong co lenh"
    qua_dem = (r.dem > 0).mean() * 100
    return (f"{nhan:26s} n={len(r):4d}  trong phien(<=7h)={(r.gio <= 7).mean()*100:4.0f}%  phai qua dem={qua_dem:4.0f}%  "
            f"giu lau nhat={r.gio.max()/24:5.0f} ngay  treo toi da={r.treo_pts.max():6.0f} diem (p99 {r.treo_pts.quantile(.99):4.0f})  "
            f"swap TB/lenh={r.swap_pts.mean():4.2f} diem  NET TB/lenh={r.net_pts.mean():+5.2f} diem  tong={r.net_pts.sum():+7.0f} diem")


if __name__ == "__main__":
    tp = float(sys.argv[1]) if len(sys.argv) > 1 else 5.5
    d = O.nap(); entries, base = O.tim_setup(d)
    base_e = [(j, p, p, d.ny_date[j]) for j, p in base]
    moc = pd.Timestamp("2023-01-01")
    nay = [e for e in entries if e[3] >= moc]; nay_b = [e for e in base_e if e[3] >= moc]
    print(f"TP co dinh = {tp} diem gia. Gia 2023-2026: {d[d.t_ny >= '2023-01-01'].close.min():.0f}-{d[d.t_ny >= '2023-01-01'].close.max():.0f}  (5,5 diem ~ {tp/6500*100:.3f}% o gia 6.500)")
    for sp in (0.6, 1.5, 3.0):
        print(f"\n--- spread {sp} diem (XM Ultra Low do ~0,6; Exness/XM Standard/micro: CHUA DO - xem spread tren man hinh) ---")
        print(bang(chay_diem(d, nay, tp, sp), "ONH-retest 2023-2026"))
        print(bang(chay_diem(d, nay_b, tp, sp), "Mua 09:00 NY 2023-2026"))
    print("\n--- Theo nam, ONH-retest, spread 1,5 diem ---")
    r = chay_diem(d, entries, tp, 1.5)
    g = r.groupby("nam").agg(n=("hit", "size"), gia_vao=("gia_vao", "mean"), qua_dem=("dem", lambda x: (x > 0).mean() * 100),
                             giu_max_ngay=("gio", lambda x: x.max() / 24), treo_max=("treo_pts", "max"), net_TB=("net_pts", "mean"))
    print(g.round(1).to_string())


def chay_quan_ly(d, entries, tp_pts, spread_pts, mode, swap_nam=O.SWAP_NAM):
    """Cac cach xu li lenh chua chot trong phien My (cung entry, cung TP ban dau):
    giu     : giu den cung, TP khong doi
    ha_dem  : qua dem dau tien thi ha TP ve gan hoa von (entry+spread+0,5)
    ha_phien: het phien My (16:00 NY) chua chot thi ha TP ve gan hoa von
    cat_phien: het phien My chua chot thi DONG (cat lo) - chi de biet GIA cua viec khong giu qua dem
    """
    lo_v, hi_v, cl, t, n = d.low.values, d.high.values, d.close.values, d.t_ny, len(d)
    hv = d.ny_h.values
    out = []
    for j, e, _H, day in entries:
        tp = e + tp_pts
        ha = e + spread_pts + 0.5
        t_ve = t[j].normalize() + pd.Timedelta(hours=17)       # moc qua dem dau (17:00 NY cung ngay)
        t_phien = t[j].normalize() + pd.Timedelta(hours=16)     # het phien My
        lo = lo_v[j]; hit = None; k = j + 1; gia_ra = None
        while k < n:
            lo = min(lo, lo_v[k])
            tp_hien = tp
            if mode == "ha_dem" and t[k] >= t_ve:
                tp_hien = min(tp, ha)
            if mode == "ha_phien" and t[k] >= t_phien:
                tp_hien = min(tp, ha)
            if mode == "cat_phien" and t[k] >= t_phien:
                gia_ra, hit = cl[k - 1], k - 1
                break
            if hi_v[k] >= tp_hien:
                gia_ra, hit = tp_hien, k
                break
            k += 1
        if hit is None:
            hit = n - 1; gia_ra = cl[-1]
        nights = dem_swap(t[j], t[hit])
        swap_pts = nights * swap_nam / 365 * e
        out.append(dict(ngay=day, nam=day.year, treo_pts=e - lo, gio=(t[hit] - t[j]).total_seconds() / 3600, dem=nights,
                        swap_pts=swap_pts, net_pts=(gia_ra - e) - spread_pts - swap_pts))
    return pd.DataFrame(out)


def so_quan_ly(d, entries, tp, sp, nhan):
    print(f"\n=== {nhan}: TP {tp} diem, spread {sp} diem ===")
    for mode in ("giu", "ha_dem", "ha_phien", "cat_phien"):
        r = chay_quan_ly(d, entries, tp, sp, mode)
        thua = (r.net_pts < 0).mean() * 100
        print(f"{mode:10s} n={len(r):4d}  NET TB/lenh={r.net_pts.mean():+5.2f}  tong={r.net_pts.sum():+7.0f}  lenh am={thua:4.1f}%  "
              f"lo/lenh am TB={r[r.net_pts<0].net_pts.mean() if (r.net_pts<0).any() else 0:+6.1f}  lenh xau nhat={r.net_pts.min():+7.0f}  "
              f"treo toi da={r.treo_pts.max():5.0f}  qua dem={(r.dem>0).mean()*100:3.0f}%  swap TB={r.swap_pts.mean():4.2f}")


if __name__ == "__main__" and "--quan-ly" in sys.argv:
    d = O.nap(); entries, _ = O.tim_setup(d)
    nay = [e for e in entries if e[3] >= pd.Timestamp("2023-01-01")]
    for sp in (0.6, 1.5):
        so_quan_ly(d, nay, 5.5, sp, "2023-2026")
    so_quan_ly(d, entries, 5.5, 1.5, "2016-2026 (gia thap hon, 5,5 diem lon hon theo %)")
