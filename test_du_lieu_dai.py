# -*- coding: utf-8 -*-
import datetime as dt
import io
import lzma
import struct
import zipfile

import numpy as np
import pandas as pd

from nhan import du_lieu_dai as D, phi_dai as P, tai_du_lieu as T


def test_est_sang_server_dst():
    t = pd.DatetimeIndex(["2025-01-15 10:00", "2025-07-15 10:00"])     # EST co dinh
    s = D.est_sang_server(t)
    # dong: EST 10:00 = NY 10:00 -> server 17:00 (GMT+2); he: EST 10:00 = UTC 15 = NY 11:00 (EDT) -> 18:00 (GMT+3)
    assert list(s.strftime("%H:%M")) == ["17:00", "18:00"]


def test_doc_histdata_zip_va_gop(tmp_path):
    f = tmp_path / "a.zip"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("DAT_ASCII_X_M1_2010.csv", "20100104 000000;1.1;1.2;1.0;1.15;0\n20100104 000100;1.15;1.2;1.1;1.12;0\n")
    h = D.doc_histdata_zip(f)
    assert str(h.index[0]) == "2010-01-04 07:00:00" and len(h) == 2
    uu = h.iloc[:1] * 0 + 9
    g = D.gop(uu, h)
    assert len(g) == 2 and g["close"].iloc[0] == 9 and g["close"].iloc[1] == 1.12
    m5 = D.sang_khung(g)
    assert len(m5) == 1 and m5["high"].iloc[0] == 9


def test_phu_song_dem_lo_hong():
    t = pd.date_range("2025-03-03 00:00", "2025-03-07 21:55", freq="5min")
    x = pd.DataFrame({"close": 1.0}, index=t)
    x = x[~((x.index >= "2025-03-04 10:00") & (x.index < "2025-03-04 16:00"))]
    r = D.phu_song(x)["2025"]
    assert r["lo_hong_4h"] == 1 and 90 < r["phu_pct"] < 100


def _bi5(rows):
    return lzma.compress(b"".join(struct.pack(">iiiiif", *r) for r in rows), format=lzma.FORMAT_ALONE)


def test_doc_bi5_va_he_so():
    b = _bi5([(60, 110000, 110010, 109990, 110020, 1.0)])
    r = T.doc_bi5_nen(b, dt.date(2020, 1, 2), T.he_so_dk("EURUSD"))
    assert r[0][0] == dt.datetime(2020, 1, 2, 0, 1) and abs(r[0][4] - 1.1001) < 1e-9
    assert T.he_so_dk("USDJPY") == 1e3 and T.he_so_dk("XAUUSD") == 1e3


def test_lui_cap_so_nhan():
    assert T.lui(0, "120") == 120 and T.lui(20) <= T.LUI_MAX * 1.2 and 48 <= T.lui(0) <= 72


def test_ky_histdata():
    k = T.ky_histdata(2026, 3)
    assert k[0] == "2000" and k[-3:] == ["2025", "202601", "202602"]


def test_he_so_nam_va_ngoai_suy(tmp_path, monkeypatch):
    bang = pd.DataFrame([(y, g, s) for y, s in ((2024, 2.0), (2025, 1.0)) for g in range(2, 23) for _ in range(2)],
                        columns=["nam", "gio", "spread"])
    assert P.he_so_tu_bang(bang) == {2024: 2.0, 2025: 1.0}
    monkeypatch.setattr(P, "bang_mt5", lambda ma, thu: bang)
    monkeypatch.setattr(P, "bang_duka", lambda ma, thu: pd.DataFrame(columns=["nam", "gio", "spread"]))
    hs, ng = P.he_so_nam("X", 2022, 2026, tmp_path)
    assert hs[2022] == 2.0 and ng[2022] == "NGOẠI SUY" and hs[2026] == 1.0 and ng[2024] == "TICK_XM"


def test_mang_he_so_va_tai_khoan():
    idx = pd.DatetimeIndex(["2003-05-01", "2010-01-01", "2030-01-01"])
    assert list(P.mang_he_so(idx, {"2004": 3.0, "2026": 1.0})) == [3.0, 3.0, 1.0]
    assert list(P.mang_he_so(idx, {})) == [1.0, 1.0, 1.0]
    from nhan import tai_khoan as TK
    hs = TK.HoSoPhi(ma="EURUSD", spread_nam={2010: 2.0})
    assert list(TK._he_so_nam(idx, hs)) == [2.0, 2.0, 2.0]


def test_hoa_hong_do(tmp_path):
    (tmp_path / "a_lenh_mt5.csv").write_text("thoi_gian;hoa_hong\nx;0.00\ny;0.00\n")
    assert P.hoa_hong_do(tmp_path) == {"tong_usd": 0.0, "so_deal": 2}


def test_mt5_tai_lich_su_tien_ich():
    from mt5tools import tai_lich_su_mt5 as M
    assert M.ten_tren_san("XAUUSD", {"GOLDmicro", "EURUSDmicro"}) == "GOLDmicro"
    assert M.ten_tren_san("EURUSD", {"EURUSDmicro"}) == "EURUSDmicro" and M.ten_tren_san("X", set()) is None
    assert M.thang("2025-11", dt.date(2026, 2, 3)) == [(2025, 11), (2025, 12), (2026, 1), (2026, 2)]
    assert all(d.weekday() in (1, 2) for d in M.ngay_mau(2020, 5))
