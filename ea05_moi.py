# -*- coding: utf-8 -*-
"""Vong 8: kiem ung vien EA05_MACD_Momentum NZDUSD H1 + loc phien P tren DU LIEU MOI.
Tieu chi dang ky truoc: reports/vong8_tien_dang_ky_EA05.md (commit 61f9fb9b). MO PHONG.

    python ea05_moi.py CSV_M5_HOAC_H1 [--ra reports/vong8_ea05_moi.json] [--nhan TEN]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
from nhan import cau_kho_ma as CK          # noqa: E402
from nhan import doc_ma as DM              # noqa: E402
import tv_chay as TC                       # noqa: E402
import vong_thu_nghiem as VT               # noqa: E402

EA = LAB / "data/cau_kho/goi_github/diayuunr__ea-optimization-project__EA05_MACD_Momentum_EA05_MACD_Momentum/EA05_MACD_Momentum.mq5"


def doc_specs():
    src = EA.read_text(encoding="utf-8", errors="ignore")
    _, s = CK.set_cua_goi("tep:" + str(EA))
    return DM.doc_chien_luoc(src, nguon=EA.name, set_ea=s)["co_che"]


def h1(df):
    if len(df) > 1 and (df.index[1] - df.index[0]).total_seconds() < 3600:
        agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
        for c in ("spread_open",):
            if c in df.columns:
                agg[c] = "first"
        df = df.resample("1h", label="left", closed="left").agg(agg).dropna(subset=["open"])
    return df


def kiem(df, specs, he_so_spread=1.0, spread_that=False):
    cp = VT.mo_hinh_chi_phi(df[["open", "high", "low", "close"]], ma="NZDUSD")
    if he_so_spread != 1.0:
        cp = cp.bien_the(spread=cp.spread_frac_chung * he_so_spread)
    if spread_that:
        from nhan import chi_phi as CP
        cp = CP.voi_spread_mang(cp, df["spread_open"].to_numpy() / df["open"].to_numpy()
                                * he_so_spread, df.index)
    nk = []
    r = TC.chay_o(df, specs, ("P",), cp, "H1", 1e-5)
    loi = r.pop("loi_bar")
    nam = {}
    for y in sorted(set(df.index.year)):
        m = np.asarray(df.index.year == y)
        nam[int(y)] = round(float(np.expm1(loi[m].sum()) * 100), 3)
    t = r["toan"]["t"]
    p = 0.5 * math.erfc(t / math.sqrt(2))
    return {"toan": r["toan"], "so_lenh": r["so_lenh"], "p": p, "theo_nam": nam}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--ra")
    ap.add_argument("--spread-that", action="store_true")
    a = ap.parse_args(argv)
    df = h1(VT.doc_csv(Path(a.csv)) if not a.spread_that else
            __import__("pandas").read_csv(a.csv, index_col=0, parse_dates=True))
    specs = doc_specs()
    goc = kiem(df, specs, spread_that=a.spread_that)
    x15 = kiem(df, specs, 1.5, spread_that=a.spread_that)
    tc = {"1_lai_va_dd": goc["toan"]["loi_pct"] > 0 and goc["toan"]["maxdd_pct"] < 80,
          "2_lenh_ge_50": goc["so_lenh"] >= 50,
          "3_p_lt_005": goc["p"] < 0.05,
          "4_nam_lai_ge_4_6": sum(v > 0 for v in goc["theo_nam"].values()) >= 4,
          "5_spread_x15_lai": x15["toan"]["loi_pct"] > 0}
    ra = {"du_lieu": a.csv, "so_bar_h1": len(df), "tu": str(df.index[0]), "den": str(df.index[-1]),
          "so_chan": len(specs), "goc": goc, "spread_x1_5": x15, "tieu_chi": tc,
          "song": all(tc.values()), "nhan": "MO PHONG"}
    print(json.dumps(ra, ensure_ascii=False, indent=1))
    if a.ra:
        json.dump(ra, open(a.ra, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
