"""Vong 27 ck2: gop_histdata_m5 phai TAT DINH khi file HistData co phut trung moc (gia khac)."""
import zipfile

import pandas as pd

import gop_histdata_m5 as g


def _zip(p, ten, dong):
    with zipfile.ZipFile(p, "w") as z:
        z.writestr(ten + ".csv", "\n".join(dong) + "\n")


def _gop(thu_muc, ra):
    g.main([str(thu_muc), "TESTFX", "2026-07-01", "2026-09-01", str(ra)])
    return pd.read_csv(ra, index_col=0)


def test_phut_trung_giu_ban_dau_tien_bat_ke_file_khac(tmp_path):
    thang7 = []
    goc = pd.Timestamp("2026-07-06")
    for m in range(25 * 1440):                  # 25 ngay lien tuc (mang lon: quicksort moi lo bat on dinh)
        t = goc + pd.Timedelta(minutes=m)
        thang7.append(t.strftime("%Y%m%d %H%M%S") + ";1.1000;1.1010;1.0990;1.1005;0")
        if m % 97 == 7:                         # nhu file that: phut TRUOC lap lai (lui thu tu), gia khac
            t0 = t - pd.Timedelta(minutes=1)
            thang7.append(t0.strftime("%Y%m%d %H%M%S") + ";1.9000;1.9000;1.9000;1.9000;0")
    a = tmp_path / "a"; a.mkdir()
    _zip(a / "DAT_ASCII_TESTFX_M1_202607.zip", "DAT_ASCII_TESTFX_M1_202607", thang7)
    b = tmp_path / "b"; b.mkdir()
    _zip(b / "DAT_ASCII_TESTFX_M1_202607.zip", "DAT_ASCII_TESTFX_M1_202607", thang7)
    _zip(b / "DAT_ASCII_TESTFX_M1_202608.zip", "DAT_ASCII_TESTFX_M1_202608",
         [(pd.Timestamp("2026-08-03") + pd.Timedelta(minutes=m)).strftime("%Y%m%d %H%M%S") + ";1.2000;1.2000;1.2000;1.2000;0"
          for m in range(10 * 1440)])
    ra_a = _gop(a, tmp_path / "a.csv")
    ra_b = _gop(b, tmp_path / "b.csv")
    chung = ra_a.index.intersection(ra_b.index)
    assert len(chung) == len(ra_a)
    pd.testing.assert_frame_equal(ra_a.loc[chung], ra_b.loc[chung])
    assert ra_a["high"].max() < 1.9          # ban trung (1.9) dung sau -> bi bo
