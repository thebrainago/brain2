# -*- coding: utf-8 -*-
"""Danh gia lai toan bo gia thuyet QUANTLAB voi tieu chi da sua (Evo 15/11/2026).

Chi DOC nao.db; khong ghi so, khong dang ky, khong tieu suat FDR.
Sua so voi audit cu:
  * PF / TB lenh tinh THEO LENH (gio = doan phoi nhiem cung dau lien tuc), khong theo bar.
  * p placebo = MOT p gop tu 999 lan dich vong (quay vong) mot phia, khong lay max nhieu hat.
  * Chi phi: mo hinh repo (A); bien the R1 = spread tick XM do that, truot 0, swap XM do that;
    R2 = nhu R1 nhung swap 0 (cap '#' tren tai khoan XM Ultra Low demo swap_mode=0).
Chay: python3 danh_gia_lai.py [so_tien_trinh]
"""
from __future__ import annotations
import json, os, sys, time
from multiprocessing import Pool
import numpy as np

GOC = os.environ.get("BRAIN_GOC", "/workspace/brain2")
sys.path.insert(0, GOC)
RA = os.environ.get("EVO_RA", "/workspace/brain2-run/danh_gia_lai.json")

# Spread tick trung vi (pip) + swap (point/lot/dem) do tren XM Ultra Low demo 15/11/2026 (E:\mt5_tester\p5)
THAT = {"AUDCAD": (2.9, 2.25, -10.38), "AUDNZD": (3.3, 0.17, -15.12), "EURCAD": (2.6, -6.55, -6.38),
        "EURGBP": (2.0, -5.87, 1.12), "AUDCHF": (2.0, 5.56, -10.32), "EURUSD": (1.1, -7.83, 1.44)}
N_NULL = 999


def _gio(v):
    """Danh sach (bat_dau, ket_thuc) cua tung lenh/gio: doan phoi nhiem cung dau lien tuc."""
    s = np.sign(np.round(v, 12))
    doi = np.flatnonzero(np.diff(np.concatenate(([0], s, [0]))) != 0)
    ra = []
    n = len(s)
    for a, b in zip(doi[:-1], doi[1:]):
        if s[a] != 0:
            # bar b (phoi nhiem ve 0) mang phi chieu RA cua lenh -> tinh vao lenh
            ra.append((a, b + 1 if b < n and s[b] == 0 else b))
    return ra


def _cp_bien_the(cp, ma, gia, kieu):
    if ma not in THAT:
        return None
    sp_pip, sl, ss = THAT[ma]
    pip = 0.01 if "JPY" in ma else 1e-4
    frac = sp_pip * pip / gia
    m = cp.bien_the(spread=frac, truot_gia=0.0)
    m.spread_frac_theo_gio = {g: x * (frac / cp.spread_frac_chung) for g, x in cp.spread_frac_theo_gio.items()} \
        if cp.spread_frac_chung > 0 else {}
    if kieu == "R1":   # swap point/dem -> ti le/nam (duong = phi)
        m = m.bien_the(phi_mua=-sl * 1e-5 / gia * 365, phi_ban=-ss * 1e-5 / gia * 365)
    else:
        m = m.bien_the(phi_mua=0.0, phi_ban=0.0)
    m.chenh_lai_suat = {}
    return m


def _mang_phi(cp, idx, n):
    from nhan import mo_phong as MP
    sp = cp.spread_mang(idx) * cp.he_so_phi_spread() + cp.truot_gia_frac
    A = cp.phi_giu_mang(idx, np.ones(n)); B = cp.phi_giu_mang(idx, -np.ones(n))
    return sp, A, B


def _loi(V, ra, sp, A, B):
    """V: (k,n) phoi nhiem da dich. Tra loi log rong (k,n) - cung cong thuc mo_phong.chay (so_hoc)."""
    doi = np.abs(np.diff(np.concatenate((np.zeros((V.shape[0], 1)), V), axis=1), axis=1))
    phi = doi * sp + np.clip(V, 0, None) * A + np.clip(-V, 0, None) * B
    return np.log(np.maximum(1.0 + V * ra - phi, 1e-12))


def do(v, kq, cp, idx, null=True, r_log=None):
    from nhan import do_luong as DO
    n = len(v); ra = np.expm1(kq.r if kq is not None else r_log)
    sp, A, B = _mang_phi(cp, idx, n)
    loi = _loi(v[None, :], ra, sp, A, B)[0]
    tho = np.log(np.maximum(1.0 + v * ra, 1e-12))
    g = _gio(v)
    lt = np.array([loi[a:b].sum() for a, b in g]) if g else np.array([])
    lg = np.array([tho[a:b].sum() for a, b in g]) if g else np.array([])
    cs = DO.chi_so(loi, idx, v)
    thang, thua = lt[lt > 0].sum(), -lt[lt < 0].sum()
    r = {"so_lenh": len(lt), "pf_lenh": round(float(thang / thua), 3) if thua > 0 else (9.99 if thang > 0 else 0),
         "pf_bar": cs.get("pf"), "tb_lenh_pct": round(float(lt.mean() * 100), 4) if len(lt) else 0,
         "tb_lenh_tho_pct": round(float(lg.mean() * 100), 4) if len(lg) else 0,
         "thang_pct": round(float((lt > 0).mean() * 100), 1) if len(lt) else 0,
         "sharpe": cs.get("sharpe"), "cagr_pct": cs.get("cagr_pct"), "dd_pct": cs.get("max_dd_pct"),
         "phoi_nhiem": cs.get("phoi_nhiem"), "so_nam": cs.get("so_nam"),
         "lai_tho_pct": round(float(tho.sum() * 100), 2), "lai_rong_pct": round(float(loi.sum() * 100), 2),
         "lech_kiem": round(float(abs(loi.sum() - np.nansum(kq.loi))), 6) if kq is not None else None}
    if len(lt) >= 5:   # tap trung: lai cua 10% lenh tot nhat / tong lai
        s = np.sort(lt)[::-1]; k = max(1, len(s) // 10)
        r["tap_trung_top10"] = round(float(s[:k].sum() / lt.sum()), 2) if lt.sum() > 0 else None
        y = np.array([idx[a].year for a, b in g]); nam = {}
        for yy, x in zip(y, lt): nam[int(yy)] = nam.get(int(yy), 0) + x
        r["nam_duong"] = f"{sum(1 for x in nam.values() if x > 0)}/{len(nam)}"
    if null and len(lt) >= 10 and r["tb_lenh_pct"] > 0:
        that = loi.sum(); rng = np.random.default_rng(12345); vuot = 0
        sh = rng.integers(1, n, N_NULL); ar = np.arange(n)
        for c in range(0, N_NULL, 50):
            S = sh[c:c + 50]
            V = v[(ar[None, :] - S[:, None]) % n]
            vuot += int((_loi(V, ra, sp, A, B).sum(axis=1) >= that).sum())
        r["p"] = round((vuot + 1) / (N_NULL + 1), 4)
    return r


def mot(gt):
    from tru import quantlab as Q
    from nhan import mau as MAU, mo_phong as MP, ngu_phap as NP
    try:
        NP.nap_vao_mau()
        ma, khung = gt["tai_san"], gt["khung"]
        ts = json.loads(gt["tham_so"] or "{}")
        _df, _tr, hold, _c, cp = Q._nap(ma, khung)
        th = MAU.sinh(gt["template"], hold, ts)
        kq = MP.chay(hold, th, cp, ma=ma, khung=khung)
        v = kq.vi_the; idx = hold.index
        out = {"ma": gt["ma"], "ts": ma, "khung": khung, "template": gt["template"], "ho": gt["ho"],
               "nguon": (gt["nguon"] or "")[:40], "hold": f"{str(idx[0])[:10]}..{str(idx[-1])[:10]}",
               "A": do(v, kq, cp, idx)}
        gia = float(hold["close"].median())
        for kieu in ("R1", "R2"):
            m = _cp_bien_the(cp, ma, gia, kieu)
            if m is not None:
                out[kieu] = do(v, None, m, idx, null=(kieu == "R2" or out["A"].get("p") is not None), r_log=kq.r)
        return out
    except Exception as e:
        return {"ma": gt["ma"], "loi": f"{type(e).__name__}: {str(e)[:150]}"}


def main():
    import sqlite3
    c = sqlite3.connect(f"file:{GOC}/nao.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
    gts = [dict(r) for r in c.execute(
        "SELECT g.*, k.verdict AS vd_repo, k.p_placebo AS p_repo FROM gia_thuyet g JOIN ket_qua k ON k.gt_ma=g.ma "
        "AND k.superseded_by IS NULL ORDER BY g.tai_san, g.khung")]
    lim = int(os.environ.get("EVO_LIM", "0"))
    if lim: gts = gts[:lim]
    t0 = time.time(); ra = []
    # nhom theo (tai_san,khung) de cache _nap trong moi tien trinh
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 6, maxtasksperchild=200) as p:
        for i, r in enumerate(p.imap(mot, gts, chunksize=8)):
            g = gts[i]; r["vd_repo"] = g["vd_repo"]; r["p_repo"] = g["p_repo"]; ra.append(r)
            if i % 100 == 0: print(i, round(time.time() - t0), flush=True)
    json.dump(ra, open(RA, "w"), ensure_ascii=False, default=str)
    print("XONG", len(ra), round(time.time() - t0))


if __name__ == "__main__":
    main()
