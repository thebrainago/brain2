import re
import numpy as np
import pandas as pd
import v19, v22, v24, v28


def _d(n=900, seed=3):
    r = np.random.default_rng(seed); c = 1 + np.cumsum(r.normal(0, 0.006, n)); o = np.r_[c[0], c[:-1]] + r.normal(0, 0.001, n)
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + 0.003, "low": np.minimum(o, c) - 0.003, "close": c,
                         "spread_open": 0.0, "so_tick": 1}, index=pd.bdate_range("2008-01-01", periods=n))


def test_loc_khong_nhin_truoc():
    d = _d(); s = np.where(np.arange(len(d)) % 5 == 0, 1, np.where(np.arange(len(d)) % 7 == 0, -1, 0))
    for k in ("KHONG", "CHE_DO", "W1_EMA20"):
        for cat in (523, 600, 777):
            a = v28.loc(d, s, k)[:500]; b = v28.loc(d.iloc[:cat], s[:cat], k)[:500]
            assert (a == b).all(), (k, cat)


def test_tin_hieu_mrz_chi_dung_qua_khu():
    d = _d(); a = v19.tin_hieu(d)[0]["MRZ"][:500]; b = v19.tin_hieu(d.iloc[:510])[0]["MRZ"][:500]
    assert (a == b).all()


def test_w1_chi_tuan_da_dong():
    d = _d(); t = v28.xu_huong_w1(d)
    # doi gia tuan tuong lai (sau ngay 400) khong anh huong ngay <= 400
    d2 = d.copy(); d2.iloc[401:, d2.columns.get_loc("close")] *= 3
    assert (v28.xu_huong_w1(d2)[:401] == t[:401]).all()


def test_chay_tr2_khop_v22():
    for seed in range(4):
        d = _d(seed=seed); s, atr, _ = v19.tin_hieu(d); sp = d["close"].to_numpy() * 2e-4
        a = v28.chay(d, s["MRZ"].astype(int), atr, sp); b = v22.chay(d, s["MRZ"].astype(int), "TR2", atr, sp)
        assert a == b and len(a) > 0


def test_gio5_giu_toi_da_5():
    d = _d(); s, atr, _ = v19.tin_hieu(d)
    L = v28.chay(d, s["MRZ"].astype(int), atr, np.zeros(len(d)), **v28.THOAT["GIO5"])
    assert L and max(x[3] for x in L) <= 6


def test_so_o_dang_ky_khop():
    txt = open("reports/vong28_tien_dang_ky.md", encoding="utf-8").read()
    hang = [l for l in txt.splitlines() if re.match(r"^\| (\d+) \| P1-", l)]
    assert len(hang) == v28.SO_O_DANG_KY == 11
    fake = {t: _d(seed=i) for i, t in enumerate(set(v28.POOL4) | set(v28.v26.FX7))}
    O, TC = v28.o_list(fake); assert len(O) == 11 and [o["so"] for o in O] == list(range(1, 12))


def test_chay_o_smoke():
    d = _d(n=3000, seed=9); d.index = pd.bdate_range("2004-01-01", periods=len(d))
    r = v28.chay_o({"so": 1, "viec": "t", "nhom": "x", "loc": "KHONG", "thoat": "TR2", "B": {"AUDCAD_X": d}, "tach": pd.Timestamp("2015-04-01")})
    assert "truoc" in r or r.get("dung_tang") == 0
    assert "B" not in r
