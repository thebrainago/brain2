import lzma

import numpy as np
import pandas as pd
import pytest

import tai_dukascopy_tick_m1 as T


def _bi5(rows):
    a = np.array(rows, dtype=T.TICK_DT)
    return lzma.compress(a.tobytes(), format=lzma.FORMAT_ALONE)


def test_giai_ma_va_gom_m1():
    g = pd.Timestamp("2024-01-10 14:00", tz="UTC")
    raw = _bi5([(1000, 110012, 110010, 1.0, 1.0), (30000, 110020, 110015, 1, 1),
                (59999, 110005, 110001, 1, 1), (61000, 110030, 110028, 1, 1)])
    tk = T.giai_ma_tick(raw, g, 100000)
    assert tk.index[0] == g + pd.Timedelta(seconds=1)
    assert tk["bid"].iloc[0] == pytest.approx(1.10010)
    m1 = T.gom_m1(tk)
    assert len(m1) == 2
    r = m1.iloc[0]
    assert (r.bid_o, r.bid_h, r.bid_l, r.bid_c) == pytest.approx((1.10010, 1.10015, 1.10001, 1.10001))
    assert (r.ask_o, r.ask_c) == pytest.approx((1.10012, 1.10005))
    assert r.so_tick == 3
    assert r.spread_min == pytest.approx(0.00002) and r.spread_max == pytest.approx(0.00005)
    assert r.spread_tb == pytest.approx((0.00002 + 0.00005 + 0.00004) / 3)
    assert m1.index[1] == g + pd.Timedelta(minutes=1)


def test_bi5_rong():
    assert T.giai_ma_tick(b"", pd.Timestamp("2024-01-01", tz="UTC"), 1000).empty
    assert T.gom_m1(pd.DataFrame(columns=["bid", "ask"])).empty


def test_doc_va_khung(tmp_path, monkeypatch):
    import du_lieu_chuan as D
    monkeypatch.setattr(D, "GOC", tmp_path)
    idx = pd.date_range("2024-01-10 00:00", periods=600, freq="1min", tz="UTC")
    bid = 1.1 + np.arange(600) * 1e-5
    m1 = pd.DataFrame({"bid_o": bid, "bid_h": bid + 2e-5, "bid_l": bid - 1e-5, "bid_c": bid + 1e-5,
                       "ask_o": bid + 1e-4, "ask_h": bid + 1.2e-4, "ask_l": bid + 0.9e-4, "ask_c": bid + 1.1e-4,
                       "spread_tb": 1e-4, "spread_min": 0.8e-4, "spread_max": 1.5e-4,
                       "so_tick": np.int32(5)}, index=idx)
    m1.index.name = "time"
    (tmp_path / "m1" / "EURUSD").mkdir(parents=True)
    m1.iloc[:300].to_parquet(tmp_path / "m1" / "EURUSD" / "EURUSD_2024.parquet")
    (tmp_path / "_ngay" / "EURUSD").mkdir(parents=True)
    m1.iloc[300:].to_parquet(tmp_path / "_ngay" / "EURUSD" / "2024-01-10.parquet")
    h1 = D.doc("eurusd", "H1", "2024-01-10", "2024-01-10")
    assert len(h1) == 10
    assert h1["open"].iloc[0] == pytest.approx((bid[0] * 2 + 1e-4) / 2)
    assert h1["close"].iloc[0] == pytest.approx((bid[59] + 1e-5 + bid[59] + 1.1e-4) / 2)
    assert h1["high"].iloc[0] == pytest.approx(max((bid[:60] + 2e-5 + bid[:60] + 1.2e-4) / 2))
    assert h1["so_tick"].iloc[0] == 300
    b = D.doc("EURUSD", "M5", gia="bid")
    assert len(b) == 120 and b["low"].iloc[0] == pytest.approx(bid[0] - 1e-5)
    a = D.doc("EURUSD", "D1", gia="tat_ca")
    assert len(a) == 1 and "mid_c" in a and a["ask_h"].iloc[0] == pytest.approx(bid[-1] + 1.2e-4)
    assert len(D.doc("EURUSD", "M1", "2024-01-10 01:00", "2024-01-10 01:59")) == 60
    with pytest.raises(FileNotFoundError):
        D.doc("GBPUSD")
    with pytest.raises(ValueError):
        D.doc("EURUSD", "W3")
    assert D.ten_chuan("US500") == "USA500.IDX"
    r = D.sinh_khung("EURUSD")
    assert r["H4"] == 3 and (tmp_path / "D1" / "EURUSD.parquet").exists()
