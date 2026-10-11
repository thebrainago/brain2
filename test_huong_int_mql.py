# -*- coding: utf-8 -*-
"""Ham tin hieu tra HUONG so nguyen (+1/-1/0) - `nhan/huong_int_mql.py` (11/10/2026).

Moi test la mot dang CHUNG do tren tap cho bo doc (EMA_Cross_Demo, GoldBreakout, RegimeRouter):
`int dir = CheckX(); if(dir == 0) return; Open(dir);` -> `isBuy = dir > 0` -> `isBuy ? Buy : Sell`.
Cac ca KHONG CHAC (OR hai dieu kien cung chieu, bien huong bi gan lai / truyen tham chieu,
nhanh -1 khong loai tru +1, dieu kien dung bien huong sau khi gan, ham huong tra 0 van vao)
PHAI tu choi.
"""
import numpy as np
import pandas as pd

from nhan import chi_phi as CP
from nhan import doc_ma as DM
from nhan import huong_int_mql as HI
from nhan import mo_phong as MP
from nhan import ngu_phap as NP

_DAU = """
#include <Trade/Trade.mqh>
CTrade g_trade;
input int InpFast = 12;
input int InpSlow = 26;
int hF, hS;
datetime g_last;
int OnInit(){ hF=iMA(_Symbol,_Period,InpFast,0,MODE_EMA,PRICE_CLOSE);
 hS=iMA(_Symbol,_Period,InpSlow,0,MODE_EMA,PRICE_CLOSE); return 0; }
bool IsNewBar(){ datetime t=iTime(_Symbol,_Period,0); if(t==g_last) return false; g_last=t; return true; }
"""

_SIG_R = """
int GetSignal()
{
   double f[], s[];
   ArraySetAsSeries(f, true);
   ArraySetAsSeries(s, true);
   if(CopyBuffer(hF, 0, 1, 2, f) != 2) return 0;
   if(CopyBuffer(hS, 0, 1, 2, s) != 2) return 0;
   if(f[0] > s[0] && f[1] <= s[1]) return  1;
   if(f[0] < s[0] && f[1] >= s[1]) return -1;
   return 0;
}
"""

_MO = """
void OpenPosition(const int signal)
{
   bool isBuy = (signal > 0);
   bool ok = isBuy ? g_trade.Buy(0.1, _Symbol)
                   : g_trade.Sell(0.1, _Symbol);
   if(!ok) Print("fail");
}
void OnTick()
{
   if(!IsNewBar()) return;
   if(PositionsTotal() > 0) return;
   int signal = GetSignal();
   if(signal == 0) return;
   OpenPosition(signal);
}
"""


def _doc(vb):
    return DM.doc_chien_luoc(vb, nguon="t")


def test_ham_huong_dang_r_hai_chieu():
    r = _doc(_DAU + _SIG_R + _MO)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]
    mua, ban = sorted(r["co_che"], key=lambda c: -c["chieu"])
    assert mua["chieu"] == 1 and ban["chieu"] == -1
    assert [d["phep"] for d in mua["vao"]] == [">", "<="]
    assert [d["phep"] for d in ban["vao"]] == ["<", ">="]
    assert any("GetSignal() tra +1" in x for x in mua["gia_dinh"])
    # nhanh -1 sau `if(A) return 1;`: A va B mau thuan -> bo qua co ghi
    assert any("suy ra: loai tru" in x for x in ban["bo_qua_quan_tri"])


def test_goi_truc_tiep_if_dir_bang_1():
    mo = """
void OnTick()
{
   if(!IsNewBar()) return;
   int dir = GetSignal();
   if(dir == 1) g_trade.Buy(0.1, _Symbol);
   if(dir == -1) g_trade.Sell(0.1, _Symbol);
}
"""
    r = _doc(_DAU + _SIG_R + mo)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]


def test_hai_dieu_kien_cung_chieu_la_or_tu_choi():
    sig = _SIG_R.replace("   return 0;\n}", "   if(f[0] > s[0] + 0.001) return 1;\n   return 0;\n}")
    r = _doc(_DAU + sig + _MO)
    assert r["so_vao_lenh_co_co_che"] == 0
    assert any("OR" in x for x in r["chua_dien_dat_duoc"])


def test_nhanh_am_khong_loai_tru_tu_choi():
    # +1: f>s va f[1]<=s[1] ; -1: f[1] < s[1] (KHONG mau thuan) -> ban = !(+1) and B: khong dich
    sig = _SIG_R.replace("if(f[0] < s[0] && f[1] >= s[1]) return -1;",
                         "if(f[1] < s[1]) return -1;")
    r = _doc(_DAU + sig + _MO)
    assert r["so_vao_lenh_co_co_che"] == 1          # chi nhanh mua
    assert any("chua chung minh loai tru" in x for x in r["chua_dien_dat_duoc"])


def test_bien_huong_gan_lai_tu_choi():
    mo = _MO.replace("   if(signal == 0) return;\n",
                     "   if(signal == 0) return;\n   signal = -signal;\n")
    r = _doc(_DAU + _SIG_R + mo)
    assert r["so_vao_lenh_co_co_che"] == 0


def test_bien_huong_truyen_tham_chieu_tu_choi():
    mo = _MO.replace("void OpenPosition(", "void Flip(int &x){ x = -x; }\nvoid OpenPosition(") \
        .replace("   if(signal == 0) return;\n", "   if(signal == 0) return;\n   Flip(signal);\n")
    r = _doc(_DAU + _SIG_R + mo)
    assert r["so_vao_lenh_co_co_che"] == 0


def test_tra_0_van_vao_tu_choi():
    # khong `if(signal == 0) return;`: isBuy = (0 > 0) sai -> nhanh BAN chay ca khi F tra 0
    # (ban = "tra -1 HOAC tra 0") -> tu choi; nhanh mua van dung (chi khi F tra +1)
    mo = _MO.replace("   if(signal == 0) return;\n", "")
    r = _doc(_DAU + _SIG_R + mo)
    assert r["so_vao_lenh_co_co_che"] == 1
    assert [c["chieu"] for c in r["co_che"]] == [1]
    assert any("tra 0" in x for x in r["chua_dien_dat_duoc"])


def test_dang_v_bien_dung_trong_dieu_kien_sau_tu_choi():
    # GoldBreakout: `if((dir == 1 && !InpAllowLong) ...) return(0);` dung bien huong -> tu choi
    sig = """
int CheckBreakout()
{
   double f[], s[];
   ArraySetAsSeries(f, true);
   ArraySetAsSeries(s, true);
   if(CopyBuffer(hF, 0, 1, 2, f) != 2) return(0);
   if(CopyBuffer(hS, 0, 1, 2, s) != 2) return(0);
   int dir = 0;
   if(f[0] > s[0]) dir = 1;
   if(f[0] < s[0]) dir = -1;
   if(dir == 1 && f[1] > 2.0) return(0);
   return(dir);
}
"""
    mo = _MO.replace("GetSignal()", "CheckBreakout()")
    assert isinstance(HI.ham_huong(DM._chuan_hoa_mql5(_DAU + sig + mo), "CheckBreakout"), str)
    assert _doc(_DAU + sig + mo)["so_vao_lenh_co_co_che"] == 0


def test_dang_v_sach():
    sig = """
int CheckBreakout()
{
   double f[], s[];
   ArraySetAsSeries(f, true);
   ArraySetAsSeries(s, true);
   if(CopyBuffer(hF, 0, 1, 2, f) != 2) return(0);
   if(CopyBuffer(hS, 0, 1, 2, s) != 2) return(0);
   int dir = 0;
   if(f[0] > s[0] && f[1] <= s[1]) dir = 1;
   if(f[0] < s[0] && f[1] >= s[1]) dir = -1;
   return(dir);
}
"""
    mo = _MO.replace("GetSignal()", "CheckBreakout()")
    r = _doc(_DAU + sig + mo)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]


def test_tin_hieu_khac_o_tang_ngoai_khong_phai_dang_nay():
    # dieu kien gia o OnTick (tang ngoai F) -> khong phai dang ham huong (hai tang) -> khong dich
    mo = _MO.replace("   if(signal == 0) return;\n",
                     "   if(signal == 0) return;\n   if(iClose(_Symbol,_Period,1) > 1.2) return;\n")
    r = _doc(_DAU + _SIG_R + mo)
    assert r["so_vao_lenh_co_co_che"] == 0


_DAO = """
ulong FindOwnPosition(int &side)
{
   side = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      side = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
      return ticket;
   }
   return 0;
}
void OpenPosition(const int signal)
{
   bool isBuy = (signal > 0);
   bool ok = isBuy ? g_trade.Buy(0.1, _Symbol)
                   : g_trade.Sell(0.1, _Symbol);
}
void OnTick()
{
   if(!IsNewBar()) return;
   int signal = GetSignal();
   if(signal == 0) return;
   int side = 0;
   ulong ticket = FindOwnPosition(side);
   if(ticket != 0)
   {
      if(side == signal) return;
      if(!g_trade.PositionClose(ticket))
      {
         Print("close failed");
         return;
      }
   }
   OpenPosition(signal);
}
"""


def test_dong_va_dao():
    r = _doc(_DAU + _SIG_R + _DAO)
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]
    for c in r["co_che"]:
        assert c.get("dao_khi_nguoc") is True and c.get("nhom_he") == "t"
        assert any("dong-va-dao" in x for x in c["gia_dinh"])


def test_dong_va_dao_khong_dong_lenh_thi_tu_choi():
    # khoi ticket != 0 lam viec khac (khong dong lenh) -> khong phai dong-va-dao
    vb = _DAU + _SIG_R + _DAO.replace("if(!g_trade.PositionClose(ticket))", "if(signal > 5)")
    assert _doc(vb)["so_vao_lenh_co_co_che"] == 0


def _df(rows):
    idx = pd.date_range("2024-01-01", periods=len(rows), freq="h")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)


def test_mo_phong_dao_chieu():
    n = 8
    df = _df([[1.0 + 0.01 * k] * 4 for k in range(n)])
    cho_m = np.zeros(n, bool)
    cho_b = np.zeros(n, bool)
    cho_m[1] = True                                   # mua o open bar 2
    cho_b[4] = True                                   # ban: dao o open bar 5
    chung = {"muc": None, "huong": None, "sl": None, "tp": None, "keo": None, "giu": 100,
             "chan_boi": [], "dat": [], "dao_khi_nguoc": True}
    nk = []
    kq = MP.chay_he(df, [dict(chung, chieu=1, cho=cho_m), dict(chung, chieu=-1, cho=cho_b)],
                    CP.MoHinhChiPhi(ma="TEST"), nhat_ky=nk)
    assert kq.so_lenh == 2
    assert nk[0]["bar_vao"] == 2 and nk[0]["bar_ra"] == 5 and nk[0]["ly_do"] == "dao_chieu"
    assert nk[1]["chieu"] == -1 and nk[1]["bar_vao"] == 5
    # khong co co -> giu nguyen lenh mua (khong dao)
    nk2 = []
    kq2 = MP.chay_he(df, [dict(chung, chieu=1, cho=cho_m, dao_khi_nguoc=False),
                          dict(chung, chieu=-1, cho=cho_b, dao_khi_nguoc=False)],
                     CP.MoHinhChiPhi(ma="TEST"), nhat_ky=nk2)
    assert kq2.so_lenh == 1


def test_sinh_chan_mang_co_dao():
    df = _df([[1.0, 1.0, 1.0, 1.0]] * 30)
    sp = {"chieu": 1, "giu": 1, "dao_khi_nguoc": True,
          "vao": [{"trai": {"chi_bao": "gia", "cot": "close"}, "phep": ">",
                   "phai": {"chi_bao": "ema", "n": 5}}]}
    assert NP.sinh_chan(sp, df)["dao_khi_nguoc"] is True
