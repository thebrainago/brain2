# -*- coding: utf-8 -*-
"""Bộ đọc CSV tín hiệu MQL5 (dạng vị thế + dạng deal In/Out) và mô phỏng lưới dịch ngược."""
import re
from pathlib import Path
import numpy as np
import pandas as pd
from nhan.dich_nguoc import doc_lich_su as DL, backtest_luoi as BL

VI_THE = """\ufeffTime;Type;Volume;Symbol;Price;S/L;T/P;Time;Price;Commission;Swap;Profit;Comment
2026.10.29 15:29:58;Sell Stop;5.15;AUDUSD.i;0.70198;0.70396;0.69198;2026.10.29 15:31:02;0.70331;;;;cancelled
2026.10.30 13:44:27;Buy;0.02;GBPUSD;1.34252;;1.34602;2026.10.30 17:00:41;1.33778;;;-9.48;
2026.10.30 12:17:08;Sell;0.04;GBPUSD;1.34229;;;2026.10.30 17:00:42;1.33798;;;17.24;
2016.10.07 10:39:17;Balance;;EURUSD;;;;;;;;5 000.00;Deposit
"""
DEAL = """\ufeffTime;Symbol;Type;Direction;Volume;Price;Commission;Swap;Profit;Comment
2026.10.30 12:02:16;AUDCAD;Sell;Out;0.03;0.98194;;;3.00;
2026.10.30 10:50:07;AUDCAD;Buy;In;0.01;0.98093;;;0.00;
2026.10.30 06:34:02;AUDCAD;Buy;In;0.02;0.98368;-0.10;;0.00;
2026.06.24 01:28:41;;Balance;;;;;;-100.00;
2026.01.01 01:00:00;;Balance;;;;;;1 000.00;
"""


def test_vi_the_bo_lenh_cho():
    df = DL.doc(VI_THE)
    assert len(df) == 2 and set(df.chieu) == {"buy", "sell"} and abs(df.loi_nhuan.sum() - 7.76) < 1e-9


def test_deal_ghep_fifo(tmp_path):
    df = DL.doc(DEAL)
    assert len(df) == 2 and (df.chieu == "buy").all()
    assert abs(df.loi_nhuan.sum() - 2.9) < 1e-9 and df.lot.tolist() == [0.02, 0.01]
    p = tmp_path / "x.csv"; p.write_text(DEAL, encoding="utf-8")
    v = DL.doc_von(str(p)); assert sorted(v.so_tien.tolist()) == [-100.0, 1000.0]


def test_von_dang_vi_the(tmp_path):
    p = tmp_path / "y.csv"; p.write_text(VI_THE, encoding="utf-8")
    assert DL.doc_von(str(p)).so_tien.tolist() == [5000.0]


def test_mo_phong_luoi_dao_dong_co_lai():
    t = np.arange(2000); c = 1.0 + 0.0040 * np.sin(t / 15)
    g = pd.DataFrame({"open": np.r_[c[0], c[:-1]], "close": c}, index=pd.date_range("2020", periods=2000, freq="h"))
    g["high"] = g[["open", "close"]].max(axis=1); g["low"] = g[["open", "close"]].min(axis=1)
    for kieu in ("luoi_tp", "ro_dca"):
        k = BL.chay(g, kieu, 1e-4, 10, 10, 1.0, 10.0, lot_moi_1000=0.001)
        assert not k["chay_tai_khoan"] and k["equity_cuoi"] > 1000


def test_ea_nhap_va_set():
    D = Path(__file__).parent / "ea_demo"
    for ten in ("BRAIN_DN_LuoiHedgeTP", "BRAIN_DN_RoDCAHedge"):
        src = (D / f"{ten}.mq5").read_text()
        assert "OnTimer" in src and "OnTradeTransaction" in src and "DEAL_SWAP" in src
        assert src.count("{") == src.count("}") and src.count("(") == src.count(")")
        ins = set(re.findall(r"^input\s+\w+\s+(\w+)", src, re.M))
        st = {l.split("=")[0] for l in (D / f"{ten}.set").read_text().splitlines() if "=" in l}
        assert st == ins


def test_swap_va_stop_out():
    t = np.arange(3000); c = 1.0 + 0.0040 * np.sin(t / 15)
    g = pd.DataFrame({"open": np.r_[c[0], c[:-1]], "close": c}, index=pd.date_range("2020", periods=3000, freq="h"))
    g["high"] = g[["open", "close"]].max(axis=1); g["low"] = g[["open", "close"]].min(axis=1)
    a = BL.chay(g, "luoi_tp", 1e-4, 10, 10, 1.0, 10.0, lot_moi_1000=0.001)
    b = BL.chay(g, "luoi_tp", 1e-4, 10, 10, 1.0, 10.0, lot_moi_1000=0.001, swap_mua=-50, swap_ban=-50)
    assert b["tong_swap"] < 0 and b["equity_cuoi"] < a["equity_cuoi"]
    # xu hướng mạnh một chiều + lô lớn + đòn bẩy thấp -> có stop-out
    x = 1.0 + np.linspace(0, 0.3, 3000)
    g2 = pd.DataFrame({"open": np.r_[x[0], x[:-1]], "close": x, "high": x + 1e-4, "low": np.r_[x[0], x[:-1]] - 1e-4},
                      index=pd.date_range("2020", periods=3000, freq="h"))
    k = BL.chay(g2, "ro_dca", 1e-4, 10, 10, 1.0, 10.0, lot_moi_1000=0.05, base_usd=1.0, don_bay=30)
    assert k["so_stop_out"] >= 1 or k["chay_tai_khoan"]


def test_vang_sl_truoc_tp_va_phi():
    from nhan.dich_nguoc import backtest_vang as BV
    idx = pd.date_range("2020-01-06", periods=6, freq="h")
    g = pd.DataFrame({"open": [100, 100, 100, 100, 100, 100.0], "high": [100, 100, 106, 100, 100, 100.0],
                      "low": [100, 100, 94, 100, 100, 100.0], "close": [100.0] * 6}, index=idx)
    def th(i, ctx):
        return [dict(c=1, lot=0.1, sl_fn=lambda p: p - 5, tp_fn=lambda p: p + 5)] if i == 1 and ctx["so_mo"] == 0 else []
    k = BV.mo_phong(g, th, "t", von=10000, swap_mua=0, swap_ban=0)
    # vào 100.55, nến 3 chạm cả SL & TP -> SL trước: lỗ 5 USD giá x 0.1 lot x 100 oz = 50
    assert abs(k["equity_cuoi"] - 9950.0) < 1e-6 and k["so_lenh"] == 1
