import numpy as np
import pandas as pd
import v27
from nhan import tien_xu_ly_ea as TX


def _d(n=900, seed=2):
    r = np.random.default_rng(seed); c = 1 + np.cumsum(r.normal(0, 0.005, n)); o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + 0.002, "low": np.minimum(o, c) - 0.002, "close": c,
                         "spread_open": 0.0, "so_tick": 1}, index=pd.bdate_range("2010-01-01", periods=n))


def test_loc_khong_nhin_truoc():
    d = _d(); s = np.where(np.arange(len(d)) % 7 == 0, 1, np.where(np.arange(len(d)) % 11 == 0, -1, 0))
    for k in ("EMA_DONG", "EMA_NGUOC", "RSI_CAN"):
        a = v27.loc(d, s, k)[:500]; b = v27.loc(d.iloc[:600], s[:600], k)[:500]
        assert (a == b).all()


def test_ema_dong_nguoc_ro_rang():
    d = _d(); s = np.ones(len(d), int)
    assert ((v27.loc(d, s, "EMA_DONG") != 0) & (v27.loc(d, s, "EMA_NGUOC") != 0)).sum() == 0


def test_tx_kiem_ky_quy_va_bool():
    vb = "bool CheckMargin(double l){return true;}\nvoid Open(bool b){ if(b) trade.Buy(1); else trade.Sell(1);}\nvoid OnTick(){ if(CheckMargin(0.1)) Open(x>1); }"
    m, log = TX.bien_doi(vb)
    assert "if(true)" in m and "Open__0()" in m and "Open__1()" in m and any("du ky quy" in z for z in log)


def test_tx_khong_chuyen_biet_ham_chi_bao():
    vb = "double GetRSI(int s){return iRSI(NULL,0,14,0,s);}\nvoid OnTick(){ if(GetRSI(1)>70) trade.Sell(1); }"
    m, _ = TX.bien_doi(vb); assert "GetRSI(1)" in m


def test_tx_ontimer():
    vb = "int OnInit(){EventSetTimer(60);return 0;}\nvoid OnTimer(){ if(a>b) trade.Buy(1); }"
    m, log = TX.bien_doi(vb); assert "void OnTick(" in m and any("OnTimer" in z for z in log)


def test_dem_tin_hieu():
    d = _d(); assert v27.tin_hieu(d) is v27.tin_hieu(d)
