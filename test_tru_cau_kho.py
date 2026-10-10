# -*- coding: utf-8 -*-
"""TRU CAUKHO (11/10/2026): cau kho ma chay dinh ky trong `dieu_phoi`, khong can
`nao.db` co du lieu, khong can mang de do lai kho dang co.

Kiem: (1) dang ky trong `dieu_phoi.TRU` voi lane rieng va ngan sach co tran;
(2) mang hong -> `tai.loi` (suy giam) ma van do kho; (3) bo nho dem theo van tay +
phien ban bo doc cho so GIONG HET doc lai; (4) `tai_mql5` dung khi het `han_giay`;
(5) con tro trang sau tien len khi trang sau tai xong.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAB = Path(__file__).resolve().parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

import dieu_phoi as DP                      # noqa: E402
from nhan import cau_kho_ma as CK          # noqa: E402
from nhan import ma_nguon as MN            # noqa: E402
from test_cau_kho_ma import EA            # noqa: E402

EA_HAM = EA.replace("""   if(r[0] < 30)
   {
      trade.Buy(0.1);
   }
}""", """   if(r[0] < 30)
      MoMua();
}
void MoMua()
{
   trade.Buy(0.1);
}""")


def _tru(thu_muc: str):
    with mock.patch.dict(os.environ, {"BRAIN_CAU_KHO_DIR": thu_muc,
                                      "BRAIN_CAU_KHO_GIAY_TAI": "30"}):
        import tru.cau_kho as T
        return importlib.reload(T)


class DangKy(unittest.TestCase):
    def test_trong_dieu_phoi_lane_rieng_co_tran(self):
        c = DP.TRU["CAUKHO"]
        self.assertEqual(c["script"], "tru/cau_kho.py")
        self.assertTrue((LAB / c["script"]).exists())
        self.assertIn(c["lan"], DP.LAN_GIOI_HAN)
        self.assertNotEqual(c["lan"], DP.TRU["SEEKER"]["lan"])
        self.assertLessEqual(c["ngan_sach"], DP.TRU["SEEKER"]["ngan_sach"])
        self.assertGreaterEqual(c["chu_ky"], 3600)


class MotLuot(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.T = _tru(self.td.name)
        kho = Path(self.td.name) / "mql5"
        kho.mkdir(parents=True)
        (kho / "1_a.mq5").write_text(EA, encoding="utf-8")
        (kho / "2_b.mq5").write_text(EA_HAM, encoding="utf-8")

    def tearDown(self):
        self.td.cleanup()

    def test_mang_hong_van_do_kho(self):
        def hong(*a, **k):
            raise OSError("mang hong")
        r = self.T.mot_luot(tai_mql5=hong, gom_tu_so=lambda: [])
        self.assertIn("loi", r["tai"])
        self.assertEqual(r["so"]["vao_lenh"], 2)
        # ham phu `MoMua()` goi tu `if(r[0] < 30)` duoc nang len cho goi
        self.assertEqual(r["so"]["vao_co"], 2)
        self.assertTrue((Path(self.td.name) / "BAO_CAO.md").exists())
        self.assertTrue((Path(self.td.name) / "ea_ra_co_che" / "NGUON.json").exists())
        dong = (Path(self.td.name) / "lich_su.jsonl").read_text().strip().splitlines()
        self.assertEqual(json.loads(dong[-1])["ty_le_dich"], 1.0)

    def test_bo_nho_cho_so_giong_doc_lai(self):
        khong = lambda *a, **k: {}               # noqa: E731
        r1 = self.T.mot_luot(tai_mql5=khong, gom_tu_so=lambda: [])
        r2 = self.T.mot_luot(tai_mql5=khong, gom_tu_so=lambda: [])
        self.assertEqual(r2["pheu"].get("tu_bo_nho"), 2)
        self.assertEqual(r1["so"], r2["so"])
        bg = CK.gom_tu_thu_muc(Path(self.td.name) / "mql5")
        self.assertEqual(CK.do_kho(bg)["so"], r2["so"])

    def test_con_tro_trang_sau_tien_len(self):
        goi = []

        def gia(thu_muc, so_trang=1, trang_dau=1, **k):
            goi.append(trang_dau)
            return {"trang": 1}
        self.T.mot_luot(tai_mql5=gia, gom_tu_so=lambda: [])
        self.T.mot_luot(tai_mql5=gia, gom_tu_so=lambda: [])
        self.assertEqual(goi, [1, 2, 1, 3])
        ct = json.loads((Path(self.td.name) / "TRANG_SAU.json").read_text())
        self.assertEqual(ct["trang"], 4)


class HanGio(unittest.TestCase):
    def test_tai_mql5_dung_khi_het_gio(self):
        ds = [{"id": str(i), "url": "u%d" % i, "tieu_de": "t%d" % i, "muc": "experts"}
              for i in range(5)]
        da_tai = []

        def tai(b):
            da_tai.append(b["id"])
            return {"ten_file": "x.mq5", "noi_dung": EA, "so_byte": len(EA)}
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(MN, "liet_ke_mql5", lambda muc, trang: ds), \
                mock.patch.object(MN, "tai_ma_nguon", tai):
            r = CK.tai_mql5(td, so_trang=3, nghi_giay=0, in_ra=lambda *_: None,
                            han_giay=1e-9)
        self.assertEqual(da_tai, [])
        self.assertGreaterEqual(r.get("het_gio", 0), 1)


if __name__ == "__main__":
    unittest.main()
