# -*- coding: utf-8 -*-
"""Vong 18: straddle phien A, straddle tin, breakout, kiet suc-dao chieu, hedging-recovery tren FX H1 bid/ask that.
Dang ky truoc reports/vong18_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pandas as pd

import lich_su_kien as LS
import mua_vu as MV
import v17_fx as F

XM = 1.2


def chuan_bi(cap):
    d = F.tai(cap)
    _, _, atr, _ = F.chi_bao(d)
    return d, atr


def _ra(s, entry, x_bid, sp, slip):
    return (x_bid - entry - slip) if s > 0 else (entry - (x_bid + sp) - slip)


def mo_phong(d, atr, he, bien, hs=1.0, slip_pip=0.0, cap="eurusd"):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    sp = d["spread_open"].to_numpy() * XM * hs
    pip = 0.01 if "jpy" in cap else 1e-4; slip = slip_pip * pip
    t = d.index; hr = t.hour.to_numpy(); ngay = t.normalize()
    nd = ngay.asi8; n = len(c); lenh = []
    ev = set()
    if he == "B2":
        ev = set(LS.nfp(2023, 2026)) | set(LS.cpi())
    i = 30
    while i < n - 2:
        # ---- tao lenh cho (pending) hoac tin hieu thi truong
        cho = None   # (buy_level, sell_level, sl_d, tp_d, start, het_ngay)
        thi = None   # (s, start, sl_d, tp_d, trail)
        a = atr[i]
        if not np.isfinite(a) or a <= 0: i += 1; continue
        if he == "B1" and hr[i] == 7 and (i + 1 < n and nd[i + 1] == nd[i]):
            m = (nd == nd[i]) & (hr <= 7)
            st = np.argmax(m); hi, lo = h[st:i + 1].max(), l[st:i + 1].min(); w = hi - lo
            if w > 0:
                cho = (hi, lo, w, w, i + 1, True)
        elif he == "B2" and hr[i] == 14 and t[i].date() in ev:
            cho = (c[i] + 0.5 * a, c[i] - 0.5 * a, a, a, i + 1, True)
        elif he == "B3":
            if c[i] > h[i - 24:i].max(): thi = (1, i + 1, None, None, 2.0)
            elif c[i] < l[i - 24:i].min(): thi = (-1, i + 1, None, None, 2.0)
        elif he == "B4":
            dir3 = np.sign(c[i - 2:i + 1] - o[i - 2:i + 1])
            if abs(dir3.sum()) == 3 and (h[i - 2:i + 1].max() - l[i - 2:i + 1].min()) > 3 * a:
                rg = h[i] - l[i]
                if rg > 0:
                    if dir3[0] > 0 and (h[i] - c[i]) <= 0.25 * rg: thi = (-1, i + 1, 1.5 * a, 1.0 * a, None)
                    elif dir3[0] < 0 and (c[i] - l[i]) <= 0.25 * rg: thi = (1, i + 1, 1.5 * a, 1.0 * a, None)
        if cho is None and thi is None: i += 1; continue
        # ---- bien the chot nhanh
        tmax = None
        if bien == "TP_NHO":
            if cho: cho = cho[:2] + (1.0 * a, 0.5 * a) + cho[4:]
            else: thi = (thi[0], thi[1], 1.0 * a, 0.5 * a, None)
        elif bien == "GIO3":
            tmax = 3
        # ---- khop
        if cho:
            bl, sl_, sld, tpd, j, het = cho; s = 0; entry = None
            while j < n and nd[j] == nd[cho[4] - 1 if cho[4] - 1 >= 0 else j]:
                up = h[j] + sp[j] >= bl; dn = l[j] <= sl_
                if up and dn:   # ca hai cung bar: khong biet thu tu -> chon chan xau nhat sau nay (SL ngay) - dung buy
                    s, entry = 1, max(bl, o[j] + sp[j]); break
                if up: s, entry = 1, max(bl, o[j] + sp[j]); break
                if dn: s, entry = -1, min(sl_, o[j]); break
                j += 1
            if s == 0: i = j; continue
            both = up and dn
        else:
            s, j, sld, tpd, tr = thi; het = False; both = False
            entry = o[j] + sp[j] if s > 0 else o[j]
        # ---- quan ly
        k = j; best = c[j]; ra = None; dau = nd[j]
        while k < n - 1:
            if sld is not None:
                if s > 0:
                    sl_hit = l[k] <= entry - sld; tp_hit = h[k] >= entry + tpd
                else:
                    sl_hit = h[k] + sp[k] >= entry + sld; tp_hit = l[k] + sp[k] <= entry - tpd
                if k == j and both: sl_hit = True
                if sl_hit:   # xau nhat: SL truoc
                    xb = entry - sld if s > 0 else entry + sld - sp[k]; ra = _ra(s, entry, xb, sp[k], slip); break
                if tp_hit and k > j:
                    xb = entry + tpd if s > 0 else entry - tpd - sp[k]; ra = _ra(s, entry, xb, sp[k], slip); break
            if thi is not None and thi[4] and bien != "TP_NHO":
                best = max(best, c[k]) if s > 0 else min(best, c[k])
                if (s > 0 and c[k] < best - 2 * atr[k]) or (s < 0 and c[k] > best + 2 * atr[k]) or k - j >= 48:
                    ra = _ra(s, entry, o[k + 1], sp[k + 1], slip); k += 1; break
            if tmax and k - j + 1 >= tmax: ra = _ra(s, entry, o[k + 1], sp[k + 1], slip); k += 1; break
            if het and nd[k + 1] != dau: ra = _ra(s, entry, o[k + 1], sp[k + 1], slip); k += 1; break
            if sld is None and thi is None: break
            if thi is not None and not thi[4] and sld is None and k - j >= 48: ra = _ra(s, entry, o[k + 1], sp[k + 1], slip); k += 1; break
            k += 1
        if ra is None: break
        dem = int(np.sum(np.diff(hr[j:k + 1]) < 0))
        lenh.append((t[j], ra / entry - dem * F.QD))
        i = max(k, i + 1)
    return lenh


def hedge(d, atr, cap, hs=1.0, slip_pip=0.0, von0=10_000.0, lot0=1000.0, toi_da=5):
    """B5 hedging-recovery (martingale an). Tra (cac chu ky (thoi diem, lai USD), duong von theo bar)."""
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    sp = d["spread_open"].to_numpy() * XM * hs; pip = 0.01 if "jpy" in cap else 1e-4; slip = slip_pip * pip
    usd = (lambda x, p: x) if cap in ("eurusd", "gbpusd", "audusd", "nzdusd") else (lambda x, p: x / p)
    n = len(c); von = von0; eq = np.full(n, von0); chu_ky = []; i = 101
    while i < n - 2 and von > 0:
        a = atr[i]
        if not np.isfinite(a) or a <= 0: i += 1; continue
        j = i + 1; lot = {1: lot0, -1: lot0}; vao = {1: o[j] + sp[j], -1: o[j]}; thuc = 0.0; buoc = 0; xong = False; k = j
        while k < n - 1:
            for s in (1, -1):
                nguong = vao[s] - a if s > 0 else vao[s] + a
                cham = (l[k] <= nguong) if s > 0 else (h[k] + sp[k] >= nguong)
                if cham:
                    x = (nguong - vao[s] - slip) if s > 0 else (vao[s] - nguong - slip)
                    thuc += usd(x * lot[s], c[k]); buoc += 1
                    if buoc > toi_da: xong = True; break
                    lot[s] *= 2; vao[s] = (nguong + sp[k] + slip) if s > 0 else (nguong - slip)
            noi = usd((c[k] - vao[1]) * lot[1], c[k]) + usd((vao[-1] - (c[k] + sp[k])) * lot[-1], c[k])
            eq[k] = von + thuc + noi
            if eq[k] <= 0: xong = True
            if xong or thuc + noi >= usd(0.5 * a * lot0, c[k]):
                tong = thuc + noi; von += tong; chu_ky.append((d.index[k], tong)); eq[k:] = von; break
            k += 1
        i = k + 1
    return chu_ky, eq


def tk(lenh, giua):
    a = np.array([x for t, x in lenh if t < giua]); b = np.array([x for t, x in lenh if t >= giua])
    if len(a) < 15 or len(b) < 15 or b.std(ddof=1) == 0: return None
    eq = np.cumprod(1 + np.array([x for _, x in lenh])); dd = float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100
    return {"n_ph": len(a), "n_kiem": len(b), "ph_pct": float(a.sum() * 100), "kiem_pct": float(b.sum() * 100),
            "p": MV.p1(b.mean() / b.std(ddof=1) * math.sqrt(len(b))), "maxdd_pct": dd}


def main(ra=None):
    out = []; hd = []
    for cap in F.CAP:
        d, atr = chuan_bi(cap); giua = d.index[len(d) // 2]
        for he in ("B1", "B2", "B3", "B4"):
            for bien in ("GOC", "TP_NHO", "GIO3"):
                r = {"cap": cap, "he": he, "bien": bien}
                s = tk(mo_phong(d, atr, he, bien, cap=cap), giua)
                if s:
                    r.update(s)
                    s2 = tk(mo_phong(d, atr, he, bien, 1.5, 0.5, cap), giua); r["kiem_x1_5_truot05_pct"] = s2["kiem_pct"] if s2 else None
                    r["do_nhay_truot"] = {str(sl): (tk(mo_phong(d, atr, he, bien, 1.0, sl, cap), giua) or {}).get("kiem_pct") for sl in (0.5, 1.0)}
                out.append(r)
        for bien, lot0 in (("GOC", 1000.0),):
            ck, eq = hedge(d, atr, cap); ck2, eq2 = hedge(d, atr, cap, 1.5, 0.5)
            dd = float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100
            hd.append({"cap": cap, "chu_ky": len(ck), "lai_pct": float((eq[-1] / 1e4 - 1) * 100), "maxdd_pct": dd, "chay": bool(eq[-1] <= 0),
                       "lai_x1_5_truot05_pct": float((eq2[-1] / 1e4 - 1) * 100), "ty_le_chu_ky_lo_pct": float(np.mean([x < 0 for _, x in ck]) * 100) if ck else None,
                       "lo_lon_nhat_usd": float(min(x for _, x in ck)) if ck else None})
        print(cap, "xong", flush=True)
    v = [r for r in out if "p" in r]
    ho0 = json.load(open("reports/vong17_hang_hoa.json"))["ho_holm"]
    cu = [1.0] * 0
    # p cu: lay lai dung ho 5.061 tu bao cao vong 17
    import v14
    cu = v14.p_cu() + [x["p"] for x in json.load(open("reports/vong14.json"))["o"]] + [x["p"] for x in json.load(open("reports/vong15.json"))["he"]] + \
        [x["p"] for x in json.load(open("reports/vong15.json"))["cpi"]] + [x["p"] for x in json.load(open("reports/vong16.json"))["o"]] + \
        [x["p"] for x in json.load(open("reports/vong17_don_bay.json"))["loc"]] + [x["p"] for x in json.load(open("reports/vong17_fx.json"))["o"] if "p" in x] + \
        [x["p"] for x in json.load(open("reports/vong17_hang_hoa.json"))["o"]]
    assert len(cu) == ho0
    H = MV.holm(cu + [r["p"] for r in v])
    for r, q in zip(v, H[len(cu):]):
        r["p_holm"] = q
        r["song"] = q < 0.05 and r["ph_pct"] > 0 and r["kiem_pct"] > 0 and (r["kiem_x1_5_truot05_pct"] or -1) > 0 and r["maxdd_pct"] < 80
    v.sort(key=lambda r: r["p"])
    print("o", len(out), "du lenh", len(v), "ho", len(H), "song", sum(r["song"] for r in v))
    for r in v[:10]:
        print(r["cap"], r["he"], r["bien"], "n", r["n_ph"], r["n_kiem"], "ph %.1f kiem %.1f x1.5+0.5pip %s" % (r["ph_pct"], r["kiem_pct"], r["kiem_x1_5_truot05_pct"]),
              "p %.4f holm %.3f DD %.1f" % (r["p"], r["p_holm"], r["maxdd_pct"]), r["do_nhay_truot"])
    import collections
    for he in ("B1", "B2", "B3", "B4"):
        for bien in ("GOC", "TP_NHO", "GIO3"):
            xs = [r for r in v if r["he"] == he and r["bien"] == bien]
            if xs: print(he, bien, "so cap", len(xs), "TV kiem %.1f" % np.median([r["kiem_pct"] for r in xs]),
                         "TV truot0.5 %.1f truot1 %.1f" % (np.median([r["do_nhay_truot"]["0.5"] or 0 for r in xs]), np.median([r["do_nhay_truot"]["1.0"] or 0 for r in xs])))
    for x in hd: print("HEDGE", x)
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": out, "hedge": hd}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
