# -*- coding: utf-8 -*-
"""Ban Python DONG LOGIC voi BRAIN_V24_Chung.mqh (RSI / MRZ trailing D1) - mo phong theo su kien 'mo nen moi' nhu EA.
Dung de kiem tuong duong voi v22.chay(thoat='TR2') + v19.tin_hieu ma v24.py dung."""
from __future__ import annotations

import math

ATR_N, RSI_N, MRZ_N, SL_ATR, TR_ATR, GIU = 14, 14, 50, 1.5, 2.0, 72


def chi_bao(o, h, l, c, che_do):
    """tra ve (atr[i], tin[i]) tinh nhu ChiBao() tren cac nen 0..i (nen i vua dong)."""
    n = len(c); A = [0.0] * n; T = [0] * n; atr = h[0] - l[0]; A[0] = atr; eu = ed = None
    for i in range(1, n):
        pc = c[i - 1]; tr = max(h[i] - l[i], abs(h[i] - pc), abs(l[i] - pc)); atr += (tr - atr) / ATR_N; A[i] = atr
        d = c[i] - pc; u, v = max(d, 0.0), max(-d, 0.0)
        if eu is None: eu, ed = u, v
        else: eu += (u - eu) / RSI_N; ed += (v - ed) / RSI_N
        if che_do == "RSI":
            if eu == 0 and ed == 0: continue
            r = 100.0 if ed == 0 else 100 - 100 / (1 + eu / ed); T[i] = 1 if r < 30 else (-1 if r > 70 else 0)
        elif i >= MRZ_N - 1:
            w = c[i - MRZ_N + 1:i + 1]; m = sum(w) / MRZ_N; sd = math.sqrt(sum((x - m) ** 2 for x in w) / (MRZ_N - 1))
            if sd > 0: z = (c[i] - m) / sd; T[i] = 1 if z < -2 else (-1 if z > 2 else 0)
    return A, T


def ea(o, h, l, c, che_do, sp=None, bat_dau=60):
    """Moi vong k = 'mo nen k'. Tra ve danh sach (j_vao, huong, gia_vao, k_ra_bar, gia_ra)."""
    n = len(c); sp = sp or [0.0] * n; A, T = chi_bao(o, h, l, c, che_do); out = []; pos = None
    for k in range(bat_dau + 1, n):
        if pos is not None:                                    # 1) mo nen k: het han 72 nen -> dong o open; neu khong: trailing theo nen k-1 vua dong
            s, j, E, st, best = pos
            if k - j >= GIU: out.append((j, s, E, k, o[k] if s > 0 else o[k] + sp[k])); pos = None; continue
            best = c[k - 1] if best is None else (max(best, c[k - 1]) if s > 0 else min(best, c[k - 1]))
            st = max(st, best - TR_ATR * A[k - 1]) if s > 0 else min(st, best + TR_ATR * A[k - 1]); pos = (s, j, E, st, best)
        elif T[k - 1] != 0:
            s = T[k - 1]; E = o[k] + sp[k] if s > 0 else o[k]; st = E - s * SL_ATR * A[k - 1]; pos = (s, k, E, st, None)
        if pos is not None:                                    # 3) SL cham trong nen k (MT5 khop o SL; khong co gap trong du lieu test)
            s, j, E, st, best = pos
            if (s > 0 and l[k] <= st) or (s < 0 and h[k] + sp[k] >= st): out.append((j, s, E, k, st)); pos = None
    return out
