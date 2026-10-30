# -*- coding: utf-8 -*-
"""Tests for tools/vong2.py — round-2 job generator."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))

spec = importlib.util.spec_from_file_location("tools_vong2", GOC / "tools" / "vong2.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class TestVong2Tools(unittest.TestCase):
    def test_parse_dd(self):
        self.assertEqual(V._parse_dd_pct("1234.5 (17.85%)"), 17.85)
        self.assertEqual(V._parse_dd_pct(9.56), 9.56)
        self.assertIsNone(V._parse_dd_pct(None))

    def test_apy_years(self):
        y = V._years("2025.01.30 - 2026.06.03")
        self.assertIsNotNone(y)
        self.assertGreater(y, 1.0)
        self.assertLess(y, 2.0)
        a = V._apy(5278.59, 10000, y)
        self.assertGreater(a, 30)
        self.assertLess(a, 50)

    def test_ma_hash(self):
        self.assertEqual(V._ma_hash("EURUSD"), "EURUSD#")
        self.assertEqual(V._ma_hash("EURUSDmicro"), "EURUSD#")
        self.assertEqual(V._ma_hash("EURUSD#"), "EURUSD#")
        self.assertEqual(V._ma_hash("XAUUSDmicro"), "GOLD.i#")

    def test_ten_v2_short(self):
        t = V._ten_v2("od_skst299b0817f66d4096_XM_CSV", "p", "tp80")
        self.assertTrue(t.startswith("od_v2r2"))
        self.assertLessEqual(len(t), 60)
        self.assertIn("XM_CSV", t)

    def test_bien_the_tham_so(self):
        goc = {
            "ten": "od_demo_XM_CSV",
            "ma": "EURUSD#",
            "tf": "H1",
            "ts": {
                "InpVao": 4, "InpTF": 16385, "InpTPPct": 1.5, "InpBuocPct": 0.8,
                "InpHeSoLot": 1.4, "InpMaxTang": 5, "InpLot0": 0.02,
                "InpGioCamTu": 23, "InpGioCamDen": 2, "InpFileCsv": "x.csv",
            },
            "python_ql": {
                "tp_pct": 1.5, "dca_buoc_pct": 0.8, "dca_he_so_lot": 1.4,
                "dca_toi_da": 5, "lot_tren_1000": 0.02,
            },
            "tu": "2022.01.01", "den": "2026.06.01", "von": 10000,
        }
        ds = V.bien_the_tham_so(goc, "od_demo")
        self.assertGreaterEqual(len(ds), 8)
        for v in ds:
            self.assertEqual(v["vong"], 2)
            self.assertEqual(v["pha"], "V2_ROBUST")
            self.assertEqual(v["vong2_loai"], "tham_so")

    def test_csv_skip_cross_symbol(self):
        goc = {"ten": "od_demo", "ma": "EURUSD#", "tf": "H1",
               "ts": {"InpVao": 4, "InpTF": 16385}, "python_ql": {}}
        self.assertEqual(V.bien_the_cap(goc, "od_demo"), [])

    def test_indicator_cross_symbol(self):
        goc = {"ten": "od_demo", "ma": "EURUSD#", "tf": "H1",
               "ts": {"InpVao": 1, "InpTF": 16385}, "python_ql": {}}
        ds = V.bien_the_cap(goc, "od_demo", toi_da=3)
        self.assertEqual(len(ds), 3)
        self.assertTrue(all(v["pha"] == "V2_DA_CAP" for v in ds))

    def test_oos_and_tf(self):
        goc = {"ten": "od_demo", "ma": "EURUSD#", "tf": "H1",
               "ts": {"InpVao": 4, "InpTF": 16385, "InpCsvTreGiay": 3600},
               "python_ql": {}, "tu": "2024.01.01", "den": "2026.06.01"}
        oos = V.bien_the_oos(goc, "od_demo")
        self.assertGreaterEqual(len(oos), 2)
        self.assertTrue(all(v["pha"] == "V2_OOS" for v in oos))
        tf = V.bien_the_khung(goc, "od_demo")
        self.assertEqual({v["tf"] for v in tf}, {"M30", "H4"})
        self.assertEqual(tf[0]["ts"]["InpTF"], 30)

    def test_ghi_hang_cho_merge(self):
        with tempfile.TemporaryDirectory() as d:
            tep = Path(d) / "h.jsonl"
            a = [{"ten": "a", "vong": 2, "vong2_loai": "tham_so", "pha": "V2_ROBUST"}]
            b = [{"ten": "b", "vong": 2, "vong2_loai": "oos", "pha": "V2_OOS"},
                 {"ten": "a", "vong": 2, "vong2_loai": "tham_so", "pha": "V2_ROBUST", "diem": 99}]
            V.ghi_hang_cho(a, tep=tep, thay_the=True)
            n = V.ghi_hang_cho(b, tep=tep, thay_the=False)
            self.assertEqual(n, 2)
            rows = [json.loads(x) for x in tep.read_text().splitlines()]
            by = {r["ten"]: r for r in rows}
            self.assertEqual(by["a"]["diem"], 99)

    def test_chon_passers_filter(self):
        # Smoke: returns list (may be empty if no ledgers, but we have them)
        ps = V.chon_passers()
        self.assertIsInstance(ps, list)
        if ps:
            self.assertGreater(ps[0]["net"], 0)
            self.assertLessEqual(ps[0]["dd_pct"], 80)


if __name__ == "__main__":
    unittest.main()
