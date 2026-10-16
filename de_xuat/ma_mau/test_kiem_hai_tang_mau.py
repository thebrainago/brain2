# -*- coding: utf-8 -*-
"""Test cho de_xuat/ma_mau/kiem_hai_tang_mau.py. Chay: python -m pytest de_xuat/ma_mau -q (< 5 giay)."""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_hai_tang_mau as K  # noqa: E402


def test_p_gom_cum_trung_ttest_khi_moi_cum_mot_lenh():
    rng = np.random.default_rng(1)
    r = rng.normal(2.0, 100.0, 200)
    p, t, G = K.p_gom_cum(r, np.arange(200))
    ref = stats.ttest_1samp(r, 0, alternative="greater")
    assert G == 200
    assert abs(t - ref.statistic) < 1e-9
    assert abs(p - ref.pvalue) < 1e-9


def test_hieu_ung_thiet_ke_iid_gan_1_va_cum_lon_hon_1():
    rng = np.random.default_rng(2)
    cum = np.repeat(np.arange(400), 5)                      # 400 tuan x 5 lenh
    iid = rng.normal(0, 100, cum.size)
    cluster = np.repeat(rng.normal(0, 100, 400), 5) * 0.7 + rng.normal(0, 100, cum.size) * 0.7
    assert 0.8 < K.hieu_ung_thiet_ke(iid, cum) < 1.25
    assert K.hieu_ung_thiet_ke(cluster, cum) > 2.0


def test_p_gom_cum_khong_nho_hon_ttest_khi_co_cum_duong():
    rng = np.random.default_rng(3)
    cum = np.repeat(np.arange(40), 5)
    r = np.repeat(rng.normal(0, 100, 40), 5) + rng.normal(0, 50, cum.size) + 8.0
    p_cum, _, _ = K.p_gom_cum(r, cum)
    p_iid = stats.ttest_1samp(r, 0, alternative="greater").pvalue
    assert p_cum >= p_iid                                    # gom cum khong BAO GIO lac quan hon khi cum cung dau


def test_holm_khop_gia_tri_tay():
    adj = K.holm([0.001, 0.01, 0.04], m=3)
    assert np.allclose(adj, [0.003, 0.02, 0.04])
    adj_ho = K.holm([0.001, 0.01, 0.04], m=1000)             # ho lon -> ap he so (m - rank)
    assert np.allclose(adj_ho, [1.0, 1.0, 1.0])


def test_hai_tang_nhe_hon_ho_lon():
    ps = [0.0004, 0.003, 0.2]
    assert (K.holm_hai_tang(ps) <= K.holm(ps, m=20503)).all()
    assert K.holm_hai_tang(ps)[0] < 0.05 <= K.holm(ps, m=20503)[0]


def test_bh_va_mde_so_lenh_can():
    assert K.bh([0.001, 0.009, 0.2, 0.9], q=0.10).tolist() == [True, True, False, False]
    # khop bang trong de_xuat/01: canh 5 bps, sd 100, alpha 0,05, power 50% -> ~1.082 lenh
    assert abs(K.so_lenh_can(5, 100, 0.05, power=0.5) - 1082) <= 2
    assert abs(K.mde(100, 150, 0.05, power=0.5) - 13.4) < 0.1
    assert K.mde(100, 150, 0.05, power=0.8) > K.mde(100, 150, 0.05, power=0.5)


def test_p_max_null_va_ic_hang():
    nul = np.arange(100.0)
    assert abs(K.p_max_null(1000.0, nul) - 1 / 101) < 1e-12
    assert K.p_max_null(-1.0, nul) == 1.0
    rng = np.random.default_rng(4)
    a = rng.normal(size=500)
    rho_tin_hieu, _ = K.ic_hang(a, a + rng.normal(size=500))
    rho_nhieu, p_nhieu = K.ic_hang(a, rng.normal(size=500))
    assert rho_tin_hieu > 0.5 and abs(rho_nhieu) < 0.2 and p_nhieu > 0.001
