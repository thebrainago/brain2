# -*- coding: utf-8 -*-
"""CAU KHO MA: kho SEEKER -> doc_ma -> thu muc cho vong_thu_nghiem (11/10/2026)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))
sys.path.insert(0, str(LAB / "mau_thu"))

from nhan import cau_kho_ma as CK          # noqa: E402
from nhan import ma_nguon as MN            # noqa: E402
from nhan import so as SO                  # noqa: E402

EA = """//+------------------------------------------------------------------+
#include <Trade/Trade.mqh>
CTrade trade;
input int Ky = 14;
int h;
int OnInit(){ h = iRSI(_Symbol, PERIOD_CURRENT, Ky, PRICE_CLOSE); return INIT_SUCCEEDED; }
void OnTick()
{
   double r[];
   if(CopyBuffer(h, 0, 1, 1, r) < 1) return;
   if(PositionsTotal() > 0) return;
   if(r[0] < 30)
   {
      trade.Buy(0.1);
   }
}
"""

MQL4 = """int start()
{
   if(Close[1] > Open[1]) OrderSend(Symbol(), OP_BUY, 0.1, Ask, 3, 0, 0);
   return(0);
}
""" + "// dem cho du dai\n" * 20

CHI_BAO = """#property indicator_chart_window
#property indicator_buffers 1
double B[];
int OnInit(){ SetIndexBuffer(0, B); return INIT_SUCCEEDED; }
int OnCalculate(const int rates_total, const int prev_calculated, const datetime &time[],
  const double &open[], const double &high[], const double &low[], const double &close[],
  const long &tick_volume[], const long &volume[], const int &spread[])
{ for(int i=0;i<rates_total;i++) B[i]=close[i]; return rates_total; }
"""


def _bg(ten, src, url=""):
    return CK._ban_ghi(ten, src, url, "", "test")


class VanTay(unittest.TestCase):
    def test_bo_chu_thich_va_khoang_trang(self):
        a = CK.van_tay(EA)
        b = CK.van_tay("// ban quyen khac\n/* tac gia */\n" + EA.replace("   ", "\t"))
        self.assertEqual(a, b)
        self.assertNotEqual(a, CK.van_tay(EA.replace("< 30", "< 25")))

    def test_mql4(self):
        self.assertTrue(CK.la_mql4(MQL4))
        self.assertFalse(CK.la_mql4(EA))
        # file lai co dau hieu MQL5 -> MQL5
        self.assertFalse(CK.la_mql4(EA + "\n// OP_BUY\nint x = OP_BUY;"))


class Pheu(unittest.TestCase):
    def test_pheu_khu_trung_mql4_chi_bao(self):
        bg = [_bg("a.mq5", EA), _bg("a_copy.mq5", "// copy\n" + EA),
              _bg("b.mq4", MQL4), _bg("ind.mq5", CHI_BAO), _bg("nho.mq5", "void OnTick(){}")]
        r = CK.do_kho(bg)
        P = r["pheu"]
        self.assertEqual(P["tong"], 5)
        self.assertEqual(P["bo_kich_thuoc"], 1)
        self.assertEqual(P["trung_noi_dung"], 1)
        # 11/10/2026: MQL4 doc qua lan mong (`mql4_chuan`), so RIENG - khong vao `so` MQL5
        self.assertEqual(P["mql4_doc"], 1)
        self.assertEqual(P.get("mql4_bo_qua", 0), 0)
        self.assertEqual(r["so"].get("vao_lenh"), 1)   # chi EA MQL5
        self.assertEqual(r["so_mql4"].get("vao_lenh"), 1)
        self.assertEqual(P["ea_dat_lenh"], 1)          # chi bao khong vao doc_ma
        self.assertEqual(r["lan"].get("chi_bao"), 1)
        a = next(x for x in r["ds"] if x["ten"] == "a.mq5")
        self.assertEqual(a["ban_sao"], 1)

    def test_rsi_ea_ra_co_che_va_xuat(self):
        r = CK.do_kho([_bg("rsi.mq5", EA, "https://example.test/rsi")])
        self.assertEqual(r["pheu"].get("ra_co_che"), 1, r["ds"])
        self.assertEqual(CK.ty_le(r), 1.0)
        with tempfile.TemporaryDirectory() as d:
            p = CK.xuat(r, d)
            ng = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(len(ng), 1)
            self.assertEqual(ng[0]["url"], "https://example.test/rsi")
            f = Path(d) / ng[0]["file"]
            self.assertTrue(f.name.endswith(".mq5") and f.read_text(encoding="utf-8") == EA)
            # vong_thu_nghiem doc lai bang chinh doc_ma -> cung ket qua
            from nhan import doc_ma as DM
            self.assertTrue(DM.doc_chien_luoc(f.read_text(encoding="utf-8"))["co_che"])

    def test_ten_an_toan_khong_thoat_thu_muc(self):
        self.assertEqual(CK._ten_an_toan("../../etc/passwd"), "passwd.mq5")
        self.assertEqual(CK._ten_an_toan("C:\\x\\My EA.mq5"), "My_EA.mq5")

    def test_trung_mau_thu_khong_dem_lai(self):
        bg = CK.gom_tu_thu_muc(LAB / "mau_thu")
        r = CK.do_kho(bg)
        self.assertEqual(r["pheu"]["trung_mau_thu"], r["pheu"]["tong"])
        self.assertIsNone(CK.ty_le(r))                 # None = chua do, khong phai 0

    def test_khop_so_do_moc_gop(self):
        """Cung dinh nghia `do_moc`: chay tren mau_thu (giu mau) ra dung so gop."""
        import do_moc as DMOC
        import do_moc_rong as DR
        g = DMOC.do(sorted(DMOC.MAU.glob("*.mq5")) + DR.tep_rong())
        r = CK.do_kho(CK.gom_tu_thu_muc(LAB / "mau_thu"), bo_mau_thu=False)
        # A2 (11/10/2026): cau kho TACH lan THIEU_TEP (include ngoai khong co trong kho) ra
        # khoi `so`; TONG hai phan phai bang dung so do_moc (do_moc khong biet include).
        tt = r.get("so_thieu_tep", {})
        for k in ("vao_lenh", "vao_co", "co_che"):
            self.assertEqual(r["so"].get(k, 0) + tt.get(k, 0), g[k], k)


class TuSo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cau_kho_ma_")
        self.goc = SO.DB
        SO.DB = Path(self.tmp.name) / "nao.db"
        SO.khoi_tao()

    def tearDown(self):
        SO.DB = self.goc
        self.tmp.cleanup()

    def test_doc_artifact_code_va_noi_dung(self):
        bai = {"id": "1", "url": "https://www.mql5.com/en/code/1", "tieu_de": "RSI EA",
               "muc": "experts", "ten_file": "rsi.mq5", "noi_dung": EA,
               "so_byte": len(EA)}
        SO.them_artifact(MN.thanh_artifact(bai))
        with SO.ket_noi() as cn:
            cn.execute("INSERT INTO noi_dung(van_tay,url,kieu,van_ban) VALUES(?,?,?,?)",
                       ("x1", "https://example.test/ea2.mq5", "ma_nguon", "// khac\n" + EA))
            cn.execute("INSERT INTO noi_dung(van_tay,url,kieu,van_ban) VALUES(?,?,?,?)",
                       ("x2", "https://example.test/p.pine", "ma_nguon",
                        "//@version=5\nstrategy('x')\n"))
        bg = CK.gom_tu_so()
        self.assertEqual(len(bg), 2)                    # pine bi loc
        a = next(b for b in bg if b["nguon"].startswith("artifact:"))
        self.assertEqual(a["url"], "https://www.mql5.com/en/code/1")
        self.assertEqual(a["revision"], "mql5-code-1")
        r = CK.do_kho(bg)
        self.assertEqual(r["pheu"]["trung_noi_dung"], 1)
        self.assertEqual(r["pheu"]["ra_co_che"], 1)


class TaiMql5(unittest.TestCase):
    def test_tai_bo_qua_bai_da_co_va_gan_url(self):
        from unittest.mock import patch
        ds = [{"id": "11", "url": "https://www.mql5.com/en/code/11", "tieu_de": "RSI EA",
               "muc": "experts"},
              {"id": "12", "url": "https://www.mql5.com/en/code/12", "tieu_de": "Hong",
               "muc": "experts"}]
        goi = []

        def tai(b):
            goi.append(b["id"])
            if b["id"] == "12":
                return None
            return {**b, "ten_file": "rsi ea.mq5", "noi_dung": EA, "so_byte": len(EA)}

        with tempfile.TemporaryDirectory() as d, \
                patch.object(MN, "liet_ke_mql5", side_effect=lambda m, t: ds if t == 1 else []), \
                patch.object(MN, "tai_ma_nguon", side_effect=tai):
            b1 = CK.tai_mql5(d, so_trang=2, nghi_giay=0, in_ra=lambda *a: None)
            self.assertEqual(b1["moi"], 1)
            self.assertEqual(b1["khong_tai_duoc"], 1)
            self.assertTrue((Path(d) / "11_rsi_ea.mq5").exists())
            b2 = CK.tai_mql5(d, so_trang=1, nghi_giay=0, in_ra=lambda *a: None)
            self.assertEqual(b2.get("moi", 0), 0)
            self.assertEqual(b2["da_co"], 2)              # ca bai hong cung khong tai lai
            self.assertEqual(goi, ["11", "12"])
            g = CK.gom_tu_thu_muc(d)
            CK._url_tu_nguon_tai(g, d)
            self.assertEqual(g[0]["url"], "https://www.mql5.com/en/code/11")
            self.assertEqual(g[0]["revision"], "mql5-code-11")


class ChiDoc(unittest.TestCase):
    def test_khong_chay_ma(self):
        src = (LAB / "nhan" / "cau_kho_ma.py").read_text(encoding="utf-8")
        for cam in ("exec(", "eval(", "subprocess", "os.system", "__import__"):
            self.assertNotIn(cam, src)


if __name__ == "__main__":
    unittest.main()
