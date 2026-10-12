# -*- coding: utf-8 -*-
"""Vong 8: thu vien co che tren H1 gop tu TICK bid/ask (spread THAT). Dang ky truoc:
reports/vong8_tien_dang_ky_spread.md. MO PHONG.

    python tv_spread.py --ra o.jsonl [--mot-lan] [--nhan]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import tv_chay as TC                        # noqa: E402
import vong_thu_nghiem as VT                # noqa: E402
from nhan import thu_vien_co_che as TV      # noqa: E402

DU = Path("/workspace/du_lieu_fx")


def doc_tick_h1(cap: str) -> pd.DataFrame:
    return pd.read_csv(DU / f"{cap.lower()}_h1_tick_ba_ny7.csv", index_col=0, parse_dates=True)


def chi_phi_that(df: pd.DataFrame, cap: str, kieu: str = "cong", mot_lan: bool = False):
    ohlc = df[["open", "high", "low", "close"]]
    cp = VT.mo_hinh_chi_phi(ohlc, ma=cap)
    raw = (df["spread_open"] / df["open"]).clip(lower=0)
    tb_xm = float(np.mean(cp.spread_mang(ohlc.index)))
    if kieu == "cong":
        xm = raw + (tb_xm - float(raw.mean()))
    else:
        xm = raw * (tb_xm / float(raw.mean()))
    cp = cp.bien_the(spread_frac_bar=xm.clip(lower=0), spread_mot_lan=mot_lan)
    return ohlc, cp, {"xm_tb_frac": tb_xm, "that_tb_frac": float(raw.mean()),
                      "markup_frac": tb_xm - float(raw.mean())}


def _viec(arg):
    ea, cap, kieu, mot_lan, chi_s, he_so, chon, loc = arg
    out = []
    try:
        df = doc_tick_h1(cap)
        ohlc, cp, info = chi_phi_that(df, cap, kieu, mot_lan)
        if he_so != 1.0:
            cp = cp.bien_the(spread=cp.spread_frac_chung * he_so)
        diem = 1e-3 if cap.endswith("JPY") else 1e-5
    except Exception as e:                                  # noqa: BLE001
        return [{"ea": ea["ten"], "cap": cap, "loi": f"du lieu: {e}"[:200]}]
    th = TV.to_hop()
    if chi_s:
        th = [x for x in th if len(x) <= 1 and x in ((), ("S",))]
    if chon == "moi":                                       # vong 9: chi to hop co B hoac R
        th = [x for x in th if "B" in x or "R" in x]
    elif chon == "cu":
        th = [x for x in th if "B" not in x and "R" not in x]
    if loc is not None:
        th = [x for x in th if ("".join(x) or "goc") in loc.get((ea["ten"], cap), ())]
    for manh in th:
        o = {"ea": ea["ten"], "cap": cap, "khung": "H1", "manh": "".join(manh) or "goc",
             "kieu_spread": kieu, "mot_lan": mot_lan, "he_so_spread": he_so}
        try:
            r = TC.chay_o(ohlc, ea["co_che"], manh, cp, "H1", diem)
            r.pop("loi_bar", None)
            o.update(r)
        except Exception as e:                              # noqa: BLE001
            o["loi"] = f"{type(e).__name__}: {e}"[:200]
        out.append(o)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", required=True)
    ap.add_argument("--mot-lan", action="store_true", help="(vong 8) - tu vong 9 la mac dinh")
    ap.add_argument("--hai-lan", action="store_true", help="stress: spread 2 lan / khu hoi (cu)")
    ap.add_argument("--he-so-spread", type=float, default=1.0)
    ap.add_argument("--to-hop", choices=("tat", "moi", "cu"), default="cu")
    ap.add_argument("--loc", help="jsonl o (ea, cap, manh) - chi chay lai cac o nay")
    ap.add_argument("--nhan", action="store_true", help="mo hinh spread NHAN (do nhay, chi goc/S)")
    ap.add_argument("--tien-trinh", type=int, default=6)
    ap.add_argument("--gom", help="pickle danh sach EA da gom (tv_chay.gom_ea) - chay lai nhanh")
    a = ap.parse_args(argv)
    if a.gom:
        import pickle
        tat = pickle.load(open(a.gom, "rb"))
    else:
        tat = TC.gom_ea()
    ds = [e for e in tat if (e.get("khung_ea") or "H1") == "H1"]
    loc = None
    if a.loc:
        loc = {}
        for x in map(json.loads, open(a.loc)):
            loc.setdefault((x["ea"], x["cap"]), set()).add(x["manh"])
    viec = [(e, c, "nhan" if a.nhan else "cong", not a.hai_lan, a.nhan, a.he_so_spread, a.to_hop, loc)
            for e in ds for c in TC.CAP if loc is None or (e["ten"], c) in loc]
    print(len(ds), "EA H1,", len(viec), "viec", flush=True)
    t0 = time.time()
    with open(a.ra, "w") as f, Pool(a.tien_trinh) as p:
        for k, out in enumerate(p.imap_unordered(_viec, viec)):
            for o in out:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
            if k % 20 == 0:
                print(k, round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
