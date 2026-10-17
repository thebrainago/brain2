import sys
sys.path.insert(0, "mt5tools")
import chay_lai_tren_san as C  # noqa: E402
import do_phi_san as D  # noqa: E402


def test_ten_goc_nhan_ra_ten_cua_ca_hai_san():
    cap = {"EURUSDc": "EURUSD", "XAUUSDc": "XAUUSD", "EURUSDm": "EURUSD", "USTECm": "US100", "US500m": "US500",
           "DE30m": "GER40", "EURUSDmicro": "EURUSD", "GOLD.i#": "XAUUSD", "US500Cash#": "US500", "GER40Cash": "GER40",
           "OILCash#": "USOIL", "GBPJPY#": "GBPJPY", "USDCHF": "USDCHF", "AUDCAD": "AUDCAD"}
    for s, g in cap.items():
        assert D.ten_goc(s) == g, s
    for s in ("AAPL", "Tesla", "BTCETH", "#AMZN"):
        assert D.ten_goc(s) is None, s


def test_swap_ra_tien_moi_dem():
    # POINTS: -5 diem EURUSD (point 1e-5), tick_value 1 USD / tick 1e-5 / lot -> 0,01 lot = -0,05 USD
    assert abs(D.swap_tien_dem(1, -5.0, 0.01, 1e-5, 1.0, 1e-5, 1.1) + 0.05) < 1e-12
    assert D.swap_tien_dem(0, -5.0, 0.01, 1e-5, 1.0, 1e-5, 1.1) == 0.0
    assert abs(D.swap_tien_dem(4, -3.0, 0.1, 0.01, 0.01, 0.01, 5000) + 0.3) < 1e-12
    # lai suat -2,5 %/nam tren US500 gia 5000, 1 diem = 1 USD/lot -> 0,1 lot ~ -0,0347 USD/dem
    assert abs(D.swap_tien_dem(5, -2.5, 0.1, 0.01, 0.01, 0.01, 5000) + 5000 * 0.1 * 0.025 / 360) < 1e-9
    assert D.swap_tien_dem(9, -1.0, 0.01, 1e-5, 1.0, 1e-5, 1.1) is None    # mode la: KHONG doan


def test_spread_gio_va_gian_doi_ngay():
    gio = [10] * 100 + [0] * 100
    sp = [0.0001] * 100 + [0.0001] * 80 + [0.0010] * 20
    b = D.spread_theo_gio(gio, sp)
    assert b[10][0] == 100 and abs(b[10][1] - 0.0001) < 1e-12
    assert b[0][2] > 0.0005                         # p90 gio 0 bat duoc doan gian
    assert D.gian_doi_ngay(b) >= 5


def test_gap_cuoi_tuan():
    h = 3600
    t = [0, h, 2 * h, 2 * h + 50 * h, 2 * h + 51 * h]
    assert D.gap_cuoi_tuan(t, [1, 1, 1, 1.5, 1.5], [1, 1, 1.2, 1.5, 1.5]) == [abs(1.5 - 1.2)]


def test_tom_tat_lich_su_lenh_dca_dong_tp():
    dl = [  # vi the 7: mua 2 lan (DCA) roi dong bang TP; vi the 8: ban dong tay tren dien thoai, lo
        dict(time=0, type=0, entry=0, volume=0.01, price=1.0, commission=-0.03, swap=0, fee=0, profit=0, symbol="EURUSDc", position_id=7, reason=1),
        dict(time=3600, type=0, entry=0, volume=0.02, price=0.99, commission=-0.06, swap=0, fee=0, profit=0, symbol="EURUSDc", position_id=7, reason=1),
        dict(time=7200, type=1, entry=1, volume=0.03, price=1.0, commission=-0.09, swap=-0.1, fee=0, profit=2.0, symbol="EURUSDc", position_id=7, reason=5),
        dict(time=0, type=1, entry=0, volume=0.01, price=1.0, commission=0, swap=0, fee=0, profit=0, symbol="EURUSDc", position_id=8, reason=1),
        dict(time=36000, type=0, entry=1, volume=0.01, price=1.01, commission=0, swap=0, fee=0, profit=-1.0, symbol="EURUSDc", position_id=8, reason=1),
        dict(time=5, type=2, entry=0, volume=0, price=0, commission=0, swap=0, fee=0, profit=100, symbol="", position_id=0, reason=0),
    ]
    tom, lenh = D.tom_tat_lich_su(dl)
    v7 = [x for x in lenh if x["vi_the"] == 7][0]
    assert v7["so_lan_vao"] == 2 and abs(v7["lot"] - 0.03) < 1e-12 and v7["ly_do_dong"] == "TP" and v7["gio_giu"] == 2.0
    assert abs(v7["rong"] - (2.0 - 0.1 - 0.18)) < 1e-9
    t = tom[0]
    assert t["so_vi_the"] == 2 and t["ti_le_dong_loi"] == 0.5
    assert abs(t["hoa_hong_moi_lot_chieu"] - (-0.18 / 0.04 / 2)) < 1e-9


def _r(ea, ma, pha, net, pf, lenh=40, **ts):
    return {"ea": ea, "ma": ma, "tf": "D1", "pha": pha, "net": net, "pf": pf, "lenh": lenh, "dd": "1 (0.1%)", "ts": ts}


def test_chon_cau_hinh_lay_nua_kem_va_bo_trung():
    sc = [_r("MRZ", "GBPUSD#", "IS", 100, 1.5, InpTrATR=2.0), _r("MRZ", "GBPUSD#", "OOS", 50, 3.0, InpTrATR=2.0),
          _r("MRZ", "GBPUSD#", "IS", 100, 1.5, InpTrATR=2.5), _r("MRZ", "GBPUSD#", "OOS", 50, 3.0, InpTrATR=2.5),   # ket qua y het -> bo
          _r("MRZ", "GBPUSD#", "IS", 80, 1.8, InpTrATR=3.0), _r("MRZ", "GBPUSD#", "OOS", 40, 1.7, InpTrATR=3.0),
          _r("RSI", "US500Cash#", "IS", -5, 0.9, InpTrATR=2.0)]
    ch = C.chon_cau_hinh(sc, top=5)
    assert [c["ts"]["InpTrATR"] for c in ch] == [3.0, 2.0]          # min(1,8;1,7)=1,7 > min(1,5;3,0)=1,5
    assert all(c["goc"] == "GBPUSD" for c in ch)
    viec, thieu = C.viec_tren_san(ch + [{"ea": "MRZ", "goc": "GER40", "tf": "D1", "ts": {}}],
                                  {"ma": {"GBPUSD": {"symbol": "GBPUSDc", "lot_min": 0.01}}})
    assert [v["ma"] for v in viec] == ["GBPUSDc", "GBPUSDc"] and thieu == ["GER40"]


def test_doc_deals_va_ghep_duong_von():
    def hang(tg, d, lai):
        return "<tr>" + "".join("<td>%s</td>" % x for x in [tg, "2", "GBPUSDc", "sell", d, "0.01", "1.2", "3", "-0.10", "-0.20", lai, "0", ""]) + "</tr>"
    t = "<b>Deals</b>" + "".join([hang("2016.01.05 02:00:00", "in", "0.00"), hang("2016.01.09 02:00:00", "out", "5.30"),
                                         hang("2016.02.09 02:00:00", "out", "-3.00")])
    t = t.replace("<b>Deals</b>", "<th>Deals</th>")
    d = C.doc_deals(t)
    assert d == [["2016.01.09 02:00:00", 5.0], ["2016.02.09 02:00:00", -3.3]]
    k = C.tong_ket_duong_von(d, 1000, 1.0)
    assert k["lenh"] == 2 and abs(k["net"] - 1.7) < 1e-9 and k["thang_te_nhat"] == -3.3 and k["thang_am"] == 1
    assert abs(k["sut_giam_pct"] - 100 * 3.3 / 1005) < 1e-3
    sc = [{"ea": "MRZ", "goc": "GBPUSD", "ma": "GBPUSDc", "tf": "D1", "ts": {"a": 1}, "pha": "TOAN", "lot": 0.01, "deals": d, "pf": 1.5,
           "tien_moi_gia_1lot": 100000.0},
          {"ea": "RSI", "goc": "GBPUSD", "ma": "GBPUSDc", "tf": "D1", "ts": {"b": 1}, "pha": "TOAN", "lot": 0.01, "deals": [["2016.03.01 00:00:00", 4.0]]},
          {"ea": "RSI", "goc": "EURGBP", "ma": "EURGBPc", "tf": "D1", "ts": {"b": 1}, "pha": "TOAN", "lot": 0.01, "deals": [["2016.03.01 00:00:00", -9.0]]},
          {"ea": "RSI", "goc": "EURJPY", "ma": "EURJPYc", "tf": "D1", "ts": {}, "pha": "TOAN", "lot": 0.01, "loi": "khong_bao_cao"}]
    g = C.ghep(sc, 1000, 80)
    assert g["manh_trong_bo"] == 2 and abs(g["bo_ghep"]["net"] - 5.7) < 1e-9     # manh lo (EURGBP) khong vao bo
    assert len(g["tung_manh"]) == 3                                               # lan hong khong tinh, khong mat
    m = [x for x in g["tung_manh"] if x["ea"] == "MRZ"][0]
    assert abs(m["chiu_them_gia_moi_lenh"] - 1.7 / 2 / (100000 * 0.01)) < 1e-9   # 0,00085 = 8,5 pip moi lenh
    assert {x["manh"] for x in g["dong_gop"]} == {"MRZ GBPUSD", "RSI GBPUSD"}
    # MRZ: 1,7 / 1000 / 10,75 nam = 0,016 %/nam, DD 0,33 % -> ~3,8 %/nam o DD 80 % -> chua dat; RSI GBPUSD khong sut -> dat;
    # EURGBP lo -> khong dat. Ca bo: 5,7 -> ~13 %/nam o DD 80 % -> DAT (ghep lam tot hon tung manh).
    assert g["manh_dat_cot_loi"] == 1 and g["bo_ghep"]["dat_cot_loi"] is True
    assert 10 <= g["bo_ghep"]["lai_pct_nam_o_dd_muc_tieu"] <= 16
