"""Bo doc vong 2 (11/10/2026 dem), doc tay hang B GitHub (lenh vao trong nhanh else, kiem Bars):

- `if(A){Buy} else if(B){Sell}`: nhanh else-if dich thanh B CHI KHI chung minh B loai tru A
  (`_mau_thuan`) -> `B and not A` == `B`. Khong chung minh duoc / `else {` tran / if khong
  ngoac -> van tu choi (PHAI).
- `if(Bars(_Symbol,_Period) < N) return;` = kiem du lieu khoi dong (quan tri), nhu `x <= 0`.
"""
from nhan import doc_ma as DM

_EA = """
#include <Trade/Trade.mqh>
CTrade trade;
input int InpFast = 10;
input int InpSlow = 30;
int fh, sh;
int OnInit(){ fh=iMA(_Symbol,_Period,InpFast,0,MODE_EMA,PRICE_CLOSE);
 sh=iMA(_Symbol,_Period,InpSlow,0,MODE_EMA,PRICE_CLOSE); return 0; }
void OnTick()
{
   if(Bars(_Symbol,_Period) < InpSlow + 10) return;
   double f[], s[];
   ArraySetAsSeries(f,true);
   ArraySetAsSeries(s,true);
   if(CopyBuffer(fh,0,1,2,f)!=2) return;
   if(CopyBuffer(sh,0,1,2,s)!=2) return;
   if(PositionsTotal() > 0) return;
   if(f[1] <= s[1] && f[0] > s[0])
   {
      trade.Buy(0.1,_Symbol);
   }
   else if(f[1] >= s[1] && f[0] < s[0])
   {
      trade.Sell(0.1,_Symbol);
   }
}
"""


def _doc(vb):
    return DM.doc_chien_luoc(vb, nguon="t")


def test_else_if_loai_tru_chung_minh_duoc():
    r = _doc(_EA)
    assert r["so_vao_lenh"] == 2
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]
    ban = [c for c in r["co_che"] if c.get("chieu", 0) < 0 or "ban" in str(c.get("ten", ""))]
    assert ban, r["co_che"]
    assert "Bars(" in " ".join(" ".join(c.get("bo_qua_quan_tri", [])) for c in r["co_che"])


def test_else_if_khong_loai_tru_tu_choi():
    # B = f[0] < s[0] khong chung minh loai tru A (f[1]<=s[1] && f[0]>s[0])? co: f0>s0 vs f0<s0.
    # Doi B thanh dieu kien KHONG lien quan -> phai tu choi.
    vb = _EA.replace("else if(f[1] >= s[1] && f[0] < s[0])", "else if(f[1] > 0.5)")
    r = _doc(vb)
    assert r["so_vao_lenh_co_co_che"] == 1
    assert any("loai tru" in x for x in r["chua_dien_dat_duoc"])


def test_else_tran_van_tu_choi():
    vb = _EA.replace("else if(f[1] >= s[1] && f[0] < s[0])", "else")
    r = _doc(vb)
    assert r["so_vao_lenh_co_co_che"] == 1
    assert any("nhanh else" in x for x in r["chua_dien_dat_duoc"])


def test_bars_lon_hon_khong_phai_kiem_du_lieu():
    assert DM._la_kiem_loi_du_lieu("Bars(_Symbol,_Period) < 100")
    assert DM._la_kiem_loi_du_lieu("BarsCalculated(h) <= 0")
    assert not DM._la_kiem_loi_du_lieu("Bars(_Symbol,_Period) > 100")


def test_mau_thuan_hai_khoang_hang_so():
    x = {"chi_bao": "rsi", "chu_ky": 14}
    assert DM._mau_thuan([{"trai": x, "phep": "<", "phai": {"hang": 30.0}},
                          {"trai": x, "phep": ">", "phai": {"hang": 70.0}}])
    assert DM._mau_thuan([{"trai": x, "phep": "<", "phai": {"hang": 30.0}},
                          {"trai": x, "phep": ">=", "phai": {"hang": 30.0}}])
    # khoang GIAO nhau / khac toan hang -> khong mau thuan (PHAI)
    assert DM._mau_thuan([{"trai": x, "phep": "<", "phai": {"hang": 70.0}},
                          {"trai": x, "phep": ">", "phai": {"hang": 30.0}}]) is None
    assert DM._mau_thuan([{"trai": x, "phep": "<=", "phai": {"hang": 30.0}},
                          {"trai": x, "phep": ">=", "phai": {"hang": 30.0}}]) is None
    y = {"chi_bao": "rsi", "chu_ky": 21}
    assert DM._mau_thuan([{"trai": x, "phep": "<", "phai": {"hang": 30.0}},
                          {"trai": y, "phep": ">", "phai": {"hang": 70.0}}]) is None


_RSI = """
#include <Trade/Trade.mqh>
CTrade trade;
input double InpBuy = 30;
input double InpSell = 70;
int h;
int OnInit(){ h=iRSI(_Symbol,_Period,14,PRICE_CLOSE); return 0; }
void OnTick()
{
   double r[];
   ArraySetAsSeries(r,true);
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(PositionsTotal() > 0) return;
   if(r[0] < InpBuy)
   {
      trade.Buy(0.1,_Symbol);
   }
   else if(r[0] > InpSell)
   {
      trade.Sell(0.1,_Symbol);
   }
}
"""


def test_else_if_nguong_rsi_roi_nhau():
    r = _doc(_RSI)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]


def test_else_if_nguong_rsi_giao_nhau_tu_choi():
    r = _doc(_RSI.replace("input double InpSell = 70;", "input double InpSell = 20;"))
    assert r["so_vao_lenh_co_co_che"] == 1


_HAM = """
#include <Trade/Trade.mqh>
CTrade trade;
int h;
int OnInit(){ h=iRSI(_Symbol,_Period,14,PRICE_CLOSE); return 0; }
void MoMua(){ trade.Buy(0.1,_Symbol); }
void MoBan(){ trade.Sell(0.1,_Symbol); }
void OnTick()
{
   double r[];
   ArraySetAsSeries(r,true);
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(PositionsTotal() > 0) return;
   if(r[0] < 30) MoMua();
   else if(r[0] > 70) MoBan();
}
"""


def test_else_if_mot_lenh_va_ham_phu():
    r = _doc(_HAM)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]


def test_else_if_mot_lenh_giao_nhau_tu_choi():
    # B = r<50 giao A = r<30: `else if` nghia la 30<=r<50 - truoc day bi dich SAI thanh r<50
    r = _doc(_HAM.replace("r[0] > 70", "r[0] < 50"))
    assert r["so_vao_lenh_co_co_che"] == 1
    assert any("loai tru" in x for x in r["chua_dien_dat_duoc"])
    vb = _RSI.replace("   if(r[0] < InpBuy)\n   {\n      trade.Buy(0.1,_Symbol);\n   }\n"
                      "   else if(r[0] > InpSell)\n   {\n      trade.Sell(0.1,_Symbol);\n   }",
                      "   if(r[0] < InpBuy) trade.Buy(0.1,_Symbol);\n"
                      "   else if(r[0] < 50) trade.Sell(0.1,_Symbol);")
    assert "else if(r[0] < 50) trade.Sell" in vb
    r = _doc(vb)
    assert r["so_vao_lenh_co_co_che"] == 1


def test_else_tran_ham_phu_tu_choi():
    r = _doc(_HAM.replace("else if(r[0] > 70) MoBan();", "else MoBan();"))
    assert r["so_vao_lenh_co_co_che"] == 1
