import sys
sys.path.insert(0, "mt5tools")
import chay_xu_li_lenh as X  # noqa: E402


def test_kich_ban_va_gan_ma():
    kb = X.kich_ban()
    # 3 ma co tin hieu x 5 cach xu li + 3 ma khong tin hieu x 4 (bo "chi_tp_trail") = 27, ten khong trung
    assert len(kb) == 27 and len({k["ten"] for k in kb}) == 27
    ms = {"ma": {"GBPUSD": {"symbol": "GBPUSDc", "lot_min": 0.01}, "US500": {"symbol": "US500m", "lot_min": 0.1}}}
    g, thieu = X.gan_ma(kb, ms)
    assert {k["ma"] for k in g} == {"GBPUSDc", "US500m"} and "XAUUSD" in thieu
    assert all(k["lot"] == 0.1 for k in g if k["ma"] == "US500m")


def test_file_set_co_lot_va_tham_so():
    k = [x for x in X.gan_ma(X.kich_ban(), None)[0] if x["ten"] == "GBPUSD_D1_dca5_hedge"][0]
    s = X.file_set(k)
    assert "InpHedgeKhiLoPct=5.0" in s and "InpNhoi=1" in s and "InpLot0=0.01" in s and "InpVao=1" in s


def test_cot_loi_dung_dd_von_mt5():
    # 10,75 nam, +1075 tren 10.000 = 1 %/nam; DD von 4 % -> lot x20 -> 20 %/nam o DD 80 % -> DAT
    c = X.cot_loi({"net": 1075.0, "dd": "412.3 (4.00%)"}, 10000)
    assert abs(c["lai_pct_nam"] - 1.0) < 1e-9 and c["he_so_lot"] == 20.0 and c["dat"]
    assert not X.cot_loi({"net": 50.0, "dd": "900 (9.00%)"}, 10000)["dat"]     # 0,05 %/nam / 9 % -> 0,4 %/nam
    assert not X.cot_loi({"net": -10.0, "dd": "10 (0.10%)"}, 10000)["dat"]


def test_bang_xep_va_bao_chua_do():
    so = [{"ten": "A", "ma": "X", "net": 1075.0, "dd": "1 (4.00%)", "lenh": 10, "pf": 1.5},
          {"ten": "B", "ma": "X", "loi": "khong_bao_cao"}]
    t = X.bang(so, 10000)
    assert "| A | X | 1.00 | 4.0 | 20.0 | 10 | 1.5 | DAT |" in t and "CHUA_DO_DUOC" in t and "B" in t
