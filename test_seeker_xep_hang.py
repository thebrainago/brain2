# -*- coding: utf-8 -*-
"""11/10/2026: goi MQL5 (.mq5+.mqh+.set), truy van, xep hang, dieu toc, Telegram cong khai."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from nhan import cau_kho_ma as CK               # noqa: E402
from nhan import dieu_toc as DT                 # noqa: E402
from nhan import ma_nguon as MN                 # noqa: E402
from nhan import tg_cong_khai as TGC            # noqa: E402
from nhan import truy_van_seeker as TV          # noqa: E402
from nhan import xep_hang_ung_vien as XH        # noqa: E402
from test_cau_kho_ma import EA                  # noqa: E402

HTML = ('<a href="/en/code/download/77738/RSI_Rev.mq5">a</a>'
        '<a href="/en/code/download/77738/RSI_Rev_EURUSD.set">b</a>'
        '<a href="/en/code/download/77738/Lib.mqh">c</a>'
        '<a href="/en/code/download/77738/TesterResults.png">d</a>'
        '<a href="/en/code/download/77738.zip">z</a>'
        '<a href="/en/code/download/99999/khac.mq5">x</a>')
QUAN_TRI = """#include <Trade/Trade.mqh>
CTrade trade;
input double TrailPoints=100;
void OnTick(){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i);
 double sl=PositionGetDouble(POSITION_SL); trade.PositionModify(t,sl+TrailPoints*_Point,0);} }
""" + "//" + "x" * 300


class GoiMql5(unittest.TestCase):
    def test_liet_ke_tep_bai(self):
        d = MN.liet_ke_tep_bai(HTML, "77738")
        self.assertEqual(d["tep"], ["RSI_Rev.mq5", "RSI_Rev_EURUSD.set", "Lib.mqh"])
        self.assertTrue(d["co_zip"])
        self.assertEqual(d["anh"], ["TesterResults.png"])

    def test_tai_goi_xep_bai_theo_tieu_de_va_ghi_goi(self):
        ds = [{"id": "1", "url": "u1", "tieu_de": "Margin Risk Auditor panel", "muc": "experts"},
              {"id": "2", "url": "u2", "tieu_de": "RSI reversal strategy with .set", "muc": "experts"}]
        tep = {"1": {"A.mq5": QUAN_TRI}, "2": {"B.mq5": EA, "B_EURUSD.set": "Lots=0.1\nRSIPeriod=14||14||1||28||Y\n"}}
        goi = []

        def tai(b, nghi_giay=0):
            goi.append(b["id"])
            return {**b, "tep": tep[b["id"]], "co_zip": False, "anh": [], "anh_ket_qua": [], "bo": []}
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(MN, "liet_ke_mql5", lambda *a, **k: ds), \
                mock.patch.object(MN, "tai_goi_ma_nguon", tai):
            r = CK.tai_mql5_goi(td, nghi_giay=0, in_ra=lambda *_: None, toi_da_bai=1)
            self.assertEqual(goi, ["2"])               # bai chien luoc + .set tai truoc
            self.assertEqual(r["co_set"], 1)
            self.assertTrue((Path(td) / "2" / "B_EURUSD.set").exists())
            self.assertTrue(json.loads((Path(td) / "2" / "GOI.json").read_text())["tep"])
            # luot sau: bai 2 da co, lay bai 1
            CK.tai_mql5_goi(td, nghi_giay=0, in_ra=lambda *_: None)
            self.assertEqual(goi, ["2", "1"])


class TruyVan(unittest.TestCase):
    def test_tach_tu_va_set(self):
        self.assertEqual(TV.tach_tu("RSI_Exhaustion_Reversal_EURUSD.set"),
                         ["rsi", "exhaustion", "reversal"])
        self.assertEqual(TV.doc_set("; c\nGridStep=200||100||1||400||N\nLotMultiplier=1.5\n"),
                         {"GridStep": "200", "LotMultiplier": "1.5"})
        self.assertEqual(TV.tu_khoa_set(["GridStep", "LotMultiplier"]), ["grid", "martingale"])

    def test_sinh_hat_giong_truoc_roi_tu_dao(self):
        ds = TV.sinh([{"ten": "SuperTrend_Breakout.mq5", "hang": "A", "tep_set": ["x.set"],
                       "khoa_set": ["GridStep"], "ho": []}])
        self.assertEqual(ds[0]["nguon"], "hat_giong")
        self.assertTrue(any(x.get("tu") == "breakout" for x in ds))
        self.assertTrue(any(x.get("tu") == "grid" for x in ds))

    def test_khop_dinh_kem_set_manh_nhat(self):
        a = TV.khop("New EA free", [{"ten": "Gold_EA.set"}, {"ten": "Gold_EA.mq5"}])
        b = TV.khop("mt5 ea set file shared", [])
        self.assertTrue(a["co_set"] and a["co_ma"])
        self.assertGreater(a["diem"], b["diem"])
        self.assertEqual(TV.khop("hello world", [])["diem"], 0)


class XepHang(unittest.TestCase):
    def test_goi_co_set_tren_khong_set_quan_tri_cuoi_mql4_lan_rieng(self):
        with tempfile.TemporaryDirectory() as td:
            for ten, src, sets in (("a", EA, {"a.set": "RSIPeriod=14\n"}), ("b", EA.replace("30", "25"), {}),
                                   ("c", QUAN_TRI, {}),
                                   ("d", "int start(){ OrderSend(Symbol(),OP_BUY,1,Ask,3,0,0); return 0;}" + "/" * 300,
                                    {"d.set": "x=1\n"})):
                g = Path(td) / ten
                g.mkdir()
                (g / (ten + (".mq4" if ten == "d" else ".mq5"))).write_text(src)
                for s, v in sets.items():
                    (g / s).write_text(v)
            bg = CK.gom_tu_thu_muc(td)
            r = CK.do_kho(bg, bo_mau_thu=False)
            h = XH.xep(r, bg)
            ten = [Path(x["ten"]).stem for x in h]
            self.assertEqual(ten[0], "a")              # A + .set
            self.assertLess(ten.index("b"), ten.index("c"))
            d = next(x for x in h if Path(x["ten"]).stem == "d")
            self.assertEqual(d["lan_doc"], "mql4")
            self.assertEqual(d["hang"], "B")
            c = next(x for x in h if Path(x["ten"]).stem == "c")
            self.assertLess(c["diem"], 0)
            out = Path(td) / "ra"
            CK.xuat(r, out, h)
            hang = json.loads((out / "HANG.json").read_text())
            self.assertTrue(hang[0].endswith("_a.mq5"))
            self.assertTrue(list(out.glob("*_a.set")))

    def test_telegram_can_mtproto_hang_T(self):
        h = XH.xep({"ds": []}, [], [{"url": "t.me/x/1", "diem": 60, "co_set": True, "co_ma": False}])
        self.assertEqual(h[0]["hang"], "T")
        self.assertEqual(h[0]["diem"], 40)


class DieuToc(unittest.TestCase):
    def test_muc(self):
        self.assertEqual(DT.trang_thai(cpu=10, tien_trinh=[], khoa=[])["muc"], "binh_thuong")
        self.assertEqual(DT.trang_thai(cpu=10, tien_trinh=[(999999, "python vong_thu_nghiem.py --mau x")],
                                       khoa=[])["muc"], "cham")
        self.assertEqual(DT.trang_thai(cpu=10, tien_trinh=[], khoa=[{"viec": "tester"}])["muc"], "dung")
        self.assertEqual(DT.trang_thai(cpu=90, tien_trinh=[], khoa=[])["muc"], "dung")
        self.assertEqual(DT.trang_thai(cpu=65, tien_trinh=[], khoa=[])["muc"], "cham")
        with mock.patch.dict(os.environ, {"BRAIN_DIEU_TOC": "tat"}):
            self.assertEqual(DT.trang_thai(cpu=99, tien_trinh=[], khoa=[{"x": 1}])["muc"], "binh_thuong")

    def test_dau_backtest_tu_xoa(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(DT, "THU_MUC_DAU", Path(td)):
            with DT.dang_chay("vong_thu_nghiem x"):
                self.assertEqual(DT.trang_thai(cpu=0, tien_trinh=[], khoa=[])["muc"], "cham")
            self.assertEqual(DT.trang_thai(cpu=0, tien_trinh=[], khoa=[])["muc"], "binh_thuong")

    def test_tru_cau_kho_dung_thi_bo_qua(self):
        import importlib
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.dict(os.environ, {"BRAIN_CAU_KHO_DIR": td}):
            import tru.cau_kho as T
            T = importlib.reload(T)
            r = T.mot_luot(tai_mql5=lambda *a, **k: self.fail("khong duoc tai"),
                           dieu_toc=lambda: {"muc": "dung", "ly_do": ["khoa_tester:x"]})
            self.assertIn("dieu_toc_dung", r["bo_qua"])

    def test_dieu_phoi_chan_lane_quet(self):
        import dieu_phoi as DP
        self.assertIn(DP.TRU["SEEKER"]["lan"], DP.LAN_DIEU_TOC)
        self.assertIn(DP.TRU["CAUKHO"]["lan"], DP.LAN_DIEU_TOC)
        self.assertNotIn(DP.TRU["QUANTLAB"]["lan"], DP.LAN_DIEU_TOC)


class TelegramCongKhai(unittest.TestCase):
    def test_loc_theo_truy_van_va_chua_do_duoc(self):
        def doc(k, truoc=None):
            if k == "tat":
                return {"bai": [], "truoc_tiep": None, "loi": "kenh tat xem truoc web"}
            return {"bai": [{"url": "t.me/k/1", "van_ban": "Gold EA mt5 + set file",
                             "dinh_kem": [{"ten": "Gold.set"}]},
                            {"url": "t.me/k/2", "van_ban": "chao buoi sang", "dinh_kem": []}],
                    "truoc_tiep": None}
        with mock.patch.object(TGC.TG, "san_sang_mtproto", lambda: (False, "chua co phien")):
            r = TGC.mot_luot(TV.sinh(), doc_trang=doc, kenh=["k", "tat"])
        self.assertEqual(len(r["bai_khop"]), 1)
        self.assertTrue(r["bai_khop"][0]["co_set"])
        self.assertTrue(r["tim_kenh"].startswith("CHUA DO DUOC"))
        self.assertEqual(TGC.tom_tat(r)["kenh_doc_duoc"], 1)


class VongThuTheoHang(unittest.TestCase):
    def test_thu_tu(self):
        import vong_thu_nghiem as V
        with tempfile.TemporaryDirectory() as td:
            for n in ("a.mq5", "b.mq5", "c.mq5"):
                (Path(td) / n).write_text("x")
            (Path(td) / "HANG.json").write_text(json.dumps(["c.mq5", "a.mq5"]))
            self.assertEqual([f.name for f in V.danh_sach_file(Path(td), theo_hang=True)],
                             ["c.mq5", "a.mq5", "b.mq5"])
            self.assertEqual(len(V.danh_sach_file(Path(td), toi_da=1)), 1)


if __name__ == "__main__":
    unittest.main()
