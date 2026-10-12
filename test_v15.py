# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import lich_su_kien as LS
import v15


def test_cpi_moi_thang_mot_ngay():
    c = LS.cpi(); assert len({(d.year, d.month) for d in c}) == len(c) and len(c) > 350


def test_vuot_mua_giu_bang_0_khi_phoi_nhiem_toan_bo():
    idx = pd.bdate_range("2000-01-01", periods=800); g = pd.Series(np.cumprod(1 + np.random.default_rng(1).normal(3e-4, 1e-2, 800)), index=idx)
    f = lambda e, hs: e * g.pct_change().fillna(0).to_numpy()
    assert abs(v15.vuot([(1.0, g, np.ones(800), f)], 1.0)) < 1e-9


def test_dich_vong_giu_so_ngay():
    idx = pd.bdate_range("2000-01-01", periods=600); g = pd.Series(1.0, index=idx); e = (np.arange(600) % 7 == 0).astype(float)
    cs = [(1.0, g, e, lambda e, hs: e)]
    assert v15.chuoi(cs, 1.0, 37).sum() == e.sum()
