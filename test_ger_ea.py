# -*- coding: utf-8 -*-
"""Test cat cho nhan/ger_ea.py (dong co GerEA: keo SL, luoi, TP ca ro, stop-out, dao chieu)."""
import numpy as np
import pandas as pd

from nhan import chi_phi as CP
from nhan import ger_ea as G

D = 1e-5


def _df(gia):
    """Moi bar: o=h=l=c (duong gia biet truoc) tru khi truyen tuple (o,h,l,c)."""
    rows = [g if isinstance(g, tuple) else (g, g, g, g) for g in gia]
    idx = pd.date_range("2025-01-06 10:00", periods=len(rows), freq="5min")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)


def _tin(n, j, huong, sl, tp=0.0):
    t = {"huong": np.zeros(n, dtype=int), "sl": np.zeros(n), "tp": np.zeros(n)}
    t["huong"][j], t["sl"][j], t["tp"][j] = huong, sl, tp
    return t


CP0 = CP.MoHinhChiPhi(ma="EURUSD")          # khong phi: so kiem tay duoc


def test_keo_sl_dong_lai():
    # mua 1.1000, d = 100 diem (sl 1.0990), keo 50%: gia len 1.1020 -> sl = 1.1015, ve 1.1010 -> dong 1.1015
    df = _df([1.1000, (1.1000, 1.1020, 1.1000, 1.1020), (1.1020, 1.1020, 1.1010, 1.1010)])
    ts = G.ThamSoGer(risk=0.01, grid=False, trail=True, trail_level=0.5)
    kq = G.chay(df, _tin(3, 0, 1, 1.0990), ts, CP0, "EURUSD", D, G.TaiKhoan())
    assert len(kq.ro) == 1 and kq.ro[0]["dong"] == ["sl"]
    lot = 1.0                                   # 10000*1% / (0.0010*100000)
    assert abs(kq.von_cuoi - (10000 + lot * 100000 * 0.0015)) < 1e-6


def test_luoi_them_tang_va_tp_ca_ro():
    # mua 1.1000 d=100 diem; gia xuong 1.0990 (n=1 -> lvl = pin - d) -> them 1 lot (mult 1);
    # TP ro = gia ma tong lai = loss1 = 1 lot * d -> (0.0010 + 1.1000 + 1.0990)/2 = 1.1000
    df = _df([1.1000, (1.1000, 1.1000, 1.0990, 1.0990), (1.0990, 1.1001, 1.0990, 1.1001)])
    ts = G.ThamSoGer(risk=0.01, grid=True, grid_vol_mult=1.0, grid_max_lvl=5, trail=False)
    kq = G.chay(df, _tin(3, 0, 1, 1.0990), ts, CP0, "EURUSD", D, G.TaiKhoan())
    assert kq.so_lenh == 2 and kq.tang_max == 2
    assert kq.ro[0]["dong"] == ["tp", "tp"]
    assert abs(kq.von_cuoi - (10000 + 100000 * 0.0010)) < 1e-6       # lai = loss1 = 100 USD


def test_grid_bat_isl_va_khong_sl():
    # Grid=true -> isl=true du IgnoreSL=false: gia xuong qua sl goc khong dong lenh
    df = _df([1.1000, (1.1000, 1.1000, 1.0985, 1.0985)])
    ts = G.ThamSoGer(risk=0.01, ignore_sl=False, grid=True, grid_max_lvl=1, trail=False)
    kq = G.chay(df, _tin(2, 0, 1, 1.0990), ts, CP0, "EURUSD", D, G.TaiKhoan())
    assert not kq.ro and kq.so_lenh == 1                              # van mo, khong cat lo


def test_stop_out_dong_lenh_lo():
    df = _df([1.1000, (1.1000, 1.1000, 1.0000, 1.0000)])
    ts = G.ThamSoGer(risk=0.5, grid=False, trail=False)               # 50 lot/1 lot... lo lon
    kq = G.chay(df, _tin(2, 0, 1, 1.0990), ts, CP0, "EURUSD", D,
                G.TaiKhoan(von=10000, don_bay=1000, stop_out=0.5, lot_max=100))
    assert kq.so_stop_out >= 1 and kq.ro and kq.ro[0]["dong"] == ["stop_out"]


def test_dao_chieu_reverse():
    # BuySignal + reverse -> BAN o BID, khoi luong theo |Bid - tp_goc|
    df = _df([1.1000, (1.1000, 1.1000, 1.0980, 1.0980)])
    ts = G.ThamSoGer(risk=0.01, grid=False, trail=False, ignore_tp=False, reverse=True)
    kq = G.chay(df, _tin(2, 0, 1, 1.0990, 1.1020), ts, CP0, "EURUSD", D, G.TaiKhoan())
    # ban; sl cua lenh ban = tp goc 1.1020 (IgnoreTP=false), tp = sl goc bi bo (isl=itp goc... )
    assert kq.so_lenh == 1 and kq.von_cuoi > 10000                    # gia xuong -> ban lai


def test_tham_so_tu_oninit_bo_gan_trong_if():
    vb = """input double Risk = 2.0;
input double GridTrailingStopLevel = 40;
input ENUM_RISK RiskMode = RISK_DEFAULT;
int OnInit() {
    ea.risk = Risk * 0.01;
    ea.grid = Grid;
    if (RiskMode == RISK_FIXED_VOL || RiskMode == RISK_MIN_AMOUNT) ea.risk = Risk;
    return INIT_SUCCEEDED;
}
void OnTimer() { if (Trail) ea.CheckForTrail(); }
"""
    th = G.doc_input(vb)
    th["Grid"] = "true"
    ts, _ = G.tham_so_tu_ma(vb, th)
    assert abs(ts.risk - 0.02) < 1e-12
    assert ts.grid_trail_level == 0.0          # thanh vien khong gan -> mac dinh constructor


def test_set_khop_ten_chinh_xac():
    th, bo = G.gop_tham_so("input int SLLookback = 7;\ninput double Risk = 1;\n",
                           "SLLookBack=9\nRisk=2.5\n")
    assert th["SLLookback"] == "7" and th["Risk"] == "2.5" and bo == ["SLLookBack"]


def test_3macd_ban_la_mua_doi_dau():
    from nhan import ger_ea_tin_hieu as T
    rng = np.random.default_rng(1)
    c = 1.1 + np.cumsum(rng.normal(0, 1e-4, 3000))
    M1, M2, M3 = (T.macd_main(c, a, b) for a, b in ((5, 8), (13, 21), (34, 144)))
    so = 0
    for j in range(200, 3000):
        b = T._3macd_mot_chieu(M1, M2, M3, j, 32, 1)
        s = T._3macd_mot_chieu(-M1, -M2, -M3, j, 32, -1)
        assert b == s
        so += b
    assert so > 0


def test_rsi_mt5_hang_so():
    from nhan import ger_ea_tin_hieu as T
    c = np.array([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    r = T.rsi(c, 3)
    assert np.isnan(r[2]) and r[3] == 100.0 and r[-1] == 100.0
