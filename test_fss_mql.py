# -*- coding: utf-8 -*-
"""EA Forex Strategy Studio (cay quyet dinh + dong theo pip o tick dau) - them 11/10/2026.

(1) `nhan/fss_mql.py` doc EMA Crossover: calcMovingAvg = bar DA DONG shift+1, hai phieu
loai tru, `dong_mo_pip` tu cau hinh static; OrderSend dong lenh = quan_ly_dich_duoc;
(2) `mo_phong.chay_he` khop TUNG LENH voi ban chep tay OnTick (gia khop ASK/BID, BID tick
dau, pip theo ten ma, khong vao lai tick dong); (3) tu choi khi lech mau; (4) DSL.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP
from nhan import mo_phong as MP
from nhan import chi_phi as CP
import vong_thu_nghiem as V

FEMA = Path(__file__).resolve().parent / "mau_thu" / "mo_rong" / "forexstrategystudio" / \
    "EMA Crossover.mq5"


def _doc(thay=None):
    vb = FEMA.read_text(errors="ignore")
    for a, b in (thay or []):
        assert a in vb, a
        vb = vb.replace(a, b)
    return DM.doc_chien_luoc(vb, nguon="ema")


def _df(n=4000, seed=3, gia=1.1):
    r = np.random.default_rng(seed)
    c = gia * np.exp(np.cumsum(r.normal(0, 0.0012, n)))
    o = np.r_[c[0], c[:-1]] * (1 + r.normal(0, 0.0001, n))
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.0004, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.0004, n)))
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


def _tham_chieu(df, sp_, pip):
    o = df["open"].to_numpy()
    e9 = NP.toan_hang(df, {"chi_bao": "ema", "n": 9}).to_numpy()
    e21 = NP.toan_hang(df, {"chi_bao": "ema", "n": 21}).to_numpy()
    pos, ra = None, []
    for j in range(5, len(df)):
        bid = o[j]
        ask = bid + sp_[j] * bid
        if pos:                                  # BUY_OPEN||SELL_OPEN: chi logic dong, return
            diff = (bid - pos[2]) * pos[0]
            if (diff > 0 and diff / pip >= 20) or (diff <= 0 and -diff / pip >= 100):
                ra.append((pos[1], j, pos[0]))
                pos = None
            continue
        b = e9[j - 1] > e21[j - 1] and e9[j - 4] < e21[j - 4]
        s = e9[j - 1] < e21[j - 1] and e9[j - 4] > e21[j - 4]
        if b:
            pos = (1, j, ask)
        elif s:
            pos = (-1, j, bid)
    return ra


class DocFSS(unittest.TestCase):
    def test_doc_ema_crossover(self):
        d = _doc()
        self.assertEqual((d["so_vao_lenh"], d["so_vao_lenh_co_co_che"]), (2, 2))
        self.assertEqual(d["phan_loai_vao_lenh"]["dich_duoc"], 1)
        self.assertEqual(d["phan_loai_vao_lenh"]["quan_ly_dich_duoc"], 1)
        cc = {sp["chieu"]: sp for sp in d["co_che"]}
        self.assertEqual(cc[1]["vao"], [
            {"trai": {"chi_bao": "ema", "n": 9}, "phep": ">", "phai": {"chi_bao": "ema", "n": 21}},
            {"trai": {"chi_bao": "tre", "cua": {"chi_bao": "ema", "n": 9}, "n": 3}, "phep": "<",
             "phai": {"chi_bao": "tre", "cua": {"chi_bao": "ema", "n": 21}, "n": 3}}])
        for sp in cc.values():
            self.assertEqual(NP.kiem_khai_bao(sp), [])
            self.assertEqual(sp["dong_mo_pip"]["tp_pip"], 20.0)
            self.assertEqual(sp["dong_mo_pip"]["sl_pip"], 100.0)
            self.assertEqual(sp["nhom_he"], "ema")
            self.assertTrue(any("Strategy Tester" in g for g in sp["gia_dinh"]))

    def test_khop_tung_lenh(self):
        for ma, gia, pip in (("EURUSD", 1.1, 0.0001), ("USDJPY", 150.0, 0.01)):
            df = _df(gia=gia)
            specs = _doc()["co_che"]
            cp = V.mo_hinh_chi_phi(df)
            nk = []
            MP.chay_he(df, [NP.sinh_chan(sp, df) for sp in specs], cp, ma=ma, khung="H1",
                       nhat_ky=nk, diem=1e-5)
            sim = [(x["bar_vao"], x["bar_ra"], x["chieu"]) for x in nk if x.get("bar_ra") is not None]
            ref = _tham_chieu(df, cp.spread_mang(df.index), pip)
            self.assertGreater(len(ref), 20)
            self.assertEqual(sim, ref, ma)


class TuChoiFSS(unittest.TestCase):
    def _kiem_tu_choi(self, thay, chu):
        d = _doc(thay)
        self.assertEqual(d["co_che"], [])
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any(x.startswith("fss:") and chu in x for x in d["chua_dien_dat_duoc"]),
                        d["chua_dien_dat_duoc"])

    def test_bar_doc_khac(self):
        self._kiem_tu_choi([("CopyBuffer(ma_handle, 0, shift+1, 1, ma_values)",
                        "CopyBuffer(ma_handle, 0, shift, 1, ma_values)")], "calcMovingAvg")

    def test_cau_hinh_bi_gan_lai(self):
        self._kiem_tu_choi([("int OnInit() {", "int OnInit() {\n   tpValue = 5.0;")], "tpValue")

    def test_phieu_khong_loai_tru(self):
        vb = FEMA.read_text(errors="ignore")
        k = vb.index("booleanToAction(ACTION::SELL")
        # phieu SELL thanh y het BUY (ema9 > ema21 va ema9 tre3 < ema21 tre3): ca hai cung
        # dung -> EA ra NEUTRAL; bo doc phai tu choi (khong chung minh duoc loai tru)
        a = vb[k:].index(") < calcMovingAvg(")
        b = vb[k:].index(") > calcMovingAvg(")
        sau = list(vb[k:])
        sau[a + 2], sau[b + 2] = ">", "<"
        sau = "".join(sau)
        d = DM.doc_chien_luoc(vb[:k] + sau, nguon="ema")
        self.assertEqual(d["co_che"], [])
        self.assertTrue(any("loai tru" in x for x in d["chua_dien_dat_duoc"]))

    def test_close_type_khac(self):
        self._kiem_tu_choi([("static CLOSE_TYPE closeType = SLTP;",
                        "static CLOSE_TYPE closeType = CUSTOM_CLOSE_LOGIC;")], "closeType")


class DSLFSS(unittest.TestCase):
    def test_kiem_va_tham_so(self):
        sp = _doc()["co_che"][0]
        ts = NP.tham_so_cua(sp)
        self.assertNotIn("giu", ts)
        self.assertFalse(any("pip" in k for k in ts))
        hong = dict(sp, dong_mo_pip={"tp_pip": -1, "sl_pip": None, "pip_mac_dinh": 0})
        self.assertTrue(NP.kiem_khai_bao(hong))
        self.assertTrue(NP.kiem_khai_bao(dict(sp, ra=sp["vao"])))


if __name__ == "__main__":
    unittest.main()
