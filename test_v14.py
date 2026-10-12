# -*- coding: utf-8 -*-
import datetime as dt
import numpy as np
import pandas as pd
import lich_su_kien as LS
import v14


def test_nfp_thu_sau_dau_thang():
    n = LS.nfp(2024, 2024)
    assert len(n) == 12 and all(d.weekday() == 4 and d.day <= 7 for d in n)


def test_dac_trung_vi_tri():
    idx = pd.bdate_range("2024-01-01", "2024-02-29"); F = v14.dac_trung(idx)
    assert idx[F["dau1"]][0] == pd.Timestamp("2024-01-01") and idx[F["cuoi1"]][0] == pd.Timestamp("2024-01-31")


def test_tin_hieu_cheo_khong_nhin_truoc():
    # A tang dung ngay B mo lenh -> khong duoc dung; chi loi A cua ngay <= ngay mo - 1
    idx = pd.bdate_range("2024-01-01", periods=6)
    rA = pd.Series([np.nan, 0.01, -0.01, 0.01, -0.01, 0.01], index=idx)
    mo = idx[:-1] - pd.Timedelta(days=1)
    sig = np.r_[np.nan, rA.reindex(rA.index.union(mo)).ffill().reindex(mo).to_numpy()]
    # B giu ngay idx[2] (mo o dong idx[1]) -> dung loi A ngay idx[0] (nan), khong phai idx[1]
    assert np.isnan(sig[2]) and sig[3] == 0.01
