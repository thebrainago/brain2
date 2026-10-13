import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "ea_demo")
import ea_logic_v24 as E
import v19
import v22


def _du_lieu(seed, n=1500):
    rng = np.random.default_rng(seed); c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    o = np.r_[c[0], c[:-1]]                                     # khong gap: open = close truoc
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.006, n)); l = np.minimum(o, c) * (1 - rng.uniform(0, 0.006, n))
    d = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "spread_open": 0.0, "so_tick": 1}, index=pd.bdate_range("2010-01-01", periods=n))
    return d


def test_ea_khop_python():
    for seed in range(6):
        d = _du_lieu(seed)
        s, atr, _ = v19.tin_hieu(d)
        o, h, l, c = (d[k].tolist() for k in ("open", "high", "low", "close"))
        for che, ten in (("RSI", "RSI"), ("MRZ", "MRZ")):
            A, T = E.chi_bao(o, h, l, c, che)
            assert np.allclose(A[60:], atr[60:], rtol=1e-9)
            assert (np.array(T[60:]) == s[ten][60:].astype(int)).all()
            P = v22.chay(d, s[ten].astype(int), "TR2", atr, np.zeros(len(d)))
            M = E.ea(o, h, l, c, che)
            # bien cuoi du lieu: Python dung o n-2 (khong mo lenh moi); chi so lenh vao truoc n-80
            P = [p for p in P if d.index.get_loc(p[0]) < len(d) - 80]; M = [m for m in M if m[0] < len(d) - 80]
            assert len(P) == len(M) and len(P) > 5
            for p, m in zip(P, M):
                r_ea = (m[4] - m[2]) / m[2] * m[1]
                assert d.index[m[0]] == p[0] and m[1] == p[2] and abs(r_ea - p[1]) < 1e-12 and m[3] - m[0] + 1 == p[3]


def test_mrz_gio_vao_mac_dinh_02h():
    mq = open("ea_demo/BRAIN_V24_MRZ_Trail_D1.mq5", encoding="utf-8").read()
    ch = open("ea_demo/BRAIN_V24_Chung.mqh", encoding="utf-8").read()
    assert "#define GIO_VAO_MAC_DINH 2" in mq and mq.index("GIO_VAO_MAC_DINH 2") < mq.index("#include")
    assert "input int    InpGioVao        = GIO_VAO_MAC_DINH;" in ch and "#ifndef GIO_VAO_MAC_DINH" in ch
    assert "GIO_VAO_MAC_DINH" not in open("ea_demo/BRAIN_V24_RSI_Trail_D1.mq5", encoding="utf-8").read()  # RSI giu 0h nhu cu
    assert "if(ChuaToiGio()) { g_cho_tin = tin;" in ch and "if(ChuaToiGio()) return;" in ch
    assert "InpGioVao=2" in open("ea_demo/BRAIN_V24_MRZ_Trail_D1.set", encoding="utf-8").read()
