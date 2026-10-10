# -*- coding: utf-8 -*-
"""Lop doc MQL5 cua `nhan/doc_ma.py` (them 10/10/2026) tren bo `mau_thu/`.

Kiem NGHIA, khong chi dem: mot co che rut ra phai dung chieu, mang du bo loc
cua tac gia, va KHONG duoc rut tu lenh hedge phu thuoc gia vao lenh.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP

MAU = Path(__file__).resolve().parent / "mau_thu"


def _doc(ten):
    return DM.doc_chien_luoc((MAU / ten).read_text(errors="ignore"), nguon=ten)


def _h1(n=24 * 60, seed=3):
    rng = np.random.default_rng(seed)
    p = 1.1 + np.cumsum(rng.normal(0, 0.0007, n))
    idx = pd.date_range("2022-01-03", periods=n, freq="h")
    return pd.DataFrame({"open": p, "high": p + 0.0004, "low": p - 0.0004,
                         "close": p, "tick_volume": 100}, index=idx)


class PhaVoPhien(unittest.TestCase):
    def test_tach_mua_ban_theo_nhanh(self):
        d = _doc("EA Snippets_Breakout_Breakout1.mq5")
        self.assertEqual(d["so_vao_lenh"], 1)
        self.assertEqual(sorted(c["chieu"] for c in d["co_che"]), [-1, 1])

    def test_giu_bo_loc_gio_va_ma_cua_tac_gia(self):
        mua = [c for c in _doc("EA Snippets_Breakout_Breakout1.mq5")["co_che"]
               if c["chieu"] == 1][0]
        vao = mua["vao"]
        # Quy uoc chi so bar MQL5 (10/10 toi): EA chay o tick dau bar i+1 ->
        # gio/khung phien tinh theo luc DONG bar i (`"luc": "dong"`).
        self.assertEqual(vao[0]["phai"], {"chi_bao": "cao_trong_gio",
                                          "gio_tu": 5, "gio_den": 8, "luc": "dong"})
        # current[0].high o tick dau bar moi = gia tick dau ~ close bar i
        self.assertEqual(vao[0]["trai"], {"chi_bao": "gia", "cot": "close"})
        self.assertIn({"trai": {"chi_bao": "gio", "luc": "dong"}, "phep": ">=",
                       "phai": {"hang": 9.0}}, vao)
        # MaValues[0] sau CopyBuffer(...,0,10,...) KHONG dao chieu = bar cu nhat
        # = bar MQL5 9 = DSL tre 8
        self.assertIn({"trai": {"chi_bao": "gia", "cot": "close"}, "phep": ">=",
                       "phai": {"chi_bao": "tre", "n": 8,
                                "cua": {"chi_bao": "sma", "n": 50}}}, vao)

    def test_khong_rut_lenh_hedge(self):
        d = _doc("EA Snippets_Breakout_Breakout2.mq5")
        self.assertEqual(d["so_vao_lenh"], 3)
        # Lenh hedge KHONG thanh co che tin hieu thanh nen (van 2 chan mua/ban
        # cua lenh dau). Tu vong "ro hedge": hedge `postotal==1` duoc mo phong
        # trong khoi `ro` cua lenh dau -> dem la dich duoc (quan_ly_dich_duoc);
        # hedge `postotal==22` khong bao gio toi duoc -> ma_chet.
        self.assertEqual(len(d["co_che"]), 2)
        self.assertTrue(all("ro" in c for c in d["co_che"]))
        self.assertEqual(d["phan_loai_vao_lenh"]["dich_duoc"], 1)
        self.assertEqual(d["phan_loai_vao_lenh"]["quan_ly_dich_duoc"], 1)
        self.assertEqual(d["phan_loai_vao_lenh"]["ma_chet"], 1)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 2)

    def test_ham_tu_viet_khong_co_ma_thi_bo(self):
        self.assertEqual(_doc("EA Snippets_Pivots_Pivots1.mq5")["co_che"], [])

    def test_moi_co_che_qua_kiem_va_khong_nhin_truoc(self):
        df = _h1()
        for ten in ("EA Snippets_Breakout_Breakout1.mq5",
                    "EA Snippets_Breakout_Breakout2.mq5"):
            for c in _doc(ten)["co_che"]:
                self.assertEqual(NP.kiem_khai_bao(c), [])
                ok, ly = NP.kiem_khong_nhin_truoc(c, df)
                self.assertTrue(ok, ly)


class HamTinHieu(unittest.TestCase):
    def test_getsignal_tra_1_va_tru_1(self):
        d = _doc("mql5-pro_assets_EA_Template.mq5")
        mua = [c for c in d["co_che"] if c["chieu"] == 1][0]
        # iClose(...,1) = bar vua dong = `close`; iClose(...,2) = `close tre 1`
        self.assertEqual(mua["vao"], [{
            "trai": {"chi_bao": "gia", "cot": "close"},
            "phep": ">",
            "phai": {"chi_bao": "tre", "cua": {"chi_bao": "gia", "cot": "close"}, "n": 1}}])


class CaoTrongGio(unittest.TestCase):
    def test_nan_truoc_khi_khung_dong(self):
        df = _h1(48)
        s = NP.toan_hang(df, {"chi_bao": "cao_trong_gio", "gio_tu": 0, "gio_den": 7})
        self.assertTrue(s[df.index.hour <= 7].isna().all())
        ngay0 = df.index.normalize() == df.index[0].normalize()
        self.assertAlmostEqual(s[ngay0 & (df.index.hour == 8)].iloc[0],
                               df["high"][ngay0 & (df.index.hour <= 7)].max())



class VongThuNghiem(unittest.TestCase):
    def test_chay_het_va_toi_uu_khong_loi(self):
        import vong_thu_nghiem as V
        df = V.du_lieu_gia_lap(24 * 120, seed=7)
        ra = V.chay_mot_file(MAU / "EA Snippets_Breakout_Breakout1.mq5", df)
        # 10/10/2026 dem: mua + ban cua Breakout1 chung luat mot lenh/ngay -> MOT
        # dong nhom (mo phong chung), hai chan o `chan`.
        self.assertEqual(len(ra), 1)
        self.assertEqual(len(ra[0]["chan"]), 2)
        for x in ra:
            self.assertNotIn("loi", x)
            self.assertIn("tham_so_tot", x)
            self.assertIn("t_kiem", x)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------- them 10/10 chieu
B5 = "EA Snippets_Breakout_Breakout5.mq5"
B522 = "EA Snippets_Breakout_Breakout5-2-2.mq5"
# Pivot gio = (H+L+C)/3 cua thanh H1 vua dong = bar i cua mo phong (tre 0)
PIVOT_H1 = {"chi_bao": "tuyen_tinh", "toan_hang": [
    {"chi_bao": "gia", "cot": c} for c in ("high", "low", "close")],
    "he_so": [1 / 3.0] * 3}


def _gan_bang(a, b):
    """So sanh spec, he so so thuc so gan dung."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_gan_bang(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_gan_bang(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) < 1e-12
    return a == b


class PivotGio(unittest.TestCase):
    """`PivotsIsAbovePivot(close, pd.PivotsHour, "P")` dich theo ma MultiPivots.mqh."""

    def test_breakout5_mua_duoi_pivot_ban_tren_pivot(self):
        d = _doc(B5)
        cc = {c["chieu"]: c for c in d["co_che"]}
        self.assertEqual(sorted(cc), [-1, 1])
        # `upbreakout = !abovepivot` -> MUA khi close < P; `downbreakout = !upbreakout`
        self.assertEqual(len(cc[1]["vao"]), 1)
        self.assertEqual(cc[1]["vao"][0]["phep"], "<")
        self.assertTrue(_gan_bang(cc[1]["vao"][0]["phai"], PIVOT_H1), cc[1]["vao"])
        self.assertEqual(cc[-1]["vao"][0]["phep"], ">=")
        for c in cc.values():
            self.assertEqual(c["ho"], "quay_ve_trung_binh")
            self.assertTrue(c.get("gia_dinh"))
            self.assertEqual(NP.kiem_khai_bao(c), [])
            ok, ly = NP.kiem_khong_nhin_truoc(c, _h1())
            self.assertTrue(ok, ly)

    def test_khong_goi_Calculate_thi_khong_dich(self):
        """Struct khong duoc tinh -> P = 0 -> dich ra pivot la noi doi."""
        vb = (MAU / B5).read_text(errors="ignore").replace(
            "pivotsdata.Calculate(New_Time[0]);", "")
        self.assertEqual(DM.doc_chien_luoc(vb, nguon="x")["co_che"], [])

    def test_loai_pivot_khac_P_thi_khong_dich(self):
        vb = (MAU / B5).read_text(errors="ignore").replace(
            "PivotTypeHour=PIVOT_TRADITIONAL", "PivotTypeHour=PIVOT_WOODIES")
        self.assertEqual(DM.doc_chien_luoc(vb, nguon="x")["co_che"], [])


class GapCauHinh(unittest.TestCase):
    """`if(ReverseEntry)` / `if(startmanual!=0){...}` khong chay o cau hinh goc."""

    def test_breakout5_2_2_dich_lenh_dau_dung_chieu(self):
        d = _doc(B522)
        cc = {c["chieu"]: c for c in d["co_che"]}
        self.assertEqual(sorted(cc), [-1, 1])
        self.assertEqual(cc[1]["vao"][0]["phep"], "<")       # khong bi `upbreakout=true`
        # lenh dau + lenh them cua luoi martingale (10/10 toi: `ro.luoi`); nhanh hedge vung
        # (else, hedgeatlevel=0) la ma chet o input mac dinh
        self.assertEqual(d["so_vao_lenh_co_co_che"], 2)
        self.assertEqual(d["phan_loai_vao_lenh"]["quan_ly_dich_duoc"], 1)

    def test_doi_input_thi_doi_chieu(self):
        """ReverseEntry=true -> MUA khi close >= P. Chung to gap THEO GIA TRI, khong bo bua."""
        vb = (MAU / B522).read_text(errors="ignore").replace(
            "input bool           ReverseEntry = false;",
            "input bool           ReverseEntry = true;")
        cc = {c["chieu"]: c for c in DM.doc_chien_luoc(vb, nguon="x")["co_che"]}
        self.assertEqual(cc[1]["vao"][0]["phep"], ">=")
        self.assertEqual(cc[-1]["vao"][0]["phep"], "<")

    def test_tham_so_goi_tay_ngoai_OnChartEvent_thi_khong_gap(self):
        vb = (MAU / B522).read_text(errors="ignore").replace(
            "      checkForOpen();\n", "      checkForOpen(1);\n")
        d = DM.doc_chien_luoc(vb, nguon="x")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)


class HoVaTrung(unittest.TestCase):
    def test_template_ho_xu_huong_va_bo_dieu_kien_thua(self):
        d = _doc("mql5-pro_assets_EA_Template.mq5")
        for c in d["co_che"]:
            self.assertEqual(c["ho"], "xu_huong")
            self.assertEqual(len(c["vao"]), 1, c["vao"])
            self.assertEqual(NP.kiem_khai_bao(c), [])

    def test_ho_gia_thuan_chi_khi_moc_cu_hon(self):
        g = {"chi_bao": "gia", "cot": "close"}
        t1 = {"chi_bao": "tre", "cua": g, "n": 1}
        self.assertEqual(DM._ho_gia_thuan([{"trai": g, "phep": ">", "phai": t1}], 1),
                         "xu_huong")
        self.assertEqual(DM._ho_gia_thuan([{"trai": g, "phep": "<", "phai": t1}], 1),
                         "quay_ve_trung_binh")
        self.assertEqual(DM._ho_gia_thuan([{"trai": g, "phep": "<", "phai": t1}], -1),
                         "xu_huong")
        # moc KHONG cu hon gia ben trai -> khong gan
        self.assertIsNone(DM._ho_gia_thuan([{"trai": t1, "phep": ">", "phai": g}], 1))
        # hai dieu kien nguoc huong -> khong gan
        self.assertIsNone(DM._ho_gia_thuan(
            [{"trai": g, "phep": ">", "phai": t1}, {"trai": g, "phep": "<", "phai":
             {"chi_bao": "tre", "cua": g, "n": 3}}], 1))


class PhanLoaiVaMaChet(unittest.TestCase):
    def test_pivots1_lenh_vao_sau_return_la_ma_chet(self):
        d = _doc("EA Snippets_Pivots_Pivots1.mq5")
        self.assertEqual(d["phan_loai_vao_lenh"]["ma_chet"], 1)
        self.assertEqual(d["co_che"], [])

    def test_hedge_xep_quan_ly_vi_the(self):
        # Vong "ro hedge" (10/10): hedge `postotal==1` mo phong duoc trong khoi
        # `ro`; `postotal==22` khong toi duoc (toi da 2 lenh) -> ma_chet.
        d = _doc("EA Snippets_Breakout_Breakout2.mq5")
        self.assertEqual(d["phan_loai_vao_lenh"],
                         {"dich_duoc": 1, "ma_chet": 1, "quan_ly_vi_the": 0, "chua_dich": 0,
                          "quan_ly_dich_duoc": 1})
        # Breakout4: lenh dau KHONG dich duoc -> hedge van la quan_ly_vi_the
        d4 = _doc("EA Snippets_Breakout_Breakout4.mq5")
        self.assertEqual(d4["phan_loai_vao_lenh"]["quan_ly_dich_duoc"], 0)
        self.assertGreaterEqual(d4["phan_loai_vao_lenh"]["quan_ly_vi_the"], 1)

    def test_tong_phan_loai_bang_so_vao_lenh(self):
        for p in sorted(MAU.glob("*.mq5")):
            d = _doc(p.name)
            self.assertEqual(sum(d["phan_loai_vao_lenh"].values()), d["so_vao_lenh"], p.name)
            self.assertEqual(d["phan_loai_vao_lenh"]["dich_duoc"]
                             + d["phan_loai_vao_lenh"]["quan_ly_dich_duoc"],
                             d["so_vao_lenh_co_co_che"], p.name)


# ------------------------------------------------- them 10/10 toi: lech mot bar
_KHUNG_EA = """
input int x = 1;
void OnTick() {
   if(!IsNewBar()) return;
   double c1 = iClose(_Symbol, _Period, %s);
   double c2 = iClose(_Symbol, _Period, %s);
   if(c1 > c2) trade.Buy(0.1);
}
"""


class ChiSoBarMQL5(unittest.TestCase):
    """EA chay o TICK DAU bar i+1; mo phong quyet dinh o DONG bar i.

    MQL5 bar k >= 1 -> DSL tre k-1; bar 0 (moi mot tick) -> `close` bar i.
    """

    def test_ten_bar(self):
        self.assertEqual(DM._ten_bar_mql("close", 1), "close")
        self.assertEqual(DM._ten_bar_mql("high", 1), "high")
        self.assertEqual(DM._ten_bar_mql("close", 3), "close[2]")
        for c in ("open", "high", "low", "close"):
            self.assertEqual(DM._ten_bar_mql(c, 0), "close")
        # chi bao o bar 0 -> tre 0 (tinh voi gia tick dau ~ close bar i)
        self.assertEqual(DM._ten_bar_mql("iMA(NULL,0,50,0,MODE_SMA,PRICE_CLOSE)", 0),
                         "iMA(NULL,0,50,0,MODE_SMA,PRICE_CLOSE)")

    def _vao(self, a, b):
        cc = DM.doc_chien_luoc(_KHUNG_EA % (a, b), nguon="x")["co_che"]
        self.assertEqual(len(cc), 1)
        return cc[0]["vao"][0]

    def test_iclose_1_2_va_2_3(self):
        g = {"chi_bao": "gia", "cot": "close"}
        d = self._vao(1, 2)
        self.assertEqual(d["trai"], g)
        self.assertEqual(d["phai"], {"chi_bao": "tre", "cua": g, "n": 1})
        d = self._vao(2, 3)
        self.assertEqual(d["trai"], {"chi_bao": "tre", "cua": g, "n": 1})
        self.assertEqual(d["phai"], {"chi_bao": "tre", "cua": g, "n": 2})

    def test_tin_hieu_khop_ea_tung_bar(self):
        """Mo phong lai EA bang tay: tai mo bar j, EA so close[j-1] > close[j-2].
        Tin hieu DSL tai bar i (= j-1) phai TRUNG KHOP tung bar."""
        cc = DM.doc_chien_luoc(_KHUNG_EA % (1, 2), nguon="x")["co_che"][0]
        df = _h1(400)
        s = np.asarray(NP.sinh_tu_spec(cc, df), dtype=float)
        c = df["close"].to_numpy()
        ea = np.zeros(len(df))
        for j in range(2, len(df)):          # EA o tick dau bar j
            if c[j - 1] > c[j - 2]:
                ea[j - 1] = 1.0              # quyet dinh thuoc ve bar i = j-1
        self.assertTrue(np.array_equal(np.nan_to_num(s[2:]) != 0, ea[2:] != 0))

    def test_copyhigh_so_lui_mot_bar(self):
        t = [x for x in DM._bang_mql(
            "double h[];\nCopyHigh(_Symbol,_Period,1,3,h);\n"
            "double r=h[ArrayMaximum(h)];") if x[1] == "r"][0][2]
        self.assertEqual({k: v for k, v in t.items() if not k.startswith("_")},
                         {"chi_bao": "cao_nhat", "n": 3,
                          "cua": {"chi_bao": "gia", "cot": "high"}})
        t = [x for x in DM._bang_mql(
            "double h[];\nCopyHigh(_Symbol,_Period,2,3,h);\n"
            "double r=h[ArrayMaximum(h)];") if x[1] == "r"][0][2]
        self.assertEqual(t["chi_bao"], "tre")
        self.assertEqual(t["n"], 1)


class LucDong(unittest.TestCase):
    def test_gio_luc_dong_va_cuoi_tuan(self):
        idx = pd.date_range("2024-01-05 21:00", periods=3, freq="h")   # thu Sau
        df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0},
                          index=idx)
        g = NP.toan_hang(df, {"chi_bao": "gio", "luc": "dong"})
        self.assertEqual(list(g), [22.0, 23.0, 0.0])
        # bar 23:00 thu Sau dong -> bar ke tiep mo 00:00 THU HAI
        t = NP.toan_hang(df, {"chi_bao": "ngay_trong_tuan", "luc": "dong"})
        self.assertEqual(list(t), [4.0, 4.0, 0.0])
        # mac dinh (khong `luc`) giu nguyen nghia cu
        self.assertEqual(list(NP.toan_hang(df, {"chi_bao": "gio"})), [21.0, 22.0, 23.0])

    def test_cao_trong_gio_luc_dong_co_gia_tri_ngay_bar_cuoi_khung(self):
        """EA o tick dau bar 08:00 doc khung 00:00-07:59 da du -> DSL bar 07:00."""
        df = _h1(48)
        s = NP.toan_hang(df, {"chi_bao": "cao_trong_gio", "gio_tu": 0, "gio_den": 7,
                              "luc": "dong"})
        ngay0 = df.index.normalize() == df.index[0].normalize()
        self.assertTrue(s[ngay0 & (df.index.hour < 7)].isna().all())
        self.assertAlmostEqual(s[ngay0 & (df.index.hour == 7)].iloc[0],
                               df["high"][ngay0 & (df.index.hour <= 7)].max())

    def test_moi_co_che_mau_khong_nhin_truoc(self):
        df = _h1(24 * 30)
        for p in sorted(MAU.glob("*.mq5")):
            for c in _doc(p.name)["co_che"]:
                self.assertEqual(NP.kiem_khai_bao(c), [], p.name)
                ok, ly = NP.kiem_khong_nhin_truoc(c, df)
                self.assertTrue(ok, f"{p.name}: {ly}")
