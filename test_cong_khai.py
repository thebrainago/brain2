# -*- coding: utf-8 -*-
"""Kiểm thử làn lịch sử công khai (seeker/cong_khai) + bộ lọc chất lượng nguồn."""
import json
from datetime import datetime
from seeker.cong_khai import cham_diem as C, mql5, nen_tang_khac as NK, chay
from seeker import chat_luong_nguon as CL

TRANG = """<html><head><title>Copy trades of the Test Grid trading signal for MetaTrader 5 - Ai</title></head><body>
<div>Growth: </div><div>120.00%</div><div>Initial Deposit:</div><div>1 000.00 USD</div>
<div>Withdrawals:</div><div>0.00 USD</div><div>Deposits:</div><div>0.00 USD</div>
<div>Latest trade:</div><div>2 days ago</div><div>Weeks:</div><div>104</div>
<div>Started:</div><div>2024.11.01 10:00:00</div><div>growth since 2024</div><div>120%</div>
<div>ICMarketsSC-Demo</div><div>1:500</div><p>EA uses a grid with martingale recovery</p>
<div>Trades:</div><div>1 234</div><div>Relative drawdown: </div><div>By Balance: </div><div>25.50% (</div>
<div>By Equity: </div><div>41.20% (</div><div>Distribution</div><div>Symbol</div><div>Deals</div><div>Sell</div><div>Buy</div>
<div>EURUSD</div><div>1000</div><div>GBPUSD</div><div>234</div><div>500</div><div>1K</div><div>1.5K</div>
<a href="/en/signals/2304847">x</a><a href="/en/signals/2394758/news">y</a></body></html>"""


def test_cagr():
    assert C.cagr_tu_tang_truong(100, 12) == 100.0
    assert abs(C.cagr_tu_tang_truong(21, 24) - 10.0) < 0.01
    assert C.cagr_tu_tang_truong(None, 12) is None and C.cagr_tu_tang_truong(50, 0) is None
    assert C.cagr_tu_tang_truong(-100, 12) == -100.0


def test_chi_hai_tieu_chi():
    assert C.dat(79.9, 10.1) == "DAT"
    assert C.dat(80.0, 50) == "KHONG_DAT" and C.dat(10, 10.0) == "KHONG_DAT"
    assert C.dat(None, 50) == "CHUA_DO" and C.dat(10, None) == "CHUA_DO"
    # điểm xếp hạng không ảnh hưởng ĐẠT: demo, tuổi ngắn vẫn ĐẠT nếu đủ 2 tiêu chí
    assert C.dat(79, 11) == "DAT"


def test_xep_hang_tuoi_va_that():
    a = {"tuoi_thang": 48, "that_demo": "that", "dd_pct": 30, "cagr_pct": 30}
    b = dict(a, that_demo="demo"); c = dict(a, tuoi_thang=6)
    assert C.diem_xep_hang(a) > C.diem_xep_hang(b) and C.diem_xep_hang(a) > C.diem_xep_hang(c)


def test_phan_tich_mql5():
    t = mql5.phan_tich(TRANG, "999", ngay_doc=datetime(2026, 11, 3))
    assert t["ten"] == "Test Grid" and t["mt"] == "MetaTrader 5"
    assert t["tang_truong_pct"] == 120.0 and t["dd_pct"] == 41.2 and t["so_lenh"] == 1234
    assert t["that_demo"] == "demo" and t["may_chu"] == "ICMarketsSC-Demo"
    assert abs(t["tuoi_thang"] - 23.92) < 0.05
    assert "grid" in t["kieu"] and "martingale" in t["kieu"]
    assert t["symbol"] == ["EURUSD", "GBPUSD"]
    assert mql5.id_tu_danh_sach(TRANG) == ["2304847"]
    assert chay.cham(t)["trang_thai"] == "DAT" and t["diem_xep_hang"] is not None


def test_litefinance_khong_co_dd_la_chua_do():
    h = '<a href="/traders/info?id=11">a</a><a href="/traders/info?id=11">a</a><div>@A</div><div>&nbsp;</div><div>599.36%</div><div>Profitability (All time)</div><div>2 </div><div>Risk</div>'
    d = NK.litefinance_danh_sach(h)
    assert len(d) == 1 and d[0]["id"] == "11" and d[0]["tang_truong_pct"] == 599.36
    assert chay.cham(d[0])["trang_thai"] == "CHUA_DO"


def test_ghi_so_va_bao_cao(tmp_path, monkeypatch):
    import nhan.so_ket_qua as S
    so = tmp_path / "kq.csv"
    monkeypatch.setattr(S, "SO", so)
    orig = S.ghi_ket_qua
    monkeypatch.setattr(S, "ghi_ket_qua", lambda d: orig(d, duong=so))
    t = chay.cham(mql5.phan_tich(TRANG, "999", ngay_doc=datetime(2026, 11, 3)))
    moi = chay.ghi_so([t], "20261103")
    assert moi and moi[0]["nguon"] == "CONG_KHAI" and moi[0]["trang_thai"] == "DAT"
    assert chay.ghi_so([t], "20261103") == []          # chạy lại cùng ngày không nhân đôi
    p = tmp_path / "bc.md"
    ds = chay.viet_bao_cao([t], {"MQL5": {"doc_duoc": 1}}, [], "2026-11-03 00:00", p)
    s = p.read_text(encoding="utf-8")
    assert len(ds) == 1 and "https://www.mql5.com/en/signals/999" in s and "chỉ để sắp thứ tự" in s


def test_chat_luong_nguon():
    assert CL.bac("mql5_signals") == "co_lich_su" and CL.bac("github_search") == "co_lich_su"
    assert CL.bac("hn_algolia") == "thao_luan" and not CL.giu("hn_algolia", {}, True) and CL.giu("hn_algolia", {}, False)
    assert CL.uu_tien("mql5_codebase", {}, 0.9) > CL.uu_tien("smartlab", {}, 0.9)
    assert CL.bac("x", {"chat_luong": "co_lich_su"}) == "co_lich_su"


def test_duong_cong_va_phong_cach():
    h = ('<script>x([1730000000,0,1732600000,10.5,1735200000,21]);window.growthChart(document.getElementById("growth_chart"),acc,res,'
         '{chart:[],table:{years:[{year:2024,yearly:0.21,months:{"10":0.1,"11":-0.02,}},],total:21}})</script>'
         '<div>Avg holding time:</div><div>3 days</div><div>Max deposit load:</div><div>62.5%</div><p>Works on H1 and H4</p>')
    dc = mql5.duong_cong(h)
    assert dc["theo_nam_pct"] == {2024: 21.0} and dc["thang_pct"] == [10.0, -2.0] and dc["thang_am_pct"] == 50.0
    assert dc["growth_mau"][-1][1] == 21.0 and dc["growth_mau"][0][0].startswith("2024")
    t = {"giu_lenh": "3 days", "tai_ky_quy_max_pct": 62.5, "kieu": ["grid"], "duong_cong": dc}
    pc = mql5.phong_cach(t, "Works on H1 and H4")
    assert pc["khung_nhac_den"] == ["H1", "H4"] and any("swing" in g for g in pc["goi_y"]) and "grid" in pc["goi_y"]


def test_url_sap_xep():
    assert mql5.url_danh_sach("mt5", 1, "") == "https://www.mql5.com/en/signals/mt5/list"
    assert mql5.url_danh_sach("mt4", 3, "orderby=weeks&dir=up") == "https://www.mql5.com/en/signals/mt4/list/page3?orderby=weeks&dir=up"
    assert "orderby=drawdown" in mql5.SAP_XEP and "orderby=weeks&dir=up" in mql5.SAP_XEP
