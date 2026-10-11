# -*- coding: utf-8 -*-
"""A1 (the-brain 02 D2, 11/10/2026): TAI HONG khong duoc hieu la HET TRANG.

Truoc sua: `liet_ke_mql5` tra `[]` ca khi tai hong -> `tai_mql5` break nhu het trang ->
`tru/cau_kho.py` van doi con tro `TRANG_SAU.json` -> trang sau bi bo qua vinh vien.
Kiem: (1) `liet_ke_mql5` tra None khi tai hong, [] khi trang rong that; (2) `tai_mql5` ghi
`loi_trang`/`trang_loi`; (3) con tro DUNG YEN khi tai hong, ve 2 khi het trang that;
(4) bai `ok: False` duoc thu lai sau THU_LAI_GIO gio, khong truoc.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

LAB = Path(__file__).resolve().parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from nhan import cau_kho_ma as CK          # noqa: E402
from nhan import ma_nguon as MN            # noqa: E402
from test_cau_kho_ma import EA            # noqa: E402


def _tru(thu_muc: str):
    with mock.patch.dict(os.environ, {"BRAIN_CAU_KHO_DIR": thu_muc,
                                      "BRAIN_CAU_KHO_GIAY_TAI": "30"}):
        import tru.cau_kho as T
        return importlib.reload(T)


class LietKe(unittest.TestCase):
    def test_tai_hong_tra_none(self):
        with mock.patch.object(MN, "_lay", return_value=None):
            self.assertIsNone(MN.liet_ke_mql5("experts", 7))

    def test_trang_rong_that_tra_list_rong(self):
        with mock.patch.object(MN, "_lay", return_value="<html><body>no items</body></html>"):
            self.assertEqual(MN.liet_ke_mql5("experts", 7), [])

    def test_trang_co_bai(self):
        html = '<a href="/en/code/76331">Moving Average Expert Advisor</a>'
        with mock.patch.object(MN, "_lay", return_value=html):
            ds = MN.liet_ke_mql5("experts", 2)
        self.assertEqual([b["id"] for b in ds], ["76331"])


class TaiMql5(unittest.TestCase):
    def test_loi_trang_ghi_ro_khong_phai_het(self):
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(MN, "liet_ke_mql5", lambda m, t: None), \
                mock.patch.object(MN, "tai_ma_nguon", lambda b: None):
            r = CK.tai_mql5(d, so_trang=1, trang_dau=9, nghi_giay=0, in_ra=lambda *_: None)
        self.assertEqual(r.get("loi_trang"), 1)
        self.assertEqual(r.get("trang_loi"), [9])
        self.assertNotIn("het_trang", r)

    def test_het_trang_that(self):
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(MN, "liet_ke_mql5", lambda m, t: []):
            r = CK.tai_mql5(d, so_trang=1, trang_dau=9, nghi_giay=0, in_ra=lambda *_: None)
        self.assertEqual(r.get("het_trang"), 1)
        self.assertNotIn("loi_trang", r)

    def test_bai_hong_thu_lai_sau_n_gio(self):
        ds = [{"id": "12", "url": "https://www.mql5.com/en/code/12", "tieu_de": "Hong",
               "muc": "experts"}]
        goi = []

        def tai(b):
            goi.append(b["id"])
            return None if len(goi) == 1 else {"ten_file": "x.mq5", "noi_dung": EA,
                                               "so_byte": len(EA)}
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(MN, "liet_ke_mql5", lambda m, t: ds), \
                mock.patch.object(MN, "tai_ma_nguon", tai):
            CK.tai_mql5(d, so_trang=1, nghi_giay=0, in_ra=lambda *_: None)
            r2 = CK.tai_mql5(d, so_trang=1, nghi_giay=0, in_ra=lambda *_: None)
            self.assertEqual(goi, ["12"])                 # chua toi han: khong thu lai
            self.assertEqual(r2["da_co"], 1)
            pm = Path(d) / "NGUON_TAI.json"
            man = json.loads(pm.read_text(encoding="utf-8"))
            self.assertFalse(man["12"]["ok"])
            self.assertEqual(man["12"]["so_lan_hong"], 1)
            cu = time.time() - (CK.THU_LAI_GIO + 1) * 3600
            man["12"]["luc"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cu))
            pm.write_text(json.dumps(man), encoding="utf-8")
            r3 = CK.tai_mql5(d, so_trang=1, nghi_giay=0, in_ra=lambda *_: None)
            self.assertEqual(goi, ["12", "12"])
            self.assertEqual(r3.get("thu_lai"), 1)
            self.assertEqual(r3.get("moi"), 1)
            self.assertTrue(json.loads(pm.read_text(encoding="utf-8"))["12"]["ok"])

    def test_ban_ghi_hong_cu_khong_luc_thu_lai_ngay(self):
        self.assertTrue(CK._den_luot_thu_lai({"ok": False}))
        self.assertFalse(CK._den_luot_thu_lai({"ok": True, "luc": "2020-01-01 00:00:00"}))


class ConTro(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.T = _tru(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def _ct(self):
        p = Path(self.td.name) / "TRANG_SAU.json"
        return json.loads(p.read_text())["trang"] if p.exists() else None

    def test_mang_hong_con_tro_dung_yen(self):
        (Path(self.td.name)).mkdir(exist_ok=True)
        (Path(self.td.name) / "TRANG_SAU.json").write_text(json.dumps({"trang": 7}))
        goi = []

        def gia(thu_muc, so_trang=1, trang_dau=1, **k):
            goi.append(trang_dau)
            return {"trang": 1, "loi_trang": 1, "trang_loi": [trang_dau]}
        ra = self.T.mot_luot(tai_mql5=gia, gom_tu_so=lambda: [])
        ra2 = self.T.mot_luot(tai_mql5=gia, gom_tu_so=lambda: [])
        self.assertEqual(goi, [1, 7, 1, 7])               # thu lai DUNG trang 7
        self.assertEqual(self._ct(), 7)
        self.assertEqual(ra["tai"]["con_tro"]["ly_do"], "loi_trang")
        self.assertIn("canh_bao", ra2["tai"])

    def test_mql5_that_hong_qua_tai_mql5_that(self):
        """Duong day du: _lay hong -> liet_ke None -> tai_mql5 loi_trang -> con tro yen."""
        (Path(self.td.name) / "TRANG_SAU.json").write_text(json.dumps({"trang": 5}))
        with mock.patch.object(MN, "_lay", return_value=None):
            ra = self.T.mot_luot(gom_tu_so=lambda: [])
        self.assertEqual(self._ct(), 5)
        self.assertEqual(ra["tai"]["trang_5"].get("loi_trang"), 1)

    def test_het_trang_that_ve_2(self):
        (Path(self.td.name) / "TRANG_SAU.json").write_text(json.dumps({"trang": 33}))
        self.T.mot_luot(tai_mql5=lambda *a, **k: {"trang": 1, "het_trang": 1},
                        gom_tu_so=lambda: [])
        self.assertEqual(self._ct(), 2)

    def test_het_gio_dung_yen(self):
        self.assertEqual(self.T.buoc_con_tro({"het_gio": 1, "thay": 5}, 4)["trang_moi"], 4)
        self.assertEqual(self.T.buoc_con_tro({"thay": 5}, 4)["trang_moi"], 5)
        self.assertEqual(self.T.buoc_con_tro({"thay": 5}, self.T.TRANG_TOI_DA)["trang_moi"], 2)


if __name__ == "__main__":
    unittest.main()
