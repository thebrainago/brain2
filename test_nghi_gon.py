# -*- coding: utf-8 -*-
"""NGHI prompt gon: go HTML + size cap truoc khi dua tai lieu / da_co vao loi nhac."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAB = str(Path(__file__).resolve().parent)
if LAB not in sys.path:
    sys.path.insert(0, LAB)

from nhan import so as SO
from tru import nghi as NGHI


HTML_MAU = """<!DOCTYPE html><html><head><style>body{color:red}</style>
<script>alert(1)</script></head><body>
<article><h1>Mean reversion sau tin</h1>
<p>Khi ATR phan vi cao va RSI duoi 30, can nhac mua. Edge den tu mean reversion.</p>
</article></body></html>"""


class NghiGon(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._db_cu = SO.DB
        SO.DB = Path(self._tmp.name) / "nao_test.db"
        SO.khoi_tao()

    def tearDown(self):
        SO.DB = self._db_cu
        self._tmp.cleanup()

    def test_gon_van_ban_bo_script_style_giu_text(self):
        gon = NGHI._gon_van_ban_tai_lieu(HTML_MAU, url="https://example.com/x")
        self.assertNotIn("<script", gon.lower())
        self.assertNotIn("<style", gon.lower())
        self.assertNotIn("alert(", gon)
        self.assertIn("Mean reversion", gon)
        self.assertIn("ATR", gon)
        self.assertLess(len(gon), len(HTML_MAU))

    def test_doc_tai_lieu_cat_theo_tran(self):
        # chen tai lieu + noi dung HTML dai
        vt = SO.van_tay("nghi_gon", "https://ex/1")
        with SO.ket_noi() as cn:
            cn.execute(
                "INSERT INTO tai_lieu(van_tay,nguon,loai,tieu_de,url,tom_tat,tu_khoa,diem,da_khai_thac) "
                "VALUES(?,?,?,?,?,?,?,?,0)",
                (vt, "test", "web", "Bai HTML", "https://ex/1", "tom tat", "A", 9.0))
            tid = cn.execute("SELECT id FROM tai_lieu ORDER BY id DESC LIMIT 1").fetchone()[0]
            dai = HTML_MAU + (" them van ban huu ich." * 800)
            cn.execute(
                "INSERT INTO noi_dung(tai_lieu_id,van_tay,url,kieu,cach,so_ky_tu,van_ban) "
                "VALUES(?,?,?,?,?,?,?)",
                (tid, vt + "_nd", "https://ex/1", "html", "test", len(dai), dai))
        rows = NGHI.doc_tai_lieu(n=3)
        self.assertTrue(rows)
        vb = rows[0]["van_ban"]
        self.assertLessEqual(len(vb), NGHI.TRAN_VAN_BAN_MOT)
        self.assertNotIn("<script", vb.lower())
        self.assertTrue(rows[0]["van_ban_goc_ky_tu"] > rows[0]["van_ban_gon_ky_tu"]
                        or rows[0]["van_ban_gon_ky_tu"] <= NGHI.TRAN_VAN_BAN_MOT)

    def test_nhac_cap_da_co_va_prompt_nho_hon_120kb(self):
        # gia da_co rat dai
        fake_ten = [f"co_che_gia_{i:04d}_" + ("x" * 20) for i in range(5000)]
        with mock.patch.object(NGHI, "MAU") as m_mau, \
             mock.patch.object(NGHI.NP, "doc_kho", return_value=[]):
            m_mau.MAU = {t: {} for t in fake_ten}
            # MAU.MAU is used as list(MAU.MAU) — make it a dict-like
            class _M:
                MAU = {t: 1 for t in fake_ten}
            # patch module-level MAU used inside _nhac
            import tru.nghi as nghi_mod
            cu = nghi_mod.MAU
            nghi_mod.MAU = _M
            try:
                dc = {"_tu_choi": [], "_da_kiem": []}
                tl = [{"tu_khoa": "A", "tieu_de": "t", "url": "u",
                       "tom_tat": "tt", "van_ban": HTML_MAU * 3}]
                # preprocess like doc_tai_lieu would
                tl[0]["van_ban"] = NGHI._gon_van_ban_tai_lieu(tl[0]["van_ban"])[:NGHI.TRAN_VAN_BAN_MOT]
                nhac = NGHI._nhac(dc, tl)
            finally:
                nghi_mod.MAU = cu
        self.assertLess(len(nhac.encode("utf-8")), 80_000,
                        f"prompt van qua lon: {len(nhac)} ky tu")
        self.assertIn("ten khac", nhac)
        self.assertNotIn("<script", nhac.lower())


if __name__ == "__main__":
    unittest.main()
