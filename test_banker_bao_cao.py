# -*- coding: utf-8 -*-
"""Test banker_bao_cao/tai_bao_cao.py (không dùng mạng)."""
import importlib.util
import json
import os
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "tai_bao_cao", os.path.join(os.path.dirname(os.path.abspath(__file__)), "banker_bao_cao", "tai_bao_cao.py"))
tbc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tbc)


class TestTaiBaoCao(unittest.TestCase):
    def test_ten_tep(self):
        self.assertEqual(tbc.ten_tep("https://x.com/a/FAFIXINC.pdf"), "FAFIXINC")

    def test_chi_muc_khong_trung(self):
        with tempfile.TemporaryDirectory() as d:
            tbc.ghi_chi_muc(d, {"url": "u1", "ngay": "1"})
            tbc.ghi_chi_muc(d, {"url": "u1", "ngay": "2"})
            ds = tbc.ghi_chi_muc(d, {"url": "u2"})
            self.assertEqual(len(ds), 2)
            with open(os.path.join(d, "nguon.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)[0]["ngay"], "2")


if __name__ == "__main__":
    unittest.main()
