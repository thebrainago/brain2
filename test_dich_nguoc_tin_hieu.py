# -*- coding: utf-8 -*-
"""Bai kiem dich nguoc tin hieu cong khai (FXBlue CSV + loc + dac trung)."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

LAB = Path(__file__).resolve().parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from nhan import thu_thap_tin_hieu_cong_khai as TT  # noqa: E402
from nhan import dich_nguoc_tin_hieu as DN  # noqa: E402


def _viet_csv(duong: Path, rows: list[dict]) -> None:
    cols = ["Type", "Ticket", "Symbol", "Lots", "Buy/sell", "Open price", "Close price",
            "Open time", "Close time", "Open date", "Close date", "Profit", "Swap",
            "Commission", "Net profit", "T/P", "S/L", "Pips", "Result",
            "Trade duration (hours)"]
    with duong.open("w", encoding="utf-8", newline="") as f:
        f.write("sep=,\n")
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def _hang(ticket, sym, lots, bs, ot, ct, sl, tp, profit, giu=1.0):
    return {
        "Type": "Closed position", "Ticket": ticket, "Symbol": sym, "Lots": lots,
        "Buy/sell": bs, "Open price": "1.10000", "Close price": "1.10100",
        "Open time": ot, "Close time": ct, "Open date": ot[:10].replace("/", "-"),
        "Close date": ct[:10].replace("/", "-"), "Profit": profit, "Swap": "0",
        "Commission": "0", "Net profit": profit, "T/P": tp, "S/L": sl,
        "Pips": "10", "Result": "1", "Trade duration (hours)": giu,
    }


class TestDocCsv(unittest.TestCase):
    def test_doc_fxblue_co_sl(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.csv"
            _viet_csv(p, [
                _hang("1", "EURUSD", "0.1", "Buy", "2024/01/02 10:00:00",
                      "2024/01/02 12:00:00", "1.09000", "1.12000", "10"),
                _hang("2", "EURUSD", "0.1", "Sell", "2024/01/03 10:00:00",
                      "2024/01/03 11:00:00", "1.11000", "1.08000", "5"),
            ])
            trades = TT.doc_csv_fxblue(p, he_id="t")
            self.assertEqual(len(trades), 2)
            self.assertEqual(trades[0]["chieu"], 1)
            self.assertEqual(trades[1]["chieu"], -1)
            self.assertIsNotNone(trades[0]["sl"])
            self.assertTrue(trades[0]["luc_vao"].startswith("2024-01-02"))

    def test_bo_deposit_va_pending(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "b.csv"
            rows = [_hang("1", "EURUSD", "0.1", "Buy", "2024/01/02 10:00:00",
                          "2024/01/02 12:00:00", "1.09", "1.12", "10")]
            rows.append({"Type": "Deposit", "Ticket": "0", "Symbol": "", "Lots": "",
                         "Buy/sell": "", "Open price": "", "Close price": "",
                         "Open time": "2024/01/01 00:00:00", "Close time": "",
                         "Open date": "", "Close date": "", "Profit": "1000",
                         "Swap": "", "Commission": "", "Net profit": "1000",
                         "T/P": "", "S/L": "", "Pips": "", "Result": "",
                         "Trade duration (hours)": ""})
            _viet_csv(p, rows)
            self.assertEqual(len(TT.doc_csv_fxblue(p, he_id="t")), 1)


class TestLoc(unittest.TestCase):
    def test_martingale(self):
        trades = []
        for i, lot in enumerate([0.1, 0.2, 0.4]):
            trades.append({
                "symbol": "EURUSD", "chieu": 1, "lot": lot,
                "luc_vao": "2024-01-0%dT10:00:00Z" % (i + 1),
                "loi": -10.0 if i < 2 else 20.0, "sl": 1.09,
            })
        co = DN.phat_hien_martingale_grid(trades)
        self.assertTrue(co["martingale"])

    def test_khong_sl(self):
        trades = [{"symbol": "XAUUSD", "chieu": 1, "lot": 0.1,
                   "luc_vao": "2024-01-01T10:00:00Z", "loi": 1, "sl": None}
                  for _ in range(10)]
        co = DN.phat_hien_martingale_grid(trades)
        self.assertTrue(co["khong_sl"])
        qd = DN.loc_he(trades, tu_choi_nguy_hiem=True)
        self.assertEqual(qd["quyet_dinh"], "tu_choi")

    def test_chap_nhan_co_sl(self):
        trades = []
        for i in range(10):
            trades.append({
                "symbol": "EURUSD", "chieu": 1 if i % 2 == 0 else -1, "lot": 0.1,
                "luc_vao": "2024-02-%02dT08:00:00Z" % (i + 1),
                "loi": 1.0, "sl": 1.09,
            })
        qd = DN.loc_he(trades, tu_choi_nguy_hiem=True)
        self.assertEqual(qd["quyet_dinh"], "chap_nhan")
        self.assertFalse(qd["martingale"])


class TestDacTrung(unittest.TestCase):
    def test_tai_tao_voi_parquet_synthetic(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            # synthetic H1
            idx = pd.date_range("2024-01-01", periods=200, freq="h", tz="UTC")
            close = 1.1 + np.cumsum(np.random.default_rng(0).normal(0, 0.0005, size=len(idx)))
            df = pd.DataFrame({
                "time": idx, "open": close, "high": close + 0.0008,
                "low": close - 0.0008, "close": close, "tick_volume": 100.0, "spread": 10.0,
            })
            df.to_parquet(td / "EURUSD_H1.parquet")
            trades = [{
                "ticket": "1", "symbol": "EURUSD", "chieu": 1, "lot": 0.1,
                "gia_vao": float(close[100]), "gia_ra": float(close[102]),
                "luc_vao": "2024-01-05T04:30:00Z", "luc_ra": "2024-01-05T06:00:00Z",
                "sl": float(close[100]) - 0.005, "tp": float(close[100]) + 0.01,
                "loi": 5.0, "giu_gio": 1.5,
            }]
            dac = DN.tai_tao_dac_trung(trades, kho_gia=td)
            self.assertEqual(len(dac), 1)
            self.assertIn(dac[0]["phien"], ("asia", "london", "ny", "late"))
            self.assertFalse(dac[0]["vao"].get("thieu_gia"))
            self.assertIn(dac[0]["vao"].get("trend"), ("len", "xuong", "ngang"))
            ho = DN.tong_hop_ho_so(trades, dac, DN.loc_he(trades, tu_choi_nguy_hiem=False))
            nhac = DN.tao_nhac_dich_boc(ho, nguon="fxblue", he_id="t")
            self.assertIn("HO SO:", nhac)
            self.assertNotIn("<html", nhac.lower())
            self.assertIn("spec", nhac)


class TestHangChoFormat(unittest.TestCase):
    def test_xep_hang_ghi_file(self):
        from nhan import hang_cho_llm as HCL
        # dùng prompt độc nhất để không đụng request khác
        trades = [{
            "symbol": "EURUSD", "chieu": 1, "lot": 0.1,
            "luc_vao": "2024-03-01T10:00:00Z", "loi": 1.0, "sl": 1.09, "giu_gio": 2,
        } for _ in range(8)]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            idx = pd.date_range("2024-01-01", periods=300, freq="h", tz="UTC")
            close = np.linspace(1.08, 1.12, len(idx))
            pd.DataFrame({
                "time": idx, "open": close, "high": close + 0.001,
                "low": close - 0.001, "close": close, "tick_volume": 1.0, "spread": 1.0,
            }).to_parquet(td / "EURUSD_H1.parquet")
            # stub thu muc goc
            old = TT.thu_muc_goc
            TT.thu_muc_goc = lambda: td / "tin"  # type: ignore
            try:
                # nhac phai unique
                uniq = "test_dich_nguoc_%s" % Path(td).name
                dac = DN.tai_tao_dac_trung(trades, kho_gia=td)
                loc = DN.loc_he(trades, tu_choi_nguy_hiem=False)
                ho = DN.tong_hop_ho_so(trades, dac, loc)
                nhac = DN.tao_nhac_dich_boc(ho, nguon="fxblue", he_id=uniq)
                kq = HCL.xep_hang("dich_boc", DN.HE_THONG_DICH, nhac,
                                  tru="test_dich_nguoc", ep_json=True)
                self.assertIn(kq["trang_thai"], ("CHO", "OK"))
                self.assertTrue(kq.get("id"))
                p = HCL.duong_cho(kq["id"])
                # có thể đã có xong từ lần trước cùng hash — nếu CHO thì file tồn tại
                if kq["trang_thai"] == "CHO":
                    self.assertTrue(p.exists())
                    d = __import__("json").loads(p.read_text(encoding="utf-8"))
                    self.assertEqual(d["loai_viec"], "dich_boc")
                    self.assertIn("HO SO", d["nhac"])
            finally:
                TT.thu_muc_goc = old


if __name__ == "__main__":
    unittest.main()
