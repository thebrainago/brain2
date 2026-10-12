# -*- coding: utf-8 -*-
"""Vong 10: quy tac mua vu - phoi nhiem dung lich, phi tinh dung."""
import numpy as np
import pandas as pd

import mua_vu as MV


def _gia():
    idx = pd.bdate_range("2019-01-01", "2021-12-31")
    return pd.Series(np.linspace(100, 130, len(idx)), index=idx)


def test_nam3_va_halloween():
    g = _gia()
    e = MV.phoi_nhiem("CHU_KY_BAU_CU_NAM3", g)
    assert e[g.index.year == 2019].all() and not e[g.index.year == 2020].any()
    h = MV.phoi_nhiem("HALLOWEEN", g)
    assert h[g.index.month == 5].sum() == 0 and h[g.index.month == 11].all()


def test_dau_cuoi_thang_4_phien_moi_thang():
    g = _gia()
    e = MV.phoi_nhiem("DAU_CUOI_THANG", g)
    m = (g.index.year == 2020) & (g.index.month == 6)
    assert e[m].sum() == 4


def test_tet_20_phien_truoc_mung_1():
    g = _gia()
    e = MV.phoi_nhiem("VANG_TRUOC_TET", g)
    tet = pd.Timestamp("2020-01-25")
    truoc = g.index[g.index < tet][-20:]
    assert e[g.index.isin(truoc)].all() and e[(g.index >= tet) & (g.index < "2020-03-01")].sum() == 0


def test_phi_spread_mot_lan_khu_hoi(monkeypatch):
    idx = pd.bdate_range("2020-01-06", periods=10)
    g = pd.Series(100.0, index=idx)
    monkeypatch.setattr(MV, "lai_suat", lambda i: np.zeros(len(i)))
    monkeypatch.setattr(MV, "MARKUP_QUA_DEM", 0.0)
    e = np.zeros(10); e[3:6] = 1
    L = MV.chay(g, e, 2e-4)
    assert abs(-L.sum() - (2e-4 + 2 * MV.TRUOT)) < 1e-12
