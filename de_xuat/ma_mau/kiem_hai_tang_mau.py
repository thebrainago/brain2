# -*- coding: utf-8 -*-
"""MAU THAM KHAO cho de xuat cong kiem dinh (de_xuat/README.md).

KHONG nap vao duong ong. Khong ai goi file nay cho toi khi chu du an duyet.
Muc dich: de Grok doc, chay thu, phan bien, roi moi quyet dinh co dua vao nhan/ hay khong.

Chi dung numpy + scipy. Moi ham la ham thuan, khong doc/ghi file.

Noi dung:
  p_gom_cum / hieu_ung_thiet_ke   p mot phia voi sai so chuan GOM CUM (thay t-test tung lenh)
  mde / so_lenh_can               cai nho nhat do duoc, so lenh can de thay mot canh
  holm / holm_hai_tang / bh       da kiem dinh: Holm theo ho m, Holm theo k ung vien, BH-FDR
  p_max_null                      p cap HO tu phan phoi null cua "o tot nhat trong luoi"
  ic_hang                         tuong quan hang giai doan 1 -> 2 (co chon loc co tac dung khong)
"""
from __future__ import annotations

import numpy as np
from scipy import stats


# ------------------------------------------------------------------ p gom cum
def _cum_ve_chi_so(cum) -> tuple[np.ndarray, int]:
    _, idx = np.unique(np.asarray(cum), return_inverse=True)
    return idx, int(idx.max()) + 1 if idx.size else 0


def p_gom_cum(r, cum) -> tuple[float, float, int]:
    """t-test mot phia (H1: trung binh > 0) voi sai so chuan gom cum (CR1).

    r   : loi tung lenh (bps)         cum : nhan cum cung do dai (vd tuan vao lenh, ngay vao lenh)
    Tra (p, t, so_cum). Do tu do = so_cum - 1.
    Khi moi cum chi co 1 lenh thi ket qua TRUNG tung so voi scipy.stats.ttest_1samp.
    """
    r = np.asarray(r, dtype=float)
    n = r.size
    idx, G = _cum_ve_chi_so(cum)
    if n < 3 or G < 2:
        return 1.0, 0.0, G
    m = r.mean()
    s = np.bincount(idx, weights=r - m, minlength=G)          # tong lech theo cum
    se = np.sqrt(G / (G - 1.0) * np.sum(s * s)) / n
    if se <= 0:
        return 1.0, 0.0, G
    t = m / se
    return float(stats.t.sf(t, G - 1)), float(t), G


def hieu_ung_thiet_ke(r, cum) -> float:
    """deff = phuong sai trung binh (gom cum) / phuong sai trung binh (coi lenh doc lap).

    deff = 1  : lenh gan nhu doc lap, t-test tung lenh dung duoc.
    deff = 2,2: n hieu dung chi con ~45% so lenh; t-test tung lenh thoi phong z len ~1,48 lan.
    """
    r = np.asarray(r, dtype=float)
    n = r.size
    idx, G = _cum_ve_chi_so(cum)
    if n < 3 or G < 2:
        return float("nan")
    m = r.mean()
    s = np.bincount(idx, weights=r - m, minlength=G)
    v_cum = G / (G - 1.0) * np.sum(s * s) / n ** 2
    v_iid = np.sum((r - m) ** 2) / (n - 1.0) / n
    return float(v_cum / v_iid) if v_iid > 0 else float("nan")


# ------------------------------------------------------------------ do luc / MDE
def mde(sd: float, n: int, alpha: float, power: float = 0.8, deff: float = 1.0) -> float:
    """Canh trung binh (cung don vi voi sd) nho nhat ma t-test mot phia nhin thay voi xac suat `power`.
    power=0,5 la "canh ngang nguong" (z_b = 0)."""
    za = stats.norm.isf(alpha)
    zb = stats.norm.isf(1.0 - power)
    return float((za + zb) * sd * np.sqrt(deff / n))


def so_lenh_can(e: float, sd: float, alpha: float, power: float = 0.8, deff: float = 1.0) -> int:
    """So lenh can de nhin thay canh e (cung don vi voi sd). Nghich dao cua mde()."""
    za = stats.norm.isf(alpha)
    zb = stats.norm.isf(1.0 - power)
    return int(np.ceil(((za + zb) * sd / e) ** 2 * deff))


# ------------------------------------------------------------------ da kiem dinh
def holm(ps, m: int | None = None) -> np.ndarray:
    """Holm step-down. `m` = kich thuoc HO (>= len(ps)); o khong kiem coi nhu p = 1.
    m=None -> m = len(ps). Tra p da hieu chinh theo thu tu dau vao."""
    ps = np.asarray(ps, dtype=float)
    k = ps.size
    m = k if m is None else int(m)
    if m < k:
        raise ValueError("m phai >= so p dem vao")
    order = np.argsort(ps)
    adj = np.empty(k)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, ps[i] * (m - rank)))
        adj[i] = run
    return adj


def holm_hai_tang(ps_gd2) -> np.ndarray:
    """Sang o GD1 (du lieu DOC LAP voi GD2) roi chi kiem k ung vien tren GD2:
    ho chi la k ung vien da duoc chuyen sang. Dieu kien: viec chon o dung DUNG GD1 va khong nhin GD2."""
    return holm(ps_gd2, m=len(ps_gd2))


def bh(ps, q: float = 0.10) -> np.ndarray:
    """Benjamini-Hochberg. Tra mang bool: o nao duoc nhan o muc FDR q."""
    ps = np.asarray(ps, dtype=float)
    k = ps.size
    if k == 0:
        return np.zeros(0, dtype=bool)
    order = np.argsort(ps)
    thr = q * (np.arange(1, k + 1) / k)
    ok = ps[order] <= thr
    out = np.zeros(k, dtype=bool)
    if ok.any():
        cut = np.max(np.nonzero(ok)[0])
        out[order[: cut + 1]] = True
    return out


# ------------------------------------------------------------------ null cap ho
def p_max_null(stat_that_max: float, stat_max_null) -> float:
    """p cap HO: xac suat "o tot nhat cua CA LUOI" tren chuoi null >= o tot nhat tren du lieu that.
    (1 + #{null >= that}) / (1 + N). Tu tinh phu thuoc giua cac o - khong can gia dinh doc lap.
    Moi chuoi null phai chay CA luoi voi cung ham sang loc, roi lay max thong ke (vd t hoac PF)."""
    nul = np.asarray(stat_max_null, dtype=float)
    return float((1 + np.sum(nul >= stat_that_max)) / (1 + nul.size))


def max_null_tu_luoi(ham_luoi, chuoi_null) -> np.ndarray:
    """ham_luoi(chuoi) -> mang thong ke cua tung o trong luoi. Tra max cua moi chuoi null."""
    return np.array([float(np.max(ham_luoi(c))) for c in chuoi_null])


# ------------------------------------------------------------------ chon loc co tac dung khong
def ic_hang(stat_gd1, stat_gd2) -> tuple[float, float]:
    """Tuong quan hang (Spearman) giua thong ke GD1 va GD2 tren cac o co du lenh o ca hai giai doan.
    ~0 : xep hang theo GD1 khong du bao gi cho GD2 -> ca ho khong co tin hieu, dung quet them o.
    > 0 co y nghia: co tin hieu cap ho dau khong o nao rieng le qua cong. Tra (rho, p)."""
    a = np.asarray(stat_gd1, dtype=float)
    b = np.asarray(stat_gd2, dtype=float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return float("nan"), 1.0
    res = stats.spearmanr(a[ok], b[ok])
    return float(res.statistic), float(res.pvalue)
