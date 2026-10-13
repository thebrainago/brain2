# -*- coding: utf-8 -*-
"""Kiem toi uu phan_tich_luoi_box (chu ky 5): chi bao co dem + chay song song phai TRUNG TUNG BIT voi cong thuc goc."""
import gzip
import math
import random

import pandas as pd

import phan_tich_luoi_box as P


def _chi_bao_goc(h, l, c, che, z_ng, mrz_n, r_thap, r_cao):
    n = len(c); A = [0.0] * n; T = [0] * n; atr = h[0] - l[0]; A[0] = atr; eu = ed = None
    for i in range(1, n):
        pc = c[i - 1]; tr = max(h[i] - l[i], abs(h[i] - pc), abs(l[i] - pc)); atr += (tr - atr) / 14; A[i] = atr
        d = c[i] - pc; u, v = max(d, 0.0), max(-d, 0.0)
        if eu is None: eu, ed = u, v
        else: eu += (u - eu) / 14; ed += (v - ed) / 14
        if che == "RSI":
            if eu == 0 and ed == 0: continue
            r = 100.0 if ed == 0 else 100 - 100 / (1 + eu / ed); T[i] = 1 if r < r_thap else (-1 if r > r_cao else 0)
        elif i >= mrz_n - 1:
            w = c[i - mrz_n + 1:i + 1]; m = sum(w) / mrz_n; sd = math.sqrt(sum((x - m) ** 2 for x in w) / (mrz_n - 1))
            if sd > 0:
                z = (c[i] - m) / sd; T[i] = 1 if z < -z_ng else (-1 if z > z_ng else 0)
    return A, T


def _chuoi(n=600, seed=3):
    rnd = random.Random(seed); c = [1.0]; o = []; h = []; l = []
    for i in range(n):
        p = c[-1] * (1 + rnd.gauss(0, 0.006)); op = c[-1]
        if i % 97 == 5: p = op  # nen phang de thu nhanh eu==ed==0 / sd==0
        o.append(op); h.append(max(op, p) * 1.002); l.append(min(op, p) * 0.998); c.append(p)
    return o, h, l, c[1:]


def test_chi_bao_co_dem_trung_goc():
    o, h, l, c = _chuoi()
    dem = {}
    for che, z, n, a, b in [("MRZ", 1.5, 20, 30, 70), ("MRZ", 2.5, 20, 30, 70), ("MRZ", 2.0, 100, 30, 70), ("RSI", 2, 50, 20, 80), ("RSI", 2, 50, 30, 70)]:
        assert P.chi_bao(h, l, c, che, z, n, a, b, dem) == _chi_bao_goc(h, l, c, che, z, n, a, b)
        assert P.chi_bao(h, l, c, che, z, n, a, b) == _chi_bao_goc(h, l, c, che, z, n, a, b)


def test_mo_phong_tru_phi_sau_trung_bit():
    o, h, l, c = _chuoi(seed=9)
    A, T = _chi_bao_goc(h, l, c, "MRZ", 1.5, 20, 30, 70)
    cp = 0.00023
    goc = P.mo_phong(o, h, l, c, A, T, 1.5, 2.0, 20, cp)
    moi = [(j, x - cp) for j, x in P.mo_phong(o, h, l, c, A, T, 1.5, 2.0, 20, 0.0)]
    assert goc == moi and len(goc) > 5


def test_song_song_trung_tuan_tu(tmp_path):
    for ma, s in (("AUDUSD", 1), ("GBPUSD", 2)):
        o, h, l, c = _chuoi(n=3800, seed=s)
        t = pd.date_range("2013-01-01", periods=len(c), freq="D")
        pd.DataFrame({"time": t, "open": o, "high": h, "low": l, "close": c}).to_csv(tmp_path / f"{ma}_D1.csv", index=False)
    P.chay(str(tmp_path), str(tmp_path / "a.json"), 1)
    P.chay(str(tmp_path), str(tmp_path / "b.json"), 2)
    a = gzip.open(tmp_path / "a_chi_tiet.jsonl.gz", "rt").read(); b = gzip.open(tmp_path / "b_chi_tiet.jsonl.gz", "rt").read()
    assert a == b and a.count("\n") > 100
