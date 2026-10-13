"""Gop M5->H1/H4: OHLC dung, so bar, trung khop mau EURUSD H4 cu."""
from pathlib import Path

import pandas as pd

import gop_m5_len_h1_h4 as g


def test_gop_ohlc_va_so_bar(tmp_path):
    idx = pd.date_range("2024-01-02 00:00", periods=48, freq="5min")  # 4 gio
    df = pd.DataFrame({
        "open": range(48), "high": range(1, 49), "low": range(-1, 47),
        "close": range(48), "tick_volume": [1] * 48,
    }, index=idx)
    df.index.name = "time"
    src = tmp_path / "m5.csv"
    df.to_csv(src)
    h1 = g.gop(df, "1h")
    h4 = g.gop(df, "4h")
    assert len(h1) == 4
    assert len(h4) == 1
    assert h1.iloc[0]["open"] == 0 and h1.iloc[0]["close"] == 11
    assert h1.iloc[0]["high"] == 12 and h1.iloc[0]["low"] == -1
    assert h1.iloc[0]["tick_volume"] == 12
    assert h4.iloc[0]["open"] == 0 and h4.iloc[0]["close"] == 47
    # CLI
    ra1, ra4 = tmp_path / "h1.csv", tmp_path / "h4.csv"
    assert g.main([str(src), str(ra1), str(ra4)]) == 0
    assert len(pd.read_csv(ra1)) == 4


def test_trung_eurusd_h4_mau_cu():
    goc = Path("/workspace/du_lieu_fx")
    m5 = goc / "eurusd_m5_histdata_server.csv"
    h4_cu = goc / "eurusd_h4_tu_histdata_m5_server.csv"
    if not m5.exists() or not h4_cu.exists():
        return
    df = g.doc_m5(m5)
    h4 = g.gop(df, "4h")
    cu = pd.read_csv(h4_cu, parse_dates=["time"], index_col="time")
    chung = h4.index.intersection(cu.index)
    assert len(chung) == len(cu)
    lech = (h4.loc[chung, ["open", "high", "low", "close"]]
            - cu.loc[chung, ["open", "high", "low", "close"]]).abs().max().max()
    assert lech == 0.0
