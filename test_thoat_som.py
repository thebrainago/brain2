# -*- coding: utf-8 -*-
"""Thoat som `if(X){ Print(..); return; }` (them 11/10/2026).

Truoc do `_thoat_som` chi bat `if(X) return;` ngay sau `)`: dang co khoi `{}`,
co `Print`/`Comment` hay lenh khac truoc `return`, hoac nam TRONG khoi guard cua
lenh vao deu bi BO SOT -> bo loc tin hieu mat im lang (ban dich LONG hon EA).
Moi test la mot doan EA viet tay; kiem ca hai chieu: bat dung bo loc, va KHONG
coi la thoat khi `return` khong chac chan chay.
"""
import unittest

from nhan import doc_ma as DM

DAU = """#property copyright "t"
#include <Trade\\Trade.mqh>
CTrade trade;
int h1, h2, h3;
double a[], b[], r[];
int dem = 0;
int OnInit(){ h1=iMA(_Symbol,_Period,10,0,MODE_EMA,PRICE_CLOSE);
   h2=iMA(_Symbol,_Period,30,0,MODE_EMA,PRICE_CLOSE);
   h3=iRSI(_Symbol,_Period,14,PRICE_CLOSE); return 0; }
bool IsNewBar(){ static datetime p=0; datetime c=iTime(_Symbol,PERIOD_CURRENT,0);
   if(p!=c){p=c; return true;} return false; }
%s
void OnTick(){
   if(!IsNewBar()) return;
   ArraySetAsSeries(a,true); ArraySetAsSeries(b,true); ArraySetAsSeries(r,true);
   CopyBuffer(h1,0,0,3,a);
   CopyBuffer(h2,0,0,3,b);
   CopyBuffer(h3,0,0,3,r);
%s
}
"""

VAO = "   if(a[1]>b[1]) trade.Buy(0.1);"


def _doc(than: str, ham: str = "") -> dict:
    return DM.doc_chien_luoc(DAU % (ham, than), nguon="t.mq5")


def _co_rsi_duoi_70(cc: dict) -> bool:
    return any("rsi" in str(d) and d["phep"] == "<" and d["phai"] == {"hang": 70.0}
               for d in cc["vao"])


class TestThoatSom(unittest.TestCase):
    def test_goc_khong_loc(self):
        d = _doc(VAO)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        self.assertEqual(len(d["co_che"][0]["vao"]), 1)

    def test_ba_dang_thoat_cho_cung_bo_loc(self):
        kq = []
        for th in ("if(r[1]>=70) return;",
                   "if(r[1]>=70) { return; }",
                   "if(r[1]>=70)\n     {\n      Print(\"qua mua; {bo}\");\n      return;\n     }",
                   "if(r[1]>=70){ Comment(\"x\"); PrintFormat(\"%d\",1); Alert(\"y\"); return; }"):
            d = _doc("   " + th + "\n" + VAO)
            self.assertEqual(d["so_vao_lenh_co_co_che"], 1, th)
            cc = d["co_che"][0]
            self.assertTrue(_co_rsi_duoi_70(cc), th)
            self.assertNotIn("gia_dinh", cc)          # Print/Comment/Alert la vo hai
            kq.append(cc["vao"])
        self.assertTrue(all(x == kq[0] for x in kq))

    def test_lenh_khac_truoc_return_van_loc_va_duoc_ghi(self):
        d = _doc("   if(r[1]>=70){ dem++; Print(\"x\"); return; }\n" + VAO)
        cc = d["co_che"][0]
        self.assertTrue(_co_rsi_duoi_70(cc))
        self.assertTrue(any("thoat som co lenh khac" in g and "dem++" in g
                            for g in cc["gia_dinh"]))

    def test_thoat_trong_khoi_guard(self):
        d = _doc("   if(a[1]>b[1]){\n      if(r[1]>=70){ Print(\"x\"); return; }\n"
                 "      trade.Buy(0.1);\n   }")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        self.assertTrue(_co_rsi_duoi_70(d["co_che"][0]))

    def test_khoi_khong_thoat_thi_khong_loc(self):
        for th in ("if(r[1]>=70){ Print(\"x\"); }",
                   "if(r[1]>=70){ return; Print(\"x\"); }".replace("return; ", "Print(\"y\"); "),
                   "if(a[2]>b[2]){ Print(\"z\"); } else if(r[1]>=70) return;"):
            d = _doc("   " + th + "\n" + VAO)
            if d["so_vao_lenh_co_co_che"]:
                self.assertFalse(_co_rsi_duoi_70(d["co_che"][0]), th)

    def test_return_long_co_dieu_kien_thi_tu_choi(self):
        # vao chi khi NOT(r>=70 and a2>a1) - khong dien dat duoc -> khong dich
        d = _doc("   if(r[1]>=70){ if(a[2]>a[1]) return; Print(\"x\"); }\n" + VAO)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("return trong khoi long" in x for x in d["chua_dien_dat_duoc"]))

    def test_kiem_du_lieu_copy_la_quan_tri(self):
        than = ("   int v = CopyBuffer(h3,0,0,3,r);\n"
                "   if(v != 3){ Print(\"thieu du lieu\"); return; }\n" + VAO)
        d = _doc(than)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        self.assertIn("v != 3", d["co_che"][0]["bo_qua_quan_tri"])
        self.assertEqual(len(d["co_che"][0]["vao"]), 1)

    def test_bien_copy_bi_gan_khac_khong_phai_kiem_loi(self):
        than = ("   int v = CopyBuffer(h3,0,0,3,r);\n   v = dem;\n"
                "   if(v != 3){ Print(\"x\"); return; }\n" + VAO)
        self.assertEqual(_doc(than)["so_vao_lenh_co_co_che"], 0)

    def test_ham_chi_loi_api_la_kiem_loi(self):
        ham = ("bool NP(double &p){ double ts=0;\n"
               "   if(!SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE,ts)){ Print(\"loi\"); return false; }\n"
               "   p = NormalizeDouble(p,_Digits); return true; }")
        than = ("   if(a[1]>b[1]){ double sl=0;\n      if(!NP(sl)){ return; }\n"
                "      trade.Buy(0.1);\n   }")
        d = _doc(than, ham)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        self.assertIn("!NP(sl)", d["co_che"][0]["bo_qua_quan_tri"])

    def test_ham_loc_tin_hieu_khong_phai_kiem_loi(self):
        ham = "bool Ok(){ if(r[1]>70) return false; return true; }"
        than = "   if(!Ok()){ Print(\"chan\"); return; }\n" + VAO
        d = _doc(than, ham)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("loc thoat som" in x and "Ok()" in x
                            for x in d["chua_dien_dat_duoc"]))


class TestTachLenh(unittest.TestCase):
    def test_chuoi_co_ngoac_va_cham_phay(self):
        self.assertEqual(DM._tach_lenh(' Print("a;{b}"); x=1; if(y){z();} return; '),
                         ['Print("a;{b}");', 'x=1;', 'if(y){z();}', 'return;'])

    def test_else_cung_lenh(self):
        self.assertEqual(DM._tach_lenh('if(y){a();} else {b();} return;'),
                         ['if(y){a();} else {b();}', 'return;'])

    def test_lenh_thoat(self):
        vb = 'if(x){ Print("p"); n=2; return; } k;'
        k = vb.index(")")
        het, tac = DM._lenh_thoat(vb, k)
        self.assertEqual(vb[het:].strip(), "k;")
        self.assertEqual(tac, ["n=2;"])
        self.assertIsNone(DM._lenh_thoat('if(x){ if(y) return; }', 4))


if __name__ == "__main__":
    unittest.main()
