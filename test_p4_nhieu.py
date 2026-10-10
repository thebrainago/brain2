"""P4: bo sinh gia nhieu GARCH dung duong gia + tong hop ti le (hieu_chuan/p4_nhieu.py)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "hieu_chuan"))
import p4_nhieu as P  # noqa: E402


def test_garch_duong_hop_le():
    df = P.gia_lap_garch_duong(2000, seed=3)
    assert len(df) == 2000
    assert (df.high >= df[["open", "close"]].max(axis=1) - 1e-12).all()
    assert (df.low <= df[["open", "close"]].min(axis=1) + 1e-12).all()
    # open bar sau = close bar truoc (duong gia lien tuc)
    assert np.allclose(df.open.to_numpy()[1:], df.close.to_numpy()[:-1])
    r = np.diff(np.log(df.close.to_numpy()))
    vol = r.std() * np.sqrt(24 * 260)
    assert 0.05 < vol < 0.15


def test_wilson_va_ti():
    t = P.ti(0, 100)
    assert t["ti_le"] == 0.0 and t["ci95"][0] == 0 and 0.02 < t["ci95"][1] < 0.05
    assert P.ti(5, 0)["ti_le"] is None


def test_luoi_o_72():
    o = P.luoi_o()
    assert len(o) == 72 and all(ts.che_do == "hai_chieu" for ts in o)


def test_tong_R2_dem_dung():
    b = [{"seed": 1, "duong": {"tot_kiem_dat": True}}, {"seed": 2, "duong": {"tot_kiem_dat": False}}]
    r = [{"seed": 1, "xau_nhat_lai": -5.0, "moi_bien_the_dat_25_09": False},
         {"seed": 2, "xau_nhat_lai": 3.0, "moi_bien_the_dat_25_09": True}]
    t = P.tong_R2(r, b)
    assert t["goc_gan_open_2pip_dat_25_09"]["k"] == 1
    assert t["R2_xau_nhat_lai_gt_0"]["k"] == 1
    assert t["trong_so_dat_goc_R2_con_lot"]["k"] == 0 and t["trong_so_dat_goc_R2_con_lot"]["n"] == 1


def test_chay_R2_bien_the_du():
    # chuoi ngan: 8 bien the (4 thu tu x 2 spread), khong loi
    r = P.chay_R2(("rw", 600, 7, 0))
    assert len(r["bien_the"]) == 8
    assert r["xau_nhat_lai"] == min(v["lai"] for v in r["bien_the"].values())


def test_p4_dau_de_xuat_khong_can_p4():
    import p4_dau as D
    luat = {"R2_duong_xau_nhat_gt_0": {"giu": [2], "giu_ma_tester_lo (nguoc dau lot qua)": [],
                                       "loai_ma_tester_lai (chan oan)": []},
            "R1_v3_lai_ge_10": {"giu_ma_tester_lo (nguoc dau lot qua)": [6]}}
    d = D.de_xuat(luat, None)
    assert "CHUA DO DUOC" in d["D1_R2_xau_nhat_gt_0 (chong NGUOC DAU voi MT5)"]["nhieu"][0]
