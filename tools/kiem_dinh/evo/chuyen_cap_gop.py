# -*- coding: utf-8 -*-
"""Kiem LUAT DONG BANG tren cac cap KHAC (khong tinh cap goc) - gop lenh nhieu cap (Evo 15/11/2026).
p gop: thong ke = tong loi rong moi cap; null = moi cap dich vong DOC LAP 999 lan. Chi doc nao.db."""
import json, os, sys
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.environ.get("BRAIN_GOC", "/workspace/brain2"))
sys.path.insert(0, os.path.dirname(__file__))
import danh_gia_lai as D

FX = ["AUDCAD", "AUDCHF", "AUDNZD", "EURCAD", "EURGBP", "GBPAUD", "GBPCAD", "NZDCAD", "EURUSD", "USDCAD", "USDCHF", "USDJPY"]


def mot(gt):
    from tru import quantlab as Q
    from nhan import mau as MAU, mo_phong as MP, ngu_phap as NP
    NP.nap_vao_mau(); ts = json.loads(gt["tham_so"] or "{}"); kh = gt["khung"]
    ds, tong_lt = [], []
    for m in FX:
        if m == gt["tai_san"]: continue
        try:
            _d, _t, h, _c, cp = Q._nap(m, kh)
            kq = MP.chay(h, MAU.sinh(gt["template"], h, ts), cp, ma=m, khung=kh)
        except Exception:
            continue
        v = kq.vi_the; ra = np.expm1(kq.r); sp, A, B = D._mang_phi(cp, h.index, len(v))
        loi = D._loi(v[None, :], ra, sp, A, B)[0]
        lt = [loi[a:b].sum() for a, b in D._gio(v)]
        tong_lt += lt; ds.append((m, v, ra, sp, A, B, float(loi.sum()), len(lt)))
    if not ds: return {"ma": gt["ma"], "loi": "khong co cap"}
    lt = np.array(tong_lt); that = sum(x[6] for x in ds)
    rng = np.random.default_rng(7); null = np.zeros(D.N_NULL)
    for (m, v, ra, sp, A, B, _s, _n) in ds:
        n = len(v); ar = np.arange(n); sh = rng.integers(1, n, D.N_NULL)
        for c in range(0, D.N_NULL, 50):
            S = sh[c:c + 50]; null[c:c + len(S)] += D._loi(v[(ar[None, :] - S[:, None]) % n], ra, sp, A, B).sum(axis=1)
    th, tl = lt[lt > 0].sum(), -lt[lt < 0].sum()
    return {"ma": gt["ma"], "so_cap": len(ds), "cap_duong": sum(1 for x in ds if x[6] > 0),
            "so_lenh": int(len(lt)), "pf_lenh": round(float(th / tl), 3) if tl > 0 else None,
            "tb_lenh_pct": round(float(lt.mean() * 100), 4) if len(lt) else 0,
            "p_gop": round(float((np.sum(null >= that) + 1) / (D.N_NULL + 1)), 4),
            "chi_tiet": {x[0]: [round(x[6] * 100, 2), x[7]] for x in ds}}


if __name__ == "__main__":
    import sqlite3
    ds = json.load(open(sys.argv[1]))
    c = sqlite3.connect("file:/workspace/brain2/nao.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
    gts = [dict(c.execute("SELECT * FROM gia_thuyet WHERE ma=?", (m,)).fetchone()) for m in ds]
    gts = [g for g in gts if g["tai_san"] in FX]
    with Pool(7) as p: ra = p.map(mot, gts, chunksize=2)
    json.dump(ra, open(sys.argv[2], "w"), ensure_ascii=False)
    for r in sorted(ra, key=lambda r: r.get("p_gop", 1)):
        print(r["ma"][:70], {k: r.get(k) for k in ("so_cap", "cap_duong", "so_lenh", "pf_lenh", "tb_lenh_pct", "p_gop")})
