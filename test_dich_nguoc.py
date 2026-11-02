# -*- coding: utf-8 -*-
"""Kiểm thử nhan/dich_nguoc: sinh lệnh từ một luật ĐÃ BIẾT rồi xem module có khôi phục được không."""
import numpy as np
import pandas as pd
import pytest
from nhan.dich_nguoc import doc_lich_su as DL, phan_tich as PT, dac_trung as DT
from nhan.dich_nguoc.__main__ import chay

pytestmark = pytest.mark.timeout(120)
PIP = 0.0001


def _gia(n=6000, hat=1):
    r = np.random.default_rng(hat)
    c = 1.10 + np.cumsum(r.normal(0, 12 * PIP, n))
    o = np.r_[c[0], c[:-1]]; h = np.maximum(o, c) + np.abs(r.normal(0, 4 * PIP, n)); l = np.minimum(o, c) - np.abs(r.normal(0, 4 * PIP, n))
    return pd.DataFrame({"time": pd.date_range("2024-01-01", periods=n, freq="h"), "open": o, "high": h, "low": l, "close": c})


def _sinh_lenh(g):
    """Luật biết trước: giờ 7-10, RSI14 (nến đóng trước) < 30 -> BUY 0.01; DCA mỗi 20 pip giá đi ngược, lot x1.5, tối đa 6;
    đóng cả rổ khi giá >= giá trung bình + 15 pip."""
    gi = g.set_index("time"); f = DT.chi_bao(gi[["open", "high", "low", "close"]], PIP)
    lenh, ro = [], []
    for t, (ts, row) in enumerate(gi.iterrows()):
        if t < 60: continue
        if ro:
            tb = sum(x["lot"] * x["gia_mo"] for x in ro) / sum(x["lot"] for x in ro)
            if row.high >= tb + 15 * PIP:
                for x in ro: x.update(dong_luc=ts, gia_dong=tb + 15 * PIP, tp=tb + 15 * PIP); lenh.append(x)
                ro = []; continue
            last = ro[-1]
            if len(ro) < 6 and row.low <= last["gia_mo"] - 20 * PIP:
                ro.append({"mo_luc": ts + pd.Timedelta(minutes=30), "lot": round(last["lot"] * 1.5, 4), "gia_mo": last["gia_mo"] - 20 * PIP})
        elif 7 <= ts.hour <= 10 and f["rsi14"].iloc[t] < 30:
            ro.append({"mo_luc": ts, "lot": 0.01, "gia_mo": row.open})
    rows = [{"Open Date": x["mo_luc"], "Close Date": x["dong_luc"], "Symbol": "EURUSD", "Action": "Buy", "Lots": x["lot"],
             "SL": 0, "TP": x["tp"], "Open Price": x["gia_mo"], "Close Price": x["gia_dong"], "Profit": 1} for x in lenh]
    return pd.DataFrame(rows)


def test_khoi_phuc_luat_tong_hop(tmp_path):
    g = _gia(); ls = _sinh_lenh(g)
    p = tmp_path / "myfxbook.csv"; ls.to_csv(p, index=False)
    kq, lich_su, the = chay(str(p), g)
    tq = kq["tong_quat"]
    assert tq["so_lenh"] >= 40
    assert tq["lot"]["kieu_lot"] == "martingale"
    assert tq["lot"]["he_so_lot_trung_vi"] == pytest.approx(1.5, abs=0.05)
    assert tq["lot"]["buoc_luoi_pip_trung_vi"] == pytest.approx(20, abs=0.5)
    assert tq["hedge"]["co_hedge"] is False
    gio_dau = PT.ro(DL.doc(str(p))).groupby("ro").head(1)["mo_luc"].dt.hour
    assert gio_dau.between(7, 10).all()
    pb = kq["phan_biet"]
    assert pb["auc_cay_cv5"] > 0.8
    top2 = list(pb["dac_trung_xep_hang"])[:3]
    assert "rsi14" in top2 or "bb_z20" in top2 or "loi_suat_5bar_atr" in top2
    assert pb["dac_trung_xep_hang"]["rsi14"]["vao_trung_vi"] < 30
    assert "rsi14" in pb["luat_cay"] or "gio" in pb["luat_cay"]
    assert the.candidate_kind == "method" and lich_su.fingerprint in the.source_artifact_fingerprints
    assert "martingale" in the.title


def test_ngau_nhien_khong_tach(tmp_path):
    """Đối chứng: lệnh vào ở thời điểm ngẫu nhiên -> AUC phải gần 0.5 (không bịa ra 'edge')."""
    g = _gia(hat=3); r = np.random.default_rng(5)
    t = g["time"].iloc[r.choice(np.arange(100, len(g) - 2), 150, replace=False)].sort_values()
    df = pd.DataFrame({"Open Date": t.values, "Close Date": t.values + np.timedelta64(2, "h"), "Symbol": "EURUSD",
                       "Action": "Sell", "Lots": 0.1, "Open Price": 1.1, "Close Price": 1.1})
    p = tmp_path / "x.csv"; df.to_csv(p, index=False)
    kq, _, _ = chay(str(p), g)
    assert kq["phan_biet"]["auc_logistic_cv5"] < 0.62
    assert kq["tong_quat"]["lot"]["kieu_lot"] in ("co_dinh_don_le", "co_dinh_dca")  # lot cố định, không martingale


MT4 = """<html><body><table>
<tr><td>Ticket</td><td>Open Time</td><td>Type</td><td>Size</td><td>Item</td><td>Price</td><td>S / L</td><td>T / P</td><td>Close Time</td><td>Price</td><td>Commission</td><td>Taxes</td><td>Swap</td><td>Profit</td></tr>
<tr><td>1</td><td>2024.03.01 08:00:00</td><td>buy</td><td>0.10</td><td>eurusd</td><td>1.08000</td><td>0</td><td>1.08200</td><td>2024.03.01 10:00:00</td><td>1.08200</td><td>0</td><td>0</td><td>0</td><td>20.00</td></tr>
<tr><td>2</td><td>2024.03.01 09:00:00</td><td>sell</td><td>0.10</td><td>eurusd</td><td>1.08100</td><td>1.08300</td><td>0</td><td>2024.03.01 11:00:00</td><td>1.08000</td><td>0</td><td>0</td><td>0</td><td>10.00</td></tr>
<tr><td>3</td><td>2024.03.01 09:30:00</td><td>balance</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>100</td></tr>
</table></body></html>"""


def test_doc_mt4_html_va_hedge():
    df = DL.doc(MT4)
    assert len(df) == 2 and set(df.chieu) == {"buy", "sell"}
    assert df.symbol.iloc[0] == "EURUSD" and df.gia_dong.iloc[0] == pytest.approx(1.082)
    tq = PT.tong_quat(df)
    assert tq["hedge"]["lenh_buy_chong_sell_cung_luc"] == 1
    assert tq["tp_sl"]["tp_pip_trung_vi"] == pytest.approx(20, abs=0.1)


def test_doc_mql5_signal_csv():
    s = "Time;Type;Volume;Symbol;Price;S/L;T/P;Time;Price;Commission;Swap;Profit\n" \
        "2024.05.02 07:00:00;Buy;0.01;XAUUSD;2300.0;;;2024.05.02 09:00:00;2305.0;0;0;5\n" \
        "2024.05.02 08:00:00;Buy;0.02;XAUUSD;2295.0;;;2024.05.02 09:00:00;2305.0;0;0;20\n"
    df = DL.doc(s)
    assert list(df.lot) == [0.01, 0.02]
    lot = PT.chuoi_lot(df)
    assert lot["he_so_lot_trung_vi"] == 2.0 and lot["buoc_luoi_pip_trung_vi"] == pytest.approx(50)
