# -*- coding: utf-8 -*-
"""Test XUONG (22/10/2026) tren du lieu TONG HOP (khong co gia that tren cloud). Kiem: tin hieu to hop, may keo lot, phan ra, toan tu, dieu phoi, danh muc."""
import random
import sqlite3
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import ong_dan as OD
from nhan import xuong as XU
from nhan import xuong_danh_muc as DM
from nhan import xuong_may as XM
from nhan import xuong_tach as TA
from nhan import xuong_tin_hieu as XT
from nhan import xuong_toan_tu as TT
from nhan import xuong_toi_uu as TU


def gia_tong_hop(n=6000, seed=1, theta=0.995, sig=0.0007, bat_dau="2016-01-04"):
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = x[i - 1] * theta + rng.normal(0, sig)
    c = 1.1 * np.exp(x)
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.0003, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.0003, n)))
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=pd.date_range(bat_dau, periods=n, freq="h"))


MRZ = {"kieu": "brain", "tham": {"kieu": "MRZ", "n": 50, "nguong_z": 2.0}}
MRZ2 = {"kieu": "brain", "tham": {"kieu": "MRZ", "n": 30, "nguong_z": 1.5}}
QL = {"tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 5, "dca_he_so_lot": 1.3}


def _the(id_="t_mrz", th=MRZ):
    return {"id": id_, "ten": id_, "loai": "he_hoan_thien", "uu_tien": 2, "tin_hieu": th, "ma_goi_y": ["EURUSD"]}


def _thu(**kw):
    return {"ma": "EURUSD", "khung": "H1", "tham": {}, "ql": dict(QL, **kw)}


class Nen:
    """Gia tong hop duoc tiem vao cache ong dan + ma_co_du_lieu."""

    def __enter__(self):
        self.cfg = OD.cau_hinh()
        self.cu = dict(OD._GIA)
        self.cu_ma = OD.ma_co_du_lieu
        OD._GIA[("EURUSD", "H1", self.cfg.get("tu_ngay"))] = gia_tong_hop()
        OD._GIA[("GBPUSD", "H1", self.cfg.get("tu_ngay"))] = gia_tong_hop(seed=7)
        OD.ma_co_du_lieu = lambda cfg=None: ["EURUSD", "GBPUSD"]
        return self.cfg

    def __exit__(self, *a):
        OD._GIA.clear()
        OD._GIA.update(self.cu)
        OD.ma_co_du_lieu = self.cu_ma


# ------------------------------------------------------------------ tin hieu
def test_bo_phieu_va_khoang_cach():
    a = np.array([0, 1, 0, 0, 0, 0, 0, 0])
    b = np.array([0, 0, 1, 0, 0, 0, 0, 0])
    c = np.array([0, 0, 0, -1, 0, 0, 0, 0])
    r = XT.bo_phieu([a, b, c], k=2, cua_so=3)
    assert r[2] == 1                                   # a va b cung chieu trong cua so, su kien moi o nen 2
    assert r[3] == 0                                   # c nguoc chieu -> khong vao
    s = np.array([1, 0, 1, 0, 0, 1, -1, 1])
    assert XT.khoang_cach(s, 3).tolist() == [1, 0, 0, 0, 0, 1, -1, 1]


def test_che_do_nhan_qua_khong_nhin_truoc():
    df = gia_tong_hop(3000)
    for cd in ({"ten": "bien_dong", "n": 14, "cua_so": 300, "q": 0.5}, {"ten": "xu_huong", "n": 50, "x": 1.5}, {"ten": "khoang", "n": 100, "tu": 0.2, "den": 0.8},
               {"ten": "gio", "tu": 8, "den": 17}, {"ten": "thu", "ds": [0, 1, 2]}):
        day = XT.mat_na_che_do(df, cd)
        cut = XT.mat_na_che_do(df.iloc[:2000], cd)
        assert (day[:2000] == cut).all(), cd


def test_dao_dispatch_va_su_kien_dich_vong():
    with Nen() as cfg:
        df = OD.gia("EURUSD", "H1", cfg)
        goc = OD.tin_hieu(_the(), df, {}, "EURUSD")
        dao = OD.tin_hieu({"tin_hieu": {"kieu": "dao", "nguon": MRZ}}, df, {}, "EURUSD")
        assert (np.asarray(dao) == -np.asarray(goc)).all() and (goc != 0).sum() > 20
        tt = XT.thay_the_dich_vong(np.asarray(goc), df.index, 777)
        s2 = OD.tin_hieu({"tin_hieu": tt}, df, {}, "EURUSD")
        assert (s2 != 0).sum() >= 0.95 * (goc != 0).sum() and (np.asarray(s2) != np.asarray(goc)).any()


def test_chuan_hoa_ql():
    a = XM.chuan_hoa_ql({"tp_pct": 0.003, "dca_toi_da": 5.0, "dca_buoc_pct": 0.005, "dca_he_so_lot": 1.3})
    b = XM.chuan_hoa_ql({"tp_pct": 0.003, "dca_toi_da": 5, "dca_buoc_pct": 0.005, "dca_he_so_lot": 1.3})
    assert a == b and isinstance(a["dca_toi_da"], int)
    assert XM.chuan_hoa_ql({"dca_toi_da": 0, "dca_buoc_pct": 0.01}) == XM.chuan_hoa_ql({"dca_toi_da": 0, "dca_buoc_pct": 0.02})


# ------------------------------------------------------------------ may
def test_chuan_lot_dat_muc_tieu_va_nho():
    with Nen() as cfg:
        m = XM.May(cfg, dd_muc_tieu=40.0)
        cl = m.chuan_lot(_the(), _thu())
        assert cl["tinh_trang"] in ("vua", "tran_lot", "khong_lenh")
        if cl["tinh_trang"] == "vua":
            assert cl["r"]["sut_giam_pct"] <= 40.0 + 1e-6 and not cl["r"]["so_stop_out"]
        n = m.so_chay
        m.chuan_lot(_the(), _thu())
        assert m.so_chay == n                           # lan hai trung bo nho
        # lot xa hon muc keo thi vuot muc tieu (do don dieu)
        if cl["tinh_trang"] == "vua":
            r2 = m.chay(_the(), _thu(), (0.0, m.cuoi_is), cl["lot"] * 2.5)
            assert r2["chay"] or r2["so_stop_out"] or r2["sut_giam_pct"] > 40.0


def test_luu_sqlite_chay_lai_khong_do_lai():
    with Nen() as cfg, tempfile.TemporaryDirectory() as d:
        tep = Path(d) / "x.sqlite"
        m = XM.May(cfg, dd_muc_tieu=40.0, tep_luu=tep)
        m.chuan_lot(_the(), _thu())
        assert m.so_chay > 0
        m2 = XM.May(cfg, dd_muc_tieu=40.0, tep_luu=tep)
        m2.chuan_lot(_the(), _thu())
        assert m2.so_chay == 0


def test_phan_ra_co_nhan_va_khong_tim_thay_edge_tren_bo_bien():
    with Nen() as cfg:
        m = XM.May(cfg, dd_muc_tieu=40.0)
        cl = m.chuan_lot(_the(), _thu())
        pr = TA.phan_ra(m, _the(), _thu(), cl["lot"], so_mau=3)
        assert pr["nhan"] in ("QUAN_LI_GANH", "TIN_HIEU_GANH", "CA_HAI_DEU_LAI", "CAN_CA_HAI", "KHONG_LAI", "KHONG_TACH_DUOC")


# ------------------------------------------------------------------ toi uu
def test_toi_uu_khong_te_hon_goc_va_tra_khuyen_nghi():
    with Nen() as cfg:
        m = XM.May(cfg, dd_muc_tieu=40.0, dd_khuyen_nghi=40.0)
        k = TU.toi_uu(m, _the(), _thu(), ngan_sach=14, chi_ql=True, in_ra=lambda *a: None)
        tot = k["tot_nhat"]
        assert tot["lai_o_dd"] >= k["goc"]["lai_o_dd"] - 1e-6
        assert set(tot["thu"]["ql"]) <= set(XM.TRUONG_QL_MT5)
        kn = tot["khuyen_nghi"]
        assert kn["lot"] is None or kn["sut_giam_pct"] <= 40.0 + 1e-6


# ------------------------------------------------------------------ toan tu
def _cha():
    return [TT.Cha(_the("a", MRZ), _thu(), 30.0, "TIN_HIEU_GANH"), TT.Cha(_the("b", MRZ2), _thu(tp_pct=0.004), 20.0, "QUAN_LI_GANH"),
            TT.Cha(_the("c", MRZ2), dict(_thu(), ma="GBPUSD"), 10.0, "CAN_CA_HAI")]


def test_moi_toan_tu_sinh_the_hop_le():
    rng = random.Random(3)
    cha = _cha()
    tong = 0
    for ten in TT.TEN_TOAN_TU:
        kw = {"tai_san": [("EURUSD", "H1"), ("GBPUSD", "H1")]} if ten == "chuyen_ma" else {}
        xs = TT.sinh(ten, cha, rng, 6, **kw)
        for x in xs:
            assert x["id"].startswith("xg_") and x["tin_hieu"] and x["_thu"]["ma"] and x["xuong"]["toan_tu"] == ten
            assert set(x["_thu"]["ql"]) <= set(XM.TRUONG_QL_MT5)
            assert "lot_tren_1000" not in x["_thu"]["ql"]
        assert len({x["id"] for x in xs}) == len(xs)
        tong += len(xs)
    assert tong >= 10


def test_sinh_nhan_ma_bang_nhau_voi_cung_hat():
    a = [x["id"] for x in TT.sinh("cay_quan_li", _cha(), random.Random(5), 5)]
    b = [x["id"] for x in TT.sinh("cay_quan_li", _cha(), random.Random(5), 5)]
    assert a == b


def test_the_to_hop_do_duoc_bang_may():
    with Nen() as cfg:
        m = XM.May(cfg, dd_muc_tieu=40.0)
        rng = random.Random(1)
        for ten in ("bo_phieu", "chuyen_che_do", "khoang_cach", "dao", "dot_bien"):
            xs = TT.sinh(ten, _cha(), rng, 2)
            for x in xs[:1]:
                r = m.chay(x, x["_thu"], (0.0, 1.0), 1.0)
                assert not r.get("loi"), (ten, r)


# ------------------------------------------------------------------ dieu phoi
def _db_mau():
    cn = OD._db(Path(tempfile.mkdtemp()) / "ts.sqlite")
    for i, (th, ql) in enumerate(((MRZ, QL), (MRZ2, dict(QL, tp_pct=0.004)))):
        t = _the("goc%d" % i, th)
        thu = dict(_thu(), ql=dict(ql, lot_tren_1000=1.0))
        with cn:
            OD._luu(cn, t, "loc", "DAT_LOC", {"tot_nhat": {"thu": thu, "kq": {"lai_pct_nam": 20.0, "sut_giam_pct": 40.0}}})
    return cn


def test_chay_dau_cuoi_dang_ky_va_bao_cao():
    with Nen() as cfg, tempfile.TemporaryDirectory() as d:
        cn = _db_mau()
        ra = Path(d) / "ra"
        ket = XU.chay(cn, cfg, tran=3, phut=5, dd=40.0, so_toi_uu=1, ngan_sach_toi_uu=8, tep_luu=Path(d) / "x.sqlite", ra=ra, in_ra=lambda *a: None,
                      toan_tu=["cay_quan_li", "bo_phieu", "khoang_cach", "dao"])
        assert ket["so_cha"] == 2
        assert (ra / "XUONG.md").exists() and (ra / "ket_qua.json").exists()
        for c in ket["chot"]:
            if c.get("dang_ky"):
                rows = [x for x in OD.cac_the(cn) if x[0]["id"] == c["id"]]
                assert rows and rows[0][1] == "toi_uu" and rows[0][2] == "DA_TOI_UU"
                r = rows[0][3]["tot_nhat"]["kq"]
                assert r["sut_giam_pct"] <= 40.0 + 5 and "ql" in rows[0][3]["tot_nhat"]["thu"]
        # sau loc, chay `buoc_loc` doc duoc the xuong
        OD.buoc_loc(cn, in_ra=lambda *a: None)


# ------------------------------------------------------------------ danh muc
def test_danh_muc_hai_the_khong_te_hon_the_tot_nhat():
    with Nen() as cfg:
        m = XM.May(cfg, dd_muc_tieu=40.0, giu_duong_von=True)
        ds = [(_the("a", MRZ), _thu(), 2.0), (dict(_the("c", MRZ2)), dict(_thu(), ma="GBPUSD"), 2.0)]
        d = DM.danh_muc(m, ds, dd_muc=40.0)
        if d.get("loi"):
            return                                                        # tong hop khong du lai: chap nhan nhung khong duoc nem
        assert d["lai_pct_nam"] >= d["lai_tot_nhat_rieng"] - 1e-6
        assert d["sut_giam_pct"] <= 40.0 + 0.5
        assert 1 <= len(d["thanh_vien"]) <= 5


def test_do_danh_muc_scale_thuan():
    nam = 4.0
    X = np.cumsum(np.r_[np.zeros(10), np.full(1000, 0.001), np.full(300, -0.0005), np.full(1000, 0.001)])
    r = DM.do_danh_muc(X, X, nam, 30.0)
    assert 0 < r["s"] and r["sut_giam_pct"] <= 30.0 + 0.1
