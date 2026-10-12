# -*- coding: utf-8 -*-
"""Do phi THAT tu log CSV cua EA demo (ea_demo/*.mq5, phan tach ';').
Cot: thoi_gian;ma;su_kien;khoi_luong;gia;bid;ask;spread_point;swap;hoa_hong;loi;<cot cuoi>
- su_kien 'kiem': anh chup bid/ask -> spread (gia, bps) theo ma va theo gio.
- 'vao'/'ra': khop lenh -> truot gia so voi bid/ask luc ghi; swap + hoa hong cua lenh dong; swap/lot/dem (ghep FIFO vao->ra).
Chay:  python do_phi_xm.py <log1.csv> [log2.csv ...] [--ra ket_qua.json]
Ghi chu: day la so do tren tai khoan DEMO; chi la uoc luong phi that, khong phai ket qua giao dich.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

COT = ["thoi_gian", "ma", "su_kien", "khoi_luong", "gia", "bid", "ask", "spread_point", "swap", "hoa_hong", "loi", "phu"]


def doc(fs):
    ds = []
    for f in fs:
        d = pd.read_csv(f, sep=";", header=None, names=COT, skiprows=1, dtype=str, encoding="latin-1", on_bad_lines="skip")
        ds.append(d)
    d = pd.concat(ds, ignore_index=True)
    d = d[d["su_kien"].isin(["kiem", "vao", "ra"])].copy()
    d["thoi_gian"] = pd.to_datetime(d["thoi_gian"].str.strip(), format="%Y.%m.%d %H:%M", errors="coerce")
    for c in ["khoi_luong", "gia", "bid", "ask", "spread_point", "swap", "hoa_hong", "loi"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.dropna(subset=["thoi_gian"]).sort_values("thoi_gian")


def tom_tat(d):
    out = {}
    for ma, g in d.groupby("ma"):
        k = g[(g["ask"] > 0) & (g["bid"] > 0)]
        sp = k["ask"] - k["bid"]; bps = sp / ((k["ask"] + k["bid"]) / 2) * 1e4
        r = {"so_dong": int(len(g)), "spread_gia_tv": float(sp.median()) if len(sp) else None,
             "spread_bps_tv": float(bps.median()) if len(bps) else None, "spread_bps_p90": float(bps.quantile(0.9)) if len(bps) else None,
             "spread_bps_theo_gio": {int(h): round(float(v), 3) for h, v in bps.groupby(k["thoi_gian"].dt.hour).median().items()} if len(bps) else {}}
        v = g[g["su_kien"] == "vao"]
        # truot: lenh mua khop o gia - ask luc ghi (>0 la bat loi); khong biet chieu -> dung gan nhat trong {bid, ask}
        if len(v):
            lech = np.minimum((v["gia"] - v["ask"]).abs(), (v["gia"] - v["bid"]).abs())
            r["truot_vao_gia_tv"] = float(lech.median()); r["truot_vao_bps_tv"] = float((lech / v["gia"] * 1e4).median())
        ra = g[g["su_kien"] == "ra"]
        r["tong_swap"] = float(ra["swap"].sum()); r["tong_hoa_hong"] = float(g.loc[g["su_kien"].isin(["vao", "ra"]), "hoa_hong"].sum())
        # FIFO vao->ra de tinh swap / lot / dem
        hang = []; lot_dem = 0.0
        for _, x in g[g["su_kien"].isin(["vao", "ra"])].iterrows():
            if x["su_kien"] == "vao": hang.append([x["thoi_gian"], x["khoi_luong"]]); continue
            con = x["khoi_luong"]
            while con > 1e-9 and hang:
                t0, q = hang[0]; m = min(q, con); dem = max((x["thoi_gian"].normalize() - t0.normalize()).days, 0)
                lot_dem += m * dem; con -= m; hang[0][1] -= m
                if hang[0][1] <= 1e-9: hang.pop(0)
        r["lot_dem"] = lot_dem; r["swap_moi_lot_dem"] = float(r["tong_swap"] / lot_dem) if lot_dem > 0 else None
        out[ma] = r
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("log", nargs="+"); ap.add_argument("--ra")
    a = ap.parse_args(argv); kq = tom_tat(doc(a.log))
    s = json.dumps({"nhan": "DO TREN DEMO", "theo_ma": kq}, ensure_ascii=False, indent=1, default=float); print(s)
    if a.ra: open(a.ra, "w", encoding="utf-8").write(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
