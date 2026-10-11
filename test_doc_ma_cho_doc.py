"""Bo doc MQL5 cho tap EA "cho bo doc" cua SEEKER (11/10/2026).

Moi test la mot loi bo doc CHUNG do tren tap cho (khong khop dap an mot EA):
const cap file, phu dinh kep `!(a && b)`, khai bao nhieu bien mot dong, `x == EMPTY_VALUE`,
`const` cuc bo, lenh vao trong `return(...)` khong phai ma chet, toan tu ba ngoi chon lenh
(+ SL/TP ATR qua bien/lam tron) - va cac truong hop PHAI van tu choi.
"""
from nhan import doc_ma as DM

_RSI = """
#include <Trade/Trade.mqh>
CTrade trade;
input int InpStart = 14;
const int InpEnd = 18;
const double InpLevel = 65.0;
input int InpRSIPeriod = 14;
int h;
int OnInit(){ h = iRSI(_Symbol,_Period,InpRSIPeriod,PRICE_CLOSE); return 0; }
void OnTick()
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(),dt);
   if(dt.hour<InpStart || dt.hour>=InpEnd) return;
   double r[];
   ArraySetAsSeries(r,true);
   if(CopyBuffer(h,0,1,2,r)!=2) return;
   double rsiNow=r[0], rsiPrev=r[1];
   if(rsiNow==EMPTY_VALUE) return;
   if(!(rsiPrev<InpLevel && rsiNow>=InpLevel)) return;
   trade.Sell(0.1,_Symbol);
}
"""


def _doc(vb):
    return DM.doc_chien_luoc(vb, nguon="t")


def test_const_phu_dinh_kep_khai_bao_phay():
    r = _doc(_RSI)
    assert r["so_vao_lenh_co_co_che"] == 1, r["chua_dien_dat_duoc"]
    vao = r["co_che"][0]["vao"]
    s = str(vao)
    assert "'rsi'" in s and "65.0" in s and "'gio'" in s
    assert any(d["trai"].get("chi_bao") == "tre" and d["phep"] == "<" for d in vao)
    assert any(d["phai"].get("hang") == 18.0 and d["phep"] == "<" for d in vao)   # const
    assert "rsiNow==EMPTY_VALUE" in " ".join(r["co_che"][0]["bo_qua_quan_tri"])


def test_phu_dinh_kep_hoac_van_tu_choi():
    vb = _RSI.replace("!(rsiPrev<InpLevel && rsiNow>=InpLevel)",
                      "!(rsiPrev<InpLevel || rsiNow>=InpLevel)")
    assert _doc(vb)["so_vao_lenh_co_co_che"] == 0


def test_const_trong_ham_khong_thanh_hang_file():
    vb = _RSI.replace("const int InpEnd = 18;", "") \
        .replace("void OnTick()\n{", "void OnTick()\n{\n   const int InpEnd = 18;")
    assert "InpEnd" not in DM._hang_const_cap_file(DM._chuan_hoa_mql5(vb))
    assert "InpEnd" in DM._hang_const_cap_file(_RSI)


def test_tach_khai_bao_phay():
    ra = DM._tach_khai_bao_phay("  double a=r[0], b=f(1,2);\nfor(int i=0,j=1;i<2;i++){}\n")
    assert "  double a=r[0];\n  double b=f(1,2);" in ra
    assert "for(int i=0,j=1;" in ra


_TN = """
#include <Trade/Trade.mqh>
CTrade trade;
input int InpFast = 20;
input int InpSlow = 50;
input double InpStopAtr = 2.0;
input double InpRR = 1.5;
input ulong InpMagic = 1;
int fh, sh, ah;
int OnInit(){ fh=iMA(_Symbol,_Period,InpFast,0,MODE_EMA,PRICE_CLOSE);
 sh=iMA(_Symbol,_Period,InpSlow,0,MODE_EMA,PRICE_CLOSE); ah=iATR(_Symbol,_Period,14); return 0; }
double RoundPrice(const double price)
  {
   const double tick = SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   if(tick <= 0.0)
      return NormalizeDouble(price,_Digits);
   return NormalizeDouble(MathRound(price/tick)*tick,_Digits);
  }
bool HasPos()
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      const ulong t = PositionGetTicket(i);
      if(t != 0 && PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) == InpMagic)
         return true;
     }
   return false;
  }
void OnTick()
  {
   if(HasPos()) return;
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick)) return;
   double f[],s[],a[];
   ArraySetAsSeries(f,true); ArraySetAsSeries(s,true); ArraySetAsSeries(a,true);
   if(CopyBuffer(fh,0,0,3,f) != 3 || CopyBuffer(sh,0,0,3,s) != 3 ||
      CopyBuffer(ah,0,0,2,a) != 2 || a[1] <= 0.0)
      return;
   const bool buy_signal = f[1] > s[1] && f[2] <= s[2];
   const bool sell_signal = f[1] < s[1] && f[2] >= s[2];
   if(!buy_signal && !sell_signal)
      return;
   const double entry = buy_signal ? tick.ask : tick.bid;
   const double min_stop = MathMax((double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*_Point,_Point);
   const double distance = MathMax(a[1]*InpStopAtr,min_stop);
   const double stop = RoundPrice(buy_signal ? entry-distance : entry+distance);
   const double limit = RoundPrice(buy_signal ? entry+distance*InpRR : entry-distance*InpRR);
   const bool ok = buy_signal
                   ? trade.Buy(0.1,_Symbol,0.0,stop,limit,"b")
                   : trade.Sell(0.1,_Symbol,0.0,stop,limit,"s");
  }
"""


def test_ba_ngoi_chon_lenh_va_sltp_atr():
    r = _doc(_TN)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]
    mua = next(c for c in r["co_che"] if c["chieu"] == 1)
    ban = next(c for c in r["co_che"] if c["chieu"] == -1)
    assert mua["vao"][0]["phep"] == ">" and ban["vao"][0]["phep"] == "<"
    for c, ref in ((mua, "ASK"), (ban, "BID")):
        k = c["sltp"]
        assert k["sl_kc"]["he_so"] == [2.0] and k["tp_kc"]["he_so"] == [3.0]
        assert k["ref_sl"] == ref and k["sl_kc"]["toan_hang"][0]["chi_bao"] == "atr"
        assert c["nhom_he"] == "t"                       # HasPos(): mot vi the mot luc
    assert any("loai tru" in x for x in ban["bo_qua_quan_tri"])


def test_ba_ngoi_khong_loai_tru_thi_tu_choi_nhanh_ban():
    # sell khong mau thuan voi buy (rsi khac ema) -> `!buy_signal` KHONG chung minh duoc
    vb = _TN.replace("const bool sell_signal = f[1] < s[1] && f[2] >= s[2];",
                     "const bool sell_signal = a[1] > 0.001;")
    r = _doc(vb)
    assert all(c["chieu"] == 1 for c in r["co_che"])


def test_ba_ngoi_co_chon_nhanh_thuan_khong_lay():
    vb = _TN.replace("const bool ok = buy_signal", "const bool isBuy = buy_signal;\n"
                     "   const bool ok = isBuy")
    r = _doc(vb)
    assert r["so_vao_lenh_co_co_che"] == 0


def test_lenh_vao_trong_return_khong_phai_ma_chet():
    vb = """
bool Send(MqlTradeRequest &request)
  {
   MqlTradeResult result;
   ZeroMemory(result);
   return(OrderSend(request,result) && result.retcode==TRADE_RETCODE_DONE);
  }
void OnTick(){ }
"""
    k = vb.index("OrderSend")
    assert DM._ma_chet(vb, k) is False
    vb2 = vb.replace("   ZeroMemory(result);", "   return(false);")
    assert DM._ma_chet(vb2, vb2.index("OrderSend")) is True
