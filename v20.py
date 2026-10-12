# -*- coding: utf-8 -*-
"""Vong 20: loc trang thai thi truong -> chon nhom chien luoc. Dang ky truoc reports/vong20_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

import mua_vu as MV
import v17_fx as F
import v19
import v19b

THOAT = ["TR2", "GIO6", "TP"]


def dac_trung(d, atr):
    c, h, l = d["close"], d["high"], d["low"]
    er = (c - c.shift(20)).abs() / c.diff().abs().rolling(20).sum()
    up, dn = h.diff(), -l.diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    A = pd.Series(atr, index=d.index)
    pdi = 100 * pd.Series(pdm, index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / A
    mdi = 100 * pd.Series(mdm, index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / A
    adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean()
    atr_med = A.shift().rolling(500, min_periods=100).median()
    r24 = (c / c.shift(24) - 1).abs()
    return er, adx, A, atr_med, r24


def c1(er, adx, A, atr_med):
    xh = ((er > 0.30) | (adx > 25)).to_numpy(); bd = (A > atr_med).to_numpy()
    s = np.where(xh, 2, 0) + np.where(bd, 1, 0)
    s = s.astype(float); s[~np.isfinite(er.to_numpy()) | ~np.isfinite(atr_med.to_numpy())] = np.nan
    return s   # 0 ngang-yen, 1 ngang-dong, 2 xu huong-yen, 3 xu huong-dong


def c2(d, er, A, r24, giua):
    X = np.column_stack([np.log(A / d["close"]), er, r24]); ok = np.isfinite(X).all(1)
    tr = ok & np.asarray(d.index < giua)
    g = GaussianMixture(3, random_state=20).fit(X[tr])
    lab = np.full(len(d), np.nan); lab[ok] = g.predict(X[ok])
    od = np.argsort(g.means_[:, 0])                       # xep theo bien dong de can nhan giua cac lan fit
    m = {int(k): i for i, k in enumerate(od)}
    return np.array([m[int(x)] if np.isfinite(x) else np.nan for x in lab])


def tat_ca_tin(d, giua):
    s1, atr, _ = v19.tin_hieu(d); s2 = v19b.tin_moi(d, atr, giua); s1.update(s2); return s1, atr


def lenh_co_trang_thai(d, s, atr, trang):
    pos = pd.Series(np.arange(len(d)), index=d.index); out = {}
    for v, tin in s.items():
        for th in THOAT:
            L = v19.chay(d, tin, th, atr)
            out[(v, th)] = [(t, r, trang[pos[t] - 1] if pos[t] >= 1 else np.nan) for t, r in L]   # trang thai tai nen tin hieu
    return out


def nhom(v): return v19b.NHOM2.get(v) or v19.VAO_NHOM[v]


def main(ra=None):
    bo = {}
    for cap in F.CAP:
        d = F.tai(cap); bo[("bo1", cap)] = d
    for ten, (d, cap) in v19b.bo2().items(): bo[("bo2", ten)] = d
    DL = {}
    for k, d in bo.items():
        giua = d.index[len(d) // 2]; s, atr = tat_ca_tin(d, giua)
        er, adx, A, am, r24 = dac_trung(d, atr)
        st1 = c1(er, adx, A, am); st2 = c2(d, er, A, r24, giua)
        DL[k] = {"giua": giua, "C1": lenh_co_trang_thai(d, s, atr, st1), "st": {"C1": st1, "C2": st2}, "er": er, "d": d, "s": s, "atr": atr}
        DL[k]["C2"] = {kk: [(t, r, st2[DL[k]['d'].index.get_loc(t) - 1]) for t, r, _ in v] for kk, v in DL[k]["C1"].items()}
        print(k, "xong", flush=True)
    kq = {"anh_xa": {}, "o": [], "bang": {}, "doi_trang_thai": {}, "do_tre": {}}
    for B in ("C1", "C2"):
        # chon anh xa tren nua phat hien bo 1
        tong = defaultdict(list)
        for (b, cap), x in DL.items():
            if b != "bo1": continue
            for kk, L in x[B].items():
                for t, r, s in L:
                    if t < x["giua"] and np.isfinite(s): tong[(int(s), kk)].append(r)
        ax = {}
        for s in range(4 if B == "C1" else 3):
            ung = [(np.mean(v), kk) for (ss, kk), v in tong.items() if ss == s and len(v) >= 30]
            best = max(ung) if ung else (0, None)
            ax[s] = best[1] if best[0] > 0 else None
        kq["anh_xa"][B] = {str(s): (list(k) if k else None) for s, k in ax.items()}; print(B, "anh xa", ax)
        # he chuyen trang thai
        for (b, cap), x in DL.items():
            for hs in (1.0, 1.5):
                if hs == 1.5:
                    d = x["d"]; pos = pd.Series(np.arange(len(d)), index=d.index); st = x["st"][B]
                    L15 = {}
                    for s_, kk in ax.items():
                        if kk: L15[kk] = [(t, r, st[pos[t] - 1]) for t, r in v19.chay(d, x["s"][kk[0]], kk[1], x["atr"], 1.5)]
                    src = L15
                else:
                    src = {kk: x[B][kk] for kk in set(k for k in ax.values() if k)}
                L = sorted([(t, r) for s_, kk in ax.items() if kk for t, r, s in src[kk] if np.isfinite(s) and int(s) == s_])
                # bo lenh chong (hai to hop cung luc): giu lenh dau, cach toi thieu 1 nen
                if b == "bo1": L = [(t, r) for t, r in L if t >= x["giua"]]
                a = np.array([r for _, r in L])
                if hs == 1.0:
                    o = {"bo_phan_loai": B, "bo": b, "chuoi": cap, "n": len(a)}
                    if len(a) >= 15 and a.std(ddof=1) > 0:
                        eq = np.cumprod(1 + a); o.update(tong_pct=float(a.sum() * 100), p=MV.p1(a.mean() / a.std(ddof=1) * math.sqrt(len(a))),
                                                       maxdd_pct=float(np.max(1 - eq / np.maximum.accumulate(eq)) * 100))
                    kq["o"].append(o)
                else:
                    kq["o"][-1]["tong_x1_5_pct"] = float(a.sum() * 100) if len(a) else None
        # bang nhom x trang thai (bps/lenh), nua kiem bo1 va toan bo2
        bang = defaultdict(list)
        for (b, cap), x in DL.items():
            for kk, L in x[B].items():
                for t, r, s in L:
                    if not np.isfinite(s) or (b == "bo1" and t < x["giua"]): continue
                    bang[(b, nhom(kk[0]), int(s))].append(r)
        kq["bang"][B] = {f"{b}|{g}|{s}": [round(float(np.mean(v)) * 1e4, 2), len(v)] for (b, g, s), v in sorted(bang.items())}
        # tan suat doi trang thai
        dd = []
        for x in DL.values():
            st = x["st"][B]; st = st[np.isfinite(st)]; ch = np.sum(st[1:] != st[:-1]); dd.append(len(st) / max(ch, 1))
        kq["doi_trang_thai"][B] = round(float(np.median(dd)), 1)
    # do tre ER20 (thoi gian thuc vs cua so tam)
    lag = []
    for x in DL.values():
        c = x["d"]["close"]; er = x["er"]
        erc = ((c.shift(-10) - c.shift(10)).abs() / c.diff().abs().rolling(20).sum().shift(-10))
        cc = [er.shift(-k).corr(erc) for k in range(0, 21)]; lag.append(int(np.argmax(cc)))
    kq["do_tre"]["ER20_nen"] = float(np.median(lag))
    # Holm
    cu = v19.ho_cu(); J = json.load(open("reports/vong19.json")); Jb = json.load(open("reports/vong19b.json"))
    cu += [r["p"] for r in J["o"] + J["ghep"] if "p" in r] + [r["p"] for r in Jb["o"] if "p" in r]
    assert len(cu) == Jb["ho_holm"]
    v = [o for o in kq["o"] if "p" in o]; H = MV.holm(cu + [o["p"] for o in v])
    for o, h in zip(v, H[len(cu):]):
        o["p_holm"] = h; o["song"] = h < 0.05 and o["tong_pct"] > 0 and (o.get("tong_x1_5_pct") or -1) > 0 and o["maxdd_pct"] < 80
    kq["ho_holm"] = len(H)
    print("ho", len(H), "o", len(kq["o"]), "song", sum(o.get("song", False) for o in v))
    for o in kq["o"]: print(o)
    print("doi trang thai (nen/doan)", kq["doi_trang_thai"], "do tre", kq["do_tre"])
    for B in kq["bang"]:
        print("BANG", B)
        for k, x in kq["bang"][B].items(): print("  ", k, x)
    # so sanh: to hop duoc chon chay rieng khong loc (nua kiem bo1 + bo2)
    ss = {}
    for B in ("C1", "C2"):
        for kk in set(tuple(k) for k in kq["anh_xa"][B].values() if k):
            for b in ("bo1", "bo2"):
                rs = [r for (bb, cap), x in DL.items() if bb == b for t, r, _ in x["C1"][kk] if b == "bo2" or t >= x["giua"]]
                ss[f"{B}|{kk}|{b}"] = [round(float(np.mean(rs)) * 1e4, 2) if rs else None, len(rs)]
    kq["khong_loc"] = ss; print("KHONG LOC (bps/lenh)", ss)
    if ra: json.dump(kq, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
