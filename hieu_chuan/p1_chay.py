#!/usr/bin/env python3
"""P1 (goi ban giao the-brain): do mo phong luoi cua brain2 voi 15 o MT5 tester SACH.

    python hieu_chuan/p1_chay.py [--du-lieu /workspace/du_lieu_fx]

Dap an: `hieu_chuan/p1_15o_tester.csv` (15 o H1 chat luong lich su 100 %, AUDCAD 8 + NZDCAD 7,
2019.03.01 -> 2019.08.31, Model 0, von 10.000 USD, don bay 100; tester ghi swap = 0; lai/nam
GOM lai/lo chua dong cuoi cua so, quy nam bang ngay/365,25). So lieu tu suy ra, khong co gia,
lenh tho hay ten bot.
Gia: nen H1 BID Dukascopy (cong khai, tai TRUC TIEP cap cheo, khong ghep tu cap USD), doi sang
gio Europe/Helsinki (UTC+2/+3 = gio may chu kieu XM). USDCAD Dukascopy H1 de doi CAD -> USD
tai tung nen. Spread: du lieu cong khai khong co -> chay 1,5 va 2,5 pip (GIA DINH).
Hai mo phong:
  - `v3` = `nhan/luoi.chay` NGUYEN TRANG (them tang o LOW -> tia o HIGH -> TP), tat swap;
  - `duong` = `nhan/luoi_duong.chay_duong` (luat EA, 4 thu tu gia trong nen, lot lam tron 0,01).
Chenh = mo phong - tester (diem %/nam). TAT CA LA MO PHONG; tester cung chi la tester, khong phai tien that.
Ra: hieu_chuan/p1_ket_qua.json + bang in ra man hinh (ban markdown trong P1_KET_QUA.md viet tay tu day).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
from nhan import luoi  # noqa: E402
from nhan.luoi_duong import THU_TU, chay_duong  # noqa: E402

TU, DEN = pd.Timestamp("2019-03-01"), pd.Timestamp("2019-08-31")
NGAY = 184.0
VON = 10_000.0
SPREADS = (1.5, 2.5)
#: khoang giua cac thu tu gia (diem %/nam) vuot nguong nay -> "CHUA DO DUOC" cho o do
NGUONG_KHOANG = 5.0
#: luat phan giai (the-brain NGUONG_PHAN_GIAI): buoc < 2 x bien do nen trung vi -> nen khong
#: phan giai duoc thu tu cham -> nhan canh bao
NGUONG_PHAN_GIAI = 2.0


def doc_gia(thu_muc: Path, ma: str, nguon: str = "histdata", khung: str = "h1") -> pd.DataFrame:
    df = pd.read_csv(thu_muc / f"{ma.lower()}_{khung}_{nguon}_2019.csv", index_col=0, parse_dates=True)
    return df[(df.index >= TU) & (df.index < DEN)]


def chay_v3(df, ts, dv, spread_pip):
    """luoi.chay nguyen trang nhung TAT swap (dem = 0) va doi tien tung nen; + lai/lo treo cuoi."""
    hi, lo, cl = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    sp = np.full(len(df), spread_pip * luoi.PIP)
    dem = np.zeros(len(df))
    chieus = {"mua": (1,), "ban": (-1,), "hai_chieu": (1, -1)}[ts.che_do]
    lai = np.zeros(len(df))
    treo = np.zeros(len(df))
    cuoi = 0.0
    so_lenh = 0
    for c in chieus:
        a, b, k = luoi._mot_ro(hi, lo, cl, sp, dem, c, ts)
        lai += a
        treo += b
        cuoi += sum(c * (cl[-1] - g) * l for g, l in k["vao_cuoi"]) * luoi.HOP_DONG
        so_lenh += k["so_lenh"]
    lai_usd = np.cumsum(np.diff(np.concatenate([[0.0], lai])) / dv)
    eq = VON + lai_usd - treo / dv
    dinh = np.maximum.accumulate(np.maximum(eq, VON))
    dd = float(np.max((dinh - eq) / dinh)) * 100.0
    tong = lai_usd[-1] + cuoi / dv[-1]
    return {"lai_nam_pct": tong / VON / (NGAY / 365.25) * 100.0, "maxdd_pct": dd, "so_lenh": so_lenh}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--du-lieu", default="/workspace/du_lieu_fx")
    ap.add_argument("--nguon", default="histdata", help="histdata (M1 -> H1) | duka")
    ap.add_argument("--khong-m1", action="store_true", help="bo lan chay tren duong M1")
    a = ap.parse_args(argv)
    td = Path(a.du_lieu)
    gia = {m: doc_gia(td, m, a.nguon) for m in ("AUDCAD", "NZDCAD")}
    usdcad = doc_gia(td, "USDCAD", a.nguon)["close"]
    co_m1 = a.nguon == "histdata" and not a.khong_m1
    if co_m1:
        m1 = {m: doc_gia(td, m, a.nguon, "m1") for m in ("AUDCAD", "NZDCAD")}
        usdcad_m1 = doc_gia(td, "USDCAD", a.nguon, "m1")["close"]
    nguon = {m: {"so_nen": len(d), "tu": str(d.index[0]), "den": str(d.index[-1]),
                 "bien_do_nen_trung_vi_pip": round(float(((d.high - d.low) / luoi.PIP).median()), 1)}
             for m, d in gia.items()}
    rows = list(csv.DictReader(open(GOC / "hieu_chuan" / "p1_15o_tester.csv", encoding="utf-8")))
    out = []
    for r in rows:
        ts = luoi.ThamSo(**json.loads(r["tham_so_json"]))
        df = gia[r["ma"]]
        dv = usdcad.reindex(df.index).ffill().bfill().to_numpy(float)
        o = {"o": int(r["o"]), "ma": r["ma"], "che_do": ts.che_do, "buoc": ts.buoc, "tp": ts.tp,
             "tran_tang": ts.tran_tang, "lot": ts.lot, "kieu_lot": ts.kieu_lot, "he_so_lot": ts.he_so_lot,
             "tia": ts.tia_lenh, "bien_cap": ts.bien_cap,
             "tester": {"lai_nam_pct": float(r["tester_lai_nam_pct"]), "maxdd_pct": float(r["tester_dd_pct"]),
                        "so_lenh": int(r["tester_so_lenh"])},
             "the_brain_v3_bo_swap": round(float(r["engine_lai_nam_pct"]) - float(r["engine_swap_nam_pct"]), 3),
             "v3": {}, "duong": {}}
        for s in SPREADS:
            o["v3"][str(s)] = chay_v3(df, ts, dv, s)
            for t in THU_TU:
                kq = chay_duong(df, ts, VON, t, s, quy_doi=dv)
                kq["lai_nam_pct"] = kq["lai_tk"] / VON / (NGAY / 365.25) * 100.0
                o["duong"][f"{t}|{s}"] = kq
        if co_m1:
            # duong M1 (gan_open trong tung phut): mo phong cung luat tren do phan giai cao hon 60 lan -
            # do PHAN do lech do nen H1 an duong di (van khong phai tick)
            d1 = m1[r["ma"]]
            dv1 = usdcad_m1.reindex(d1.index).ffill().bfill().to_numpy(float)
            for s in SPREADS:
                kq = chay_duong(d1, ts, VON, "gan_open", s, quy_doi=dv1)
                kq["lai_nam_pct"] = kq["lai_tk"] / VON / (NGAY / 365.25) * 100.0
                o.setdefault("m1", {})[str(s)] = kq
        T = o["tester"]["lai_nam_pct"]
        v3 = [o["v3"][str(s)]["lai_nam_pct"] - T for s in SPREADS]
        du = [v["lai_nam_pct"] - T for v in o["duong"].values()]
        o["chenh_v3"] = [min(v3), max(v3)]
        o["chenh_duong"] = [min(du), max(du)]
        if co_m1:
            mm = [o["m1"][str(s)]["lai_nam_pct"] - T for s in SPREADS]
            o["chenh_m1"] = [min(mm), max(mm)]
        khoang_thu_tu = max(
            max(o["duong"][f"{t}|{s}"]["lai_nam_pct"] for t in THU_TU)
            - min(o["duong"][f"{t}|{s}"]["lai_nam_pct"] for t in THU_TU) for s in SPREADS)
        o["khoang_thu_tu"] = khoang_thu_tu
        o["phan_giai_kem"] = ts.buoc < NGUONG_PHAN_GIAI * nguon[r["ma"]]["bien_do_nen_trung_vi_pip"]
        o["duong_do_duoc"] = khoang_thu_tu <= NGUONG_KHOANG
        out.append(o)
    # tom tat
    def _tt(ds, key):
        x = [d[key] for d in ds]
        return {"n": len(x), "min": min(v[0] for v in x), "max": max(v[1] for v in x),
                "trung_vi_giua": float(np.median([(v[0] + v[1]) / 2 for v in x]))}
    tia = [d for d in out if d["tia"]]
    ko = [d for d in out if not d["tia"]]
    tom = {"v3_co_tia": _tt(tia, "chenh_v3"), "v3_khong_tia": _tt(ko, "chenh_v3"),
           "duong_co_tia": _tt(tia, "chenh_duong"), "duong_khong_tia": _tt(ko, "chenh_duong"),
           **({"m1_co_tia": _tt(tia, "chenh_m1"), "m1_khong_tia": _tt(ko, "chenh_m1")} if co_m1 else {}),
           "duong_chua_do_duoc": [d["o"] for d in out if not d["duong_do_duoc"]],
           "v3_lac_quan_o": sum(d["chenh_v3"][0] > 0 for d in out),
           "duong_lac_quan_o": sum(d["chenh_duong"][0] > 0 for d in out)}
    def spearmanr(x, y):
        return (pd.Series(x).rank().corr(pd.Series(y).rank()),)
    tv = [d["tester"]["lai_nam_pct"] for d in out]
    tom["spearman_v3"] = float(spearmanr(tv, [d["v3"]["1.5"]["lai_nam_pct"] for d in out])[0])
    tom["spearman_duong_gan_open_1.5"] = float(spearmanr(tv, [d["duong"]["gan_open|1.5"]["lai_nam_pct"] for d in out])[0])
    tom["spearman_the_brain_v3"] = float(spearmanr(tv, [d["the_brain_v3_bo_swap"] for d in out])[0])
    if co_m1:
        tom["spearman_m1_1.5"] = float(spearmanr(tv, [d["m1"]["1.5"]["lai_nam_pct"] for d in out])[0])
    ra = {"nguon_gia": nguon, "nguon": a.nguon, "spreads_pip": SPREADS, "nguong_khoang": NGUONG_KHOANG,
          "o": out, "tom_tat": tom, "nhan": "MO PHONG vs TESTER MT5 - khong phai tien that"}
    (GOC / "hieu_chuan" / "p1_ket_qua.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1, default=float),
                                                       encoding="utf-8")
    print(json.dumps(nguon, ensure_ascii=False))
    print("| o | ma | che_do | buoc/tp/tang | lot (he) | tia | tester lai·DD·lenh | the-brain v3 | brain2 v3 (1.5/2.5) | chenh v3 | duong min..max | chenh duong | khoang thu tu | DD v3 / duong(gan_open,1.5) / M1 | lenh v3 / duong / M1 | chenh M1 |")
    for d in out:
        T = d["tester"]
        v15, v25 = d["v3"]["1.5"], d["v3"]["2.5"]
        dv_ = [v["lai_nam_pct"] for v in d["duong"].values()]
        g = d["duong"]["gan_open|1.5"]
        print(f"| {d['o']} | {d['ma']} | {d['che_do']} | {d['buoc']:g}/{d['tp']:g}/{d['tran_tang']} | {d['lot']:g} ({d['he_so_lot']:g}) | "
              f"{'co' if d['tia'] else '-'} | {T['lai_nam_pct']:+.1f}·{T['maxdd_pct']:.1f}·{T['so_lenh']} | {d['the_brain_v3_bo_swap']:+.1f} | "
              f"{v15['lai_nam_pct']:+.1f}/{v25['lai_nam_pct']:+.1f} | {d['chenh_v3'][0]:+.1f}..{d['chenh_v3'][1]:+.1f} | "
              f"{min(dv_):+.1f}..{max(dv_):+.1f} | {d['chenh_duong'][0]:+.1f}..{d['chenh_duong'][1]:+.1f} | "
              f"{d['khoang_thu_tu']:.1f}{'' if d['duong_do_duoc'] else ' CHUA DO DUOC'}{' (phan giai kem)' if d['phan_giai_kem'] else ''} | "
              f"{v15['maxdd_pct']:.1f} / {g['maxdd_pct']:.1f} / {d['m1']['1.5']['maxdd_pct'] if co_m1 else float('nan'):.1f} | "
              f"{v15['so_lenh']} / {g['so_lenh']} / {d['m1']['1.5']['so_lenh'] if co_m1 else '-'} | "
              f"{(str(round(d['chenh_m1'][0], 1)) + '..' + str(round(d['chenh_m1'][1], 1))) if co_m1 else '-'} |")
    print(json.dumps(tom, ensure_ascii=False, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
