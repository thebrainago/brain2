# -*- coding: utf-8 -*-
"""
TEST E – BẢN ĐỒ XÁC SUẤT TRONG NGÀY (scalp): từ giá mở cửa ngày / mở phiên / các mốc ngày trước,
giá chạm những đích nào với xác suất cao nhất?
Dữ liệu 1h: GC=F, ES=F (ngày futures 18:00→17:00 NY; vàng thêm biến thể ngày UTC), ^GSPC giờ RTH.
Mọi mốc chỉ dùng thông tin đã biết tại thời điểm neo. ATR = ATR14 ngày (của các ngày TRƯỚC).
"""
import numpy as np, pandas as pd

GRID = np.round(np.arange(0.05, 2.001, 0.05), 2)             # lưới khoảng cách theo ATR ngày
PCT = [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0]
ROUND = {"GC=F": [10, 25, 50], "ES=F": [25, 50], "^GSPC": [25, 50]}
LEGS = [0.15, 0.25, 0.5]
SPREAD = {"GC=F": 0.3, "ES=F": 0.25, "^GSPC": 0.5}


def sq9(p, ang, side):
    r = np.sqrt(p) + side * ang / 180.0
    return r * r


def atr14(dh, dl, dc):
    pc = np.r_[np.nan, dc[:-1]]
    tr = np.nanmax(np.vstack([dh - dl, np.abs(dh - pc), np.abs(dl - pc)]), axis=0)
    a = pd.Series(tr).ewm(alpha=1 / 14, adjust=False).mean().values
    return a


def build_days(tk, mode):
    f = {"GC=F": "data_GCF_1h.pkl", "ES=F": "data_ESF_1h.pkl", "^GSPC": "data_GSPC_1h.pkl"}[tk]
    d = pd.read_pickle(f).dropna(subset=["Open", "High", "Low", "Close"])
    ny = d.index.tz_convert("America/New_York")
    utc = d.index.tz_convert("UTC"); lon = d.index.tz_convert("Europe/London")
    if mode == "fut": key = (ny + pd.Timedelta(hours=6)).date
    elif mode == "utc": key = utc.date
    else: key = ny.date
    df = pd.DataFrame({"o": d.Open.values, "h": d.High.values, "l": d.Low.values, "c": d.Close.values,
                       "day": key, "ny_h": ny.hour, "utc_h": utc.hour, "lon_h": lon.hour, "ts": ny.tz_localize(None)})
    days = [g.reset_index(drop=True) for _, g in df.groupby("day", sort=True)]
    days = [g for g in days if len(g) >= (5 if mode == "rth" else 15)]
    dh = np.array([g.h.max() for g in days]); dl = np.array([g.l.min() for g in days]); dc = np.array([g.c.iloc[-1] for g in days])
    atr = atr14(dh, dl, dc)
    # percentile ATR trong 120 ngày trước (chế độ biến động)
    atrp = pd.Series(atr).rolling(120, min_periods=40).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True).values
    return days, dh, dl, dc, atr, atrp


def touch_info(g, s, A, T):
    """Chạm T từ nến s (bao gồm) tới cuối ngày. Trả (chạm?, số giờ tới chạm, MAE (giá) trước chạm)."""
    h, l = g.h.values[s:], g.l.values[s:]
    m = (l <= T) & (h >= T)
    if T >= A: m = h >= T
    else: m = l <= T
    if not m.any(): return False, np.nan, np.nan
    k = int(m.argmax())
    mae = (A - l[:k + 1].min()) if T >= A else (h[:k + 1].max() - A)
    return True, k + 1, max(mae, 0.0)


def return_after_leg(g, s, A, leg):
    """Sau khi giá rời A ≥ leg (giá), có quay lại chạm A không? Trả (có leg?, quay lại?, giờ từ leg tới quay lại, hướng leg, MAE thêm sau leg)."""
    h, l = g.h.values[s:], g.l.values[s:]
    up = h >= A + leg; dn = l <= A - leg
    fu = up.argmax() if up.any() else 10**6; fd = dn.argmax() if dn.any() else 10**6
    if fu == fd == 10**6: return False, False, np.nan, 0, np.nan
    if fu == fd: return False, False, np.nan, 0, np.nan        # nến mơ hồ
    k, dirn = (fu, 1) if fu < fd else (fd, -1)
    rest_h, rest_l = h[k + 1:], l[k + 1:]
    back = (rest_l <= A) if dirn == 1 else (rest_h >= A)
    if back.any():
        j = int(back.argmax())
        ext = (rest_h[:j + 1].max() - (A + leg)) if dirn == 1 else ((A - leg) - rest_l[:j + 1].min())
        return True, True, j + 1, dirn, max(ext, 0)
    ext = (rest_h.max() - (A + leg)) if dirn == 1 and len(rest_h) else ((A - leg) - rest_l.min()) if len(rest_l) else 0
    return True, False, np.nan, dirn, max(ext, 0)


def session_start(g, tk, mode, which):
    if which == "day": return 0
    if which == "asia": m = g.utc_h.values == 0
    elif which == "london": m = g.lon_h.values == 8
    elif which == "ny": m = g.ny_h.values == 9
    else: return None
    return int(m.argmax()) if m.any() else None


def run(tk, mode):
    days, dh, dl, dc, atr, atrp = build_days(tk, mode)
    rows, beh, grid_rows, scalp = [], [], [], []
    n = len(days); half_date = days[n // 2].day.iloc[0]
    sessions = ["day"] + (["asia", "london", "ny"] if mode != "rth" else [])
    for i in range(15, n):
        g = days[i]; a = atr[i - 1]
        if not np.isfinite(a): continue
        pdh, pdl, pdc = dh[i - 1], dl[i - 1], dc[i - 1]; pdm = (pdh + pdl) / 2
        O = g.o.iloc[0]; per = "IS" if g.day.iloc[0] < half_date else "OOS"
        date = g.day.iloc[0]
        base = dict(ticker=tk, mode=mode, date=date, period=per, year=pd.Timestamp(date).year,
                    dow=pd.Timestamp(date).dayofweek, atr=a, atr_tercile=int(min(2, atrp[i - 1] * 3)) if np.isfinite(atrp[i - 1]) else -1,
                    gap="tren_PDC" if O > pdc else "duoi_PDC",
                    open_pos="tren_PDH" if O > pdh else "duoi_PDL" if O < pdl else "trong_bien")
        # ---- hướng giờ đầu ----
        fh_dir = "len" if g.c.iloc[0] > O else "xuong"
        base["fh_dir"] = fh_dir
        for ses in sessions:
            s = session_start(g, tk, mode, ses)
            if s is None or s >= len(g) - 1: continue
            A = g.o.iloc[s]
            tg = {}
            for pc in PCT:
                tg[f"+{pc}%"] = A * (1 + pc / 100); tg[f"-{pc}%"] = A * (1 - pc / 100)
            for k in (0.25, 0.5, 0.75, 1.0):
                tg[f"+{k}ATR"] = A + k * a; tg[f"-{k}ATR"] = A - k * a
            for ang in (45, 90, 180):
                tg[f"Sq9+{ang}"] = sq9(A, ang, 1); tg[f"Sq9-{ang}"] = sq9(A, ang, -1)
            tg["PDC"] = pdc; tg["PDH"] = pdh; tg["PDL"] = pdl; tg["PDM"] = pdm
            if ses != "day": tg["DayOpen"] = O
            for st in ROUND[tk]:
                up = np.ceil(A / st) * st; dn = np.floor(A / st) * st
                if up == A: up += st
                if dn == A: dn -= st
                tg[f"Tron{st}↑"] = up; tg[f"Tron{st}↓"] = dn
            for name, T in tg.items():
                hit, hrs, mae = touch_info(g, s, A, T)
                rows.append(dict(base, session=ses, target=name, dist_atr=(T - A) / a, dist_pct=100 * (T - A) / A,
                                 hit=hit, hours=hrs, mae_atr=mae / a if hit else np.nan))
            # lưới cho đường cong khoảng cách
            hh, ll = g.h.values[s:].max(), g.l.values[s:].min()
            grid_rows.append(dict(base, session=ses, up=(hh >= A + GRID * a), dn=(ll <= A - GRID * a)))
            # quay về neo sau một nhịp; đối chứng: mốc giả = neo ± 0.1/0.2 ATR
            for leg in LEGS:
                ok, back, hrs, dirn, ext = return_after_leg(g, s, A, leg * a)
                fake = []
                for off in (-0.2, -0.1, 0.1, 0.2):
                    ok2, b2, _, _, _ = return_after_leg(g, s, A + off * a, leg * a)
                    if ok2: fake.append(b2)
                beh.append(dict(base, session=ses, behavior=f"ve_lai_neo_sau_nhip_{leg}ATR", has=ok, hit=back if ok else np.nan,
                                hours=hrs, mae_atr=ext / a if ok else np.nan, base_rand=np.mean(fake) if fake else np.nan))
                # scalp: fade nhịp đầu về neo
                if ok:
                    hv, lv, cv = g.h.values[s:], g.l.values[s:], g.c.values[s:]
                    up = hv >= A + leg * a; dn = lv <= A - leg * a
                    k0 = (up.argmax() if dirn == 1 else dn.argmax())
                    E = A + dirn * leg * a
                    for slk in (0.25, 0.5, 1.0):
                        SL = E + dirn * slk * a; risk = slk * a; sp = SPREAD[tk]
                        if (dirn == 1 and hv[k0] >= SL) or (dirn == -1 and lv[k0] <= SL):
                            R = -(risk + sp) / risk
                        else:
                            R = None
                            for j in range(k0 + 1, len(hv)):
                                hitSL = hv[j] >= SL if dirn == 1 else lv[j] <= SL
                                hitTP = lv[j] <= A if dirn == 1 else hv[j] >= A
                                if hitSL: R = -(risk + sp) / risk; break
                                if hitTP: R = (leg * a - sp) / risk; break
                            if R is None: R = ((E - cv[-1]) * dirn - sp) / risk
                        scalp.append(dict(base, session=ses, strat=f"fade_nhip_{leg}ATR_ve_neo", SL=slk, R=R))
        # ---- hành vi theo ngày (neo = mở cửa ngày) ----
        h1, l1 = g.h.iloc[0], g.l.iloc[0]
        restH, restL = g.h.values[1:].max(), g.l.values[1:].min()
        H, L = g.h.max(), g.l.min()
        B = {"PDC_cham": L <= pdc <= H, "PDH_bi_vuot": H > pdh, "PDL_bi_thung": L < pdl, "PDH_hoac_PDL": (H > pdh) or (L < pdl),
             "PDH_va_PDL": (H > pdh) and (L < pdl), "PDM_cham": L <= pdm <= H,
             "dinh_gio_dau_bi_vuot": restH > h1, "day_gio_dau_bi_thung": restL < l1,
             "dinh_hoac_day_gio_dau_bi_pha": (restH > h1) or (restL < l1), "ca_dinh_va_day_gio_dau_bi_pha": (restH > h1) and (restL < l1),
             "mo_cua_duoc_cham_lai_sau_gio_dau": (restL <= O <= restH),
             "±0.25ATR_ca_hai": (H >= O + 0.25 * a) and (L <= O - 0.25 * a), "±0.5ATR_ca_hai": (H >= O + 0.5 * a) and (L <= O - 0.5 * a)}
        for k, v in B.items():
            beh.append(dict(base, session="day", behavior=k, has=True, hit=bool(v), hours=np.nan, mae_atr=np.nan, base_rand=np.nan))
        # scalp: đi về PDC / PDH-PDL gần nhất từ giá mở
        for nm, T in (("ve_PDC", pdc), ("ve_PDH_PDL_gan_nhat", pdh if abs(pdh - O) < abs(O - pdl) else pdl)):
            dd = (T - O) / a
            if not (0.1 <= abs(dd) <= 1.0) or (nm != "ve_PDC" and (O > pdh or O < pdl)): continue
            dirn = 1 if T > O else -1; sp = SPREAD[tk]
            for slk in (0.25, 0.5, 1.0):
                SL = O - dirn * slk * a; risk = slk * a; R = None
                for j in range(len(g)):
                    hitSL = g.l.iloc[j] <= SL if dirn == 1 else g.h.iloc[j] >= SL
                    hitTP = g.h.iloc[j] >= T if dirn == 1 else g.l.iloc[j] <= T
                    if hitSL: R = -(risk + sp) / risk; break
                    if hitTP: R = (abs(T - O) - sp) / risk; break
                if R is None: R = ((g.c.iloc[-1] - O) * dirn - sp) / risk
                scalp.append(dict(base, session="day", strat=nm, SL=slk, R=R, dist=abs(dd)))
    return pd.DataFrame(rows), pd.DataFrame(beh), pd.DataFrame(grid_rows), pd.DataFrame(scalp)


if __name__ == "__main__":
    R, Bh, G, S = [], [], [], []
    for tk, mode in (("GC=F", "fut"), ("GC=F", "utc"), ("ES=F", "fut"), ("^GSPC", "rth")):
        r, b, g, s = run(tk, mode); R.append(r); Bh.append(b); G.append(g); S.append(s)
        print(tk, mode, "ngày:", b[b.behavior == "PDC_cham"].shape[0], flush=True)
    pd.concat(R).to_pickle("results5/targets.pkl"); pd.concat(Bh).to_pickle("results5/behaviors.pkl")
    pd.concat(G).to_pickle("results5/grid.pkl"); pd.concat(S).to_pickle("results5/scalp.pkl")
