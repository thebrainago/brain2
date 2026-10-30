# -*- coding: utf-8 -*-
import importlib.util, tempfile, unittest
from pathlib import Path
GOC = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hoc", GOC / "tools" / "hoc_tu_so_cai.py")
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)

class TestHoc(unittest.TestCase):
    def test_fam_and_pass(self):
        self.assertEqual(H._fam("od_skst299b0817_XM_CSV"), "skst")
        self.assertEqual(H._ma_chuan("EURUSDmicro"), "EURUSD")
        r = {"net": 250, "dd": "10 (5%)", "von": 1000,
             "ky_bc": "H1 (2024.01.01 - 2025.01.01)", "loi": None, "ten": "od_skst_x"}
        self.assertEqual(H._nhan_pass(r), "pass")
        r2 = {"net": -1, "dd": "10 (5%)", "von": 1000, "loi": None, "ten": "x"}
        self.assertEqual(H._nhan_pass(r2), "fail")

    def test_chay_smoke(self):
        kq = H.chay()
        self.assertTrue(Path(kq["json"]).exists())
        self.assertTrue(Path(kq["md"]).exists())
        self.assertGreater(kq["n_dong"], 0)

if __name__ == "__main__":
    unittest.main()
