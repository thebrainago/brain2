# -*- coding: utf-8 -*-
"""Vong 7 viec (A): chay THU VIEN CO CHE (`nhan/thu_vien_co_che.py`) tren moi EA da dich.

Tieu chi dang ky TRUOC: `reports/vong7_tien_dang_ky_A.md`. Moi o = (EA, to hop manh, cap,
khung); MOI o chay deu ghi ra (ke ca loi / it lenh) de dem so phep thu cho Holm.
Ket qua la MO PHONG (Python, phi XM, du lieu HistData), khong phai tien that.

    python tv_chay.py --ra /duong/dan/o.jsonl [--cap EURUSD,GBPUSD] [--tien-trinh 6]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(LAB / "tru"))

from nhan import cau_kho_ma as CK          # noqa: E402
from nhan import doc_ma as DM              # noqa: E402
from nhan import mo_phong as MP            # noqa: E402
from nhan import mql4_chuan as MQ4         # noqa: E402
from nhan import ngu_phap as NP            # noqa: E402
from nhan import thu_vien_co_che as TV     # noqa: E402
import vong_thu_nghiem as VT               # noqa: E402

DU_LIEU = Path("/workspace/du_lieu_fx")
CAP = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"]
TAN = {"M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h"}
CAT = 0.7


def gom_ea() -> list[dict]:
    """EA dich duoc (co_che khac rong) trong kho - cung cach dem voi bang dem vong 6/7."""
    G = LAB / "data" / "cau_kho"
    bg = []
    for k in ("goi_mql5", "goi_mql4", "goi_github", "ea_ra_co_che"):
        if (G / k).exists():
            bg += CK.gom_tu_thu_muc(G / k)
    co_san = {Path(str(b.get("ten") or "")).name.lower() for b in bg}
    da, ra = set(), []
    for b in bg:
        src = b["src"] or ""
        if not (CK.SAN_KY_TU <= len(src) <= CK.TRAN_KY_TU):
            continue
        vt = CK.van_tay(src)
        if vt in da:
            continue
        da.add(vt)
        m4 = CK.la_mql4(src) or (str(b["ten"]).lower().endswith(".mq4") and
                                 not re.search(r"\bCTrade\b|\bMqlTradeRequest\b", src))
        try:
            if m4:
                d = DM.doc_chien_luoc(MQ4.chuan_hoa(src), nguon=b["ten"])
            else:
                if CK.tep_include_ngoai(src) and CK.tep_thieu_that(src, b.get("nguon") or "",
                                                                   co_san):
                    continue
                _, s = CK.set_cua_goi(b.get("nguon") or "")
                d = DM.doc_chien_luoc(src, nguon=b["ten"], set_ea=s)
        except Exception:                                  # noqa: BLE001
            continue
        if d.get("co_che"):
            ra.append({"ten": str(b["ten"]), "nguon": b.get("nguon"), "co_che": d["co_che"],
                       "khung_ea": d.get("khung_ea")})
    return ra


def doc_cap(cap: str, khung: str) -> pd.DataFrame:
    df = VT.doc_csv(DU_LIEU / f"{cap.lower()}_m5_histdata_server.csv")
    if khung != "M5":
        df = df.resample(TAN[khung], label="left", closed="left").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    return df


def chi_so(loi: np.ndarray, khung: str) -> dict:
    loi = np.nan_to_num(np.asarray(loi, dtype=float))
    nam = len(loi) / VT.BAR_NAM.get(khung, 260)
    sr = VT._sharpe(loi, khung)
    return {"loi_pct": round(float(np.expm1(loi.sum()) * 100), 3), "sharpe": round(sr, 3),
            "maxdd_pct": round(VT._maxdd_pct(loi), 2), "nam": round(nam, 3),
            "t": round(sr * math.sqrt(nam), 3)}


def chay_o(df, specs, manh, cp, khung, diem, cat_tai=CAT):
    chan = [NP.sinh_chan(sp, df) for sp in specs]
    if manh and not TV.ap_duoc(chan):
        return {"bo": "chan RO / khong ap manh"}
    chan = TV.ap_manh(chan, df, manh, diem=diem)
    nk: list = []
    kq = MP.chay_he(df, chan, cp, ma="", khung=khung, diem=diem, nhat_ky=nk)
    loi = np.nan_to_num(np.asarray(kq.loi, dtype=float))
    c = int(len(df) * cat_tai)
    return {"tm": chi_so(loi[:c], khung), "nm": chi_so(loi[c:], khung),
            "toan": chi_so(loi, khung), "so_lenh": int(kq.so_lenh),
            "lenh_tm": sum(1 for x in nk if x.get("bar_vao", -1) < c),
            "lenh_nm": sum(1 for x in nk if x.get("bar_vao", -1) >= c), "loi_bar": loi}


def _viec(arg):
    ea, cap, khung, he_so_spread = arg
    out = []
    try:
        df = doc_cap(cap, khung)
        diem = 1e-3 if cap.endswith("JPY") else 1e-5
        cp = VT.mo_hinh_chi_phi(df, ma=cap)
        if he_so_spread != 1.0:
            cp = cp.bien_the(spread=cp.spread_frac_chung * he_so_spread)
    except Exception as e:                                 # noqa: BLE001
        return [{"ea": ea["ten"], "cap": cap, "khung": khung, "loi": f"du lieu: {e}"[:200]}]
    for manh in TV.to_hop():
        o = {"ea": ea["ten"], "nguon": ea["nguon"], "cap": cap, "khung": khung,
             "manh": "".join(manh) or "goc"}
        try:
            r = chay_o(df, ea["co_che"], manh, cp, khung, diem)
            r.pop("loi_bar", None)
            o.update(r)
        except Exception as e:                             # noqa: BLE001
            o["loi"] = f"{type(e).__name__}: {e}"[:200]
        out.append(o)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", required=True)
    ap.add_argument("--cap", default=",".join(CAP))
    ap.add_argument("--tien-trinh", type=int, default=6)
    ap.add_argument("--loc", default="")
    a = ap.parse_args(argv)
    ds = [e for e in gom_ea() if a.loc in e["ten"]]
    viec = []
    for ea in ds:
        khs = [ea["khung_ea"]] if ea.get("khung_ea") else ["H1"]
        for kh in khs:
            if kh not in TAN:
                continue
            for cap in a.cap.split(","):
                viec.append((ea, cap, kh, 1.0))
    print(f"{len(ds)} EA, {len(viec)} viec x {len(TV.to_hop())} to hop", flush=True)
    t0 = time.time()
    with open(a.ra, "w") as f, Pool(a.tien_trinh) as p:
        for k, out in enumerate(p.imap_unordered(_viec, viec)):
            for o in out:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
            f.flush()
            if k % 20 == 0:
                print(k, round(time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
