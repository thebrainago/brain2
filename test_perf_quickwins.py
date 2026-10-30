# -*- coding: utf-8 -*-
"""Perf quick-wins (evo/perf-quickwins): poll MT5 thich ung, chu ky EVO/CAUKHO
thich ung, index noi_dung(kieu). Mac dinh cu van dat duoc qua bien moi truong.
"""
from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAB = Path(__file__).resolve().parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

import dieu_phoi as DP  # noqa: E402


class PollMt5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(LAB / "mt5tools"))
        import chay_lien_tuc as CLT  # noqa: E402
        cls.CLT = CLT

    def test_mac_dinh_ban_3_ranh_15(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in ("BRAIN_MT5_POLL_BAN", "BRAIN_MT5_POLL_RANH"):
                os.environ.pop(k, None)
            self.assertEqual(self.CLT._poll_giay(True), 3.0)
            self.assertEqual(self.CLT._poll_giay(False), 15.0)

    def test_cau_hinh_kep_tran(self):
        with mock.patch.dict(os.environ, {"BRAIN_MT5_POLL_BAN": "1.5",
                                          "BRAIN_MT5_POLL_RANH": "30"}):
            self.assertEqual(self.CLT._poll_giay(True), 1.5)
            self.assertEqual(self.CLT._poll_giay(False), 30.0)
        with mock.patch.dict(os.environ, {"BRAIN_MT5_POLL_BAN": "0.01"}):
            self.assertEqual(self.CLT._poll_giay(True), 0.5)  # san
        with mock.patch.dict(os.environ, {"BRAIN_MT5_POLL_RANH": "999"}):
            self.assertEqual(self.CLT._poll_giay(False), 120.0)  # tran


class ChuKyEvo(unittest.TestCase):
    def test_nang_thi_ngan_mac_900(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in ("BRAIN_EVO_CHU_KY_NANG", "BRAIN_EVO_CHU_KY_NHE"):
                os.environ.pop(k, None)
            with mock.patch.object(DP, "_co_van_de_nang", return_value=True):
                self.assertEqual(DP.chu_ky_hien_tai("EVO"), 900)

    def test_khong_nang_thi_30_60_phut(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in ("BRAIN_EVO_CHU_KY_NANG", "BRAIN_EVO_CHU_KY_NHE"):
                os.environ.pop(k, None)
            with mock.patch.object(DP, "_co_van_de_nang", return_value=False):
                v = DP.chu_ky_hien_tai("EVO")
                self.assertGreaterEqual(v, 1800)
                self.assertLessEqual(v, 3600)
                self.assertEqual(v, 2700)

    def test_cau_hinh_nhe(self):
        with mock.patch.dict(os.environ, {"BRAIN_EVO_CHU_KY_NHE": "3600"}):
            with mock.patch.object(DP, "_co_van_de_nang", return_value=False):
                self.assertEqual(DP.chu_ky_hien_tai("EVO"), 3600)

    def test_tru_khac_khong_doi(self):
        self.assertEqual(DP.chu_ky_hien_tai("SEEKER"), DP.TRU["SEEKER"]["chu_ky"])
        self.assertEqual(DP.chu_ky_hien_tai("QUANTLAB"), DP.TRU["QUANTLAB"]["chu_ky"])


class ChuKyCaukho(unittest.TestCase):
    def test_TRU_mac_dinh_van_6h(self):
        # Hang so TRU khong doi - test_tru_cau_kho van pass
        self.assertGreaterEqual(DP.TRU["CAUKHO"]["chu_ky"], 3600)
        self.assertEqual(DP.TRU["CAUKHO"]["chu_ky"], 6 * 3600)

    def test_con_hang_thi_ngan(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BRAIN_CAUKHO_CHU_KY_BAN", None)
            with mock.patch.object(DP, "_caukho_con_hang", return_value=True):
                self.assertEqual(DP.chu_ky_hien_tai("CAUKHO"), 900)

    def test_ranh_thi_6h(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BRAIN_CAUKHO_CHU_KY_RANH", None)
            with mock.patch.object(DP, "_caukho_con_hang", return_value=False):
                self.assertEqual(DP.chu_ky_hien_tai("CAUKHO"), 6 * 3600)

    def test_caukho_con_hang_doc_TRANG_SAU(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict(os.environ, {"BRAIN_CAU_KHO_DIR": td}):
                # chua co file -> con hang
                self.assertTrue(DP._caukho_con_hang())
                p = Path(td) / "TRANG_SAU.json"
                p.write_text(json.dumps({"trang": 5, "ly_do": "ok"}), encoding="utf-8")
                self.assertTrue(DP._caukho_con_hang())
                p.write_text(json.dumps({"trang": 2, "ly_do": "het_trang"}), encoding="utf-8")
                self.assertFalse(DP._caukho_con_hang())
                p.write_text(json.dumps({"trang": 60, "ly_do": "toi_da"}), encoding="utf-8")
                self.assertFalse(DP._caukho_con_hang())


class IndexNoiDungKieu(unittest.TestCase):
    def test_schema_co_ix_nd_kieu(self):
        from nhan import so as SO
        self.assertIn("ix_nd_kieu", SO.SCHEMA)
        self.assertIn("CREATE INDEX IF NOT EXISTS ix_nd_kieu ON noi_dung(kieu)", SO.SCHEMA)

    def test_khoi_tao_idempotent(self):
        from nhan import so as SO
        td = tempfile.TemporaryDirectory()
        db_cu = SO.DB
        try:
            SO.DB = Path(td.name) / "nao.db"
            SO.khoi_tao()
            SO.khoi_tao()  # lan 2 khong loi (IF NOT EXISTS)
            with sqlite3.connect(SO.DB) as cn:
                idx = {r[1] for r in cn.execute("PRAGMA index_list(noi_dung)")}
            self.assertIn("ix_nd_kieu", idx)
            self.assertIn("ix_nd_boc", idx)
        finally:
            SO.DB = db_cu
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
