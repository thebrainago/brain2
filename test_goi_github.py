# -*- coding: utf-8 -*-
"""Nguon GitHub cho cau kho (11/10/2026, `nhan/goi_github.py`): khong mang trong test.

Kiem: (1) ghep `.set` theo quy tac cau truc (ten bat dau bang ten EA / cung thu muc khi thu
muc co DUNG MOT .mq5) - ca ca PHAI tu choi; (2) mot luot tao goi chi cho file co OnTick, kem
.mqh khi EA include ngoai, GOI.json co url/revision github; (3) search 403 -> dung, khong quay
vong; (4) repo khong doi `pushed_at` khong ton luot lai; (5) tru CAUKHO doc kho goi_github va
`set_cua_goi` nhan DUNG MOT .set.
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

from nhan import cau_kho_ma as CK          # noqa: E402
from nhan import goi_github as GG          # noqa: E402
from test_cau_kho_ma import EA             # noqa: E402

CHI_BAO = "#property indicator_chart_window\nint OnCalculate(const int a){return a;}\n"
EA_INC = '#include "Helper.mqh"\n' + EA


def _gia(tree: dict, tep: dict, search_loi: str | None = None):
    goi = {"search": 0, "tree": 0}

    def get(url, params=None, j=True):
        if "/search/repositories" in url:
            goi["search"] += 1
            if search_loi:
                return None, search_loi
            return {"items": [{"full_name": fn, "name": fn.split("/")[1], "description": "EA",
                               "default_branch": "main", "pushed_at": "2026-10-01",
                               "stargazers_count": 1} for fn in tree]}, None
        if "/git/trees/" in url:
            goi["tree"] += 1
            fn = url.split("/repos/")[1].split("/git/")[0]
            return {"tree": [{"type": "blob", "path": p, "size": 100} for p in tree[fn]]}, None
        for (fn, p), vb in tep.items():
            if url.endswith("/%s/main/%s" % (fn, p)):
                return vb.encode("utf-8"), None
        return None, "HTTP 404"
    return get, goi


class GhepSet(unittest.TestCase):
    def test_ten_bat_dau_bang_ten_ea(self):
        self.assertEqual(GG.ghep_set("src/MyEA.mq5", ["src/MyEA.mq5", "src/B.mq5"],
                                     ["sets/myea_eurusd_m5.set", "sets/B.set"]),
                         ["sets/myea_eurusd_m5.set"])

    def test_cung_thu_muc_mot_mq5(self):
        self.assertEqual(GG.ghep_set("x/A.mq5", ["x/A.mq5", "y/B.mq5"], ["x/cfg.set"]),
                         ["x/cfg.set"])

    def test_tu_choi_cung_thu_muc_nhieu_mq5(self):
        # thu muc co hai EA, ten .set khong chi ro EA nao -> KHONG gan
        self.assertEqual(GG.ghep_set("x/A.mq5", ["x/A.mq5", "x/B.mq5"], ["x/cfg.set"]), [])

    def test_tu_choi_khac_thu_muc_khac_ten(self):
        self.assertEqual(GG.ghep_set("x/A.mq5", ["x/A.mq5"], ["z/other.set"]), [])


class MotLuot(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def test_tao_goi_chi_cho_ea(self):
        tree = {"u/r": ["EA1.mq5", "Ind.mq5", "Helper.mqh", "EA1_eurusd.set", "README.md"]}
        tep = {("u/r", "EA1.mq5"): EA_INC, ("u/r", "Ind.mq5"): CHI_BAO,
               ("u/r", "Helper.mqh"): "int H(){return 1;}\n",
               ("u/r", "EA1_eurusd.set"): "InpLots=0.1\n"}
        get, _ = _gia(tree, tep)
        r = GG.tai_github_goi(self.d, han_giay=60, get=get, nghi_giay=0, in_ra=lambda *_: None)
        self.assertEqual(r["ea_moi"], 1)
        self.assertEqual(r["ea_co_set"], 1)
        goi = [p for p in self.d.iterdir() if p.is_dir()]
        self.assertEqual(len(goi), 1)
        ten = sorted(p.name for p in goi[0].iterdir())
        self.assertEqual(ten, ["EA1.mq5", "EA1_eurusd.set", "GOI.json", "Helper.mqh"])
        meta = json.loads((goi[0] / "GOI.json").read_text(encoding="utf-8"))
        self.assertTrue(meta["url"].startswith("https://github.com/u/r/blob/main/"))
        self.assertTrue(meta["revision"].startswith("github-u/r@"))
        ten_set, _ = CK.set_cua_goi("tep:%s" % (goi[0] / "EA1.mq5"))
        self.assertEqual(ten_set, "EA1_eurusd.set")
        self.assertEqual(CK.tep_thieu_that(EA_INC, "tep:%s" % (goi[0] / "EA1.mq5")), [])

    def test_search_403_dung(self):
        get, goi = _gia({"u/r": ["EA1.mq5"]}, {}, search_loi="HTTP 403")
        r = GG.tai_github_goi(self.d, han_giay=60, get=get, nghi_giay=0, in_ra=lambda *_: None)
        self.assertEqual(goi["search"], 1)
        self.assertEqual(goi["tree"], 0)
        self.assertIn("search:HTTP 403", r["loi"])

    def test_repo_khong_doi_khong_ton_luot(self):
        get, goi = _gia({"u/r": ["EA1.mq5"]}, {("u/r", "EA1.mq5"): EA})
        GG.tai_github_goi(self.d, han_giay=60, get=get, nghi_giay=0, in_ra=lambda *_: None)
        GG.tai_github_goi(self.d, han_giay=60, get=get, nghi_giay=0, in_ra=lambda *_: None)
        self.assertEqual(goi["tree"], 1)


class TruCauKho(unittest.TestCase):
    def test_tru_doc_kho_github(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict(os.environ, {"BRAIN_CAU_KHO_DIR": td,
                                              "BRAIN_DIEU_TOC": "tat"}):
                import tru.cau_kho as T
                T = importlib.reload(T)
                tree = {"u/r": ["EA1.mq5"]}
                get, _ = _gia(tree, {("u/r", "EA1.mq5"): EA})
                r = T.mot_luot(tai_mql5=lambda *a, **k: {}, gom_tu_so=lambda: [],
                               tai_github=lambda kho, **k: GG.tai_github_goi(
                                   kho, get=get, nghi_giay=0, in_ra=lambda *_: None))
            self.assertEqual(r["tai"]["github"]["ea_moi"], 1)
            self.assertEqual(r["so"]["vao_lenh"], 1)
            ng = json.loads((Path(td) / "ea_ra_co_che" / "NGUON.json").read_text("utf-8"))
            self.assertIn("github.com/u/r", json.dumps(ng))


if __name__ == "__main__":
    unittest.main()
