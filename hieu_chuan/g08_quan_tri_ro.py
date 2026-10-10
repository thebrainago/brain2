#!/usr/bin/env python3
"""G08 = G-a cua goi ban giao the-brain (file 06): "quan li lenh quyet dinh" - 11/10/2026.

Cau hoi: tren AUDCAD va EURGBP (hai tai san duy nhat hon nhieu chut it o G07, p 0,14 / 0,095 - KHONG dat), CUNG
luoi goc G06/G07 (tin hieu 2023752) nhung DOI CACH QUAN TRI RO (5 bien the dang ky truoc, khong quet) co:
  (a) lai sau phi (spread cao + swap thang) va maxDD < 80 % (luat chu du an) o nam / tai san nao?
  (b) hon chuoi nhieu cung bien do (dao dau tung nen M1) tren CUNG tai san?
  (c) hon luoi goc NHIEU HON muc no "hon goc" tren nhieu (so sanh cap, cung seed)?

    /workspace/venv/bin/python hieu_chuan/g08_quan_tri_ro.py [--nhan 7]

Ke hoach DONG BANG: hieu_chuan/G08_KE_HOACH.json (sha256 in trong ket qua). TAT CA LA MO PHONG.
Dung lai du lieu + chuyen tham so + swap cua G07 (g07_chon_tai_san). Gia khong vao git.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(GOC / "hieu_chuan"))
from nhan.luoi import PIP, ThamSo  # noqa: E402
from nhan.luoi_duong import chay_duong  # noqa: E402
import g06_audcad_2023752 as g06  # noqa: E402
import g07_chon_tai_san as g07  # noqa: E402

KE_HOACH_FILE = GOC / "hieu_chuan" / "G08_KE_HOACH.json"
RA = GOC / "hieu_chuan" / "g08_ket_qua.json"

_TS = g07.KE_HOACH["tham_so"]
KE_HOACH = {
    "gia_thuyet": "06 G-a (the-brain so tay gia thuyet 2): quan tri lenh quyet dinh hon entry. Ban brain2: tren cung luoi "
                  "goc, doi QUAN TRI RO (khoang them tang, so tang toi da, cach dong ro, dung theo gio) co dua AUDCAD/EURGBP "
                  "thanh lai sau phi + DD<80 % va hon nhieu khong? (Phan 'doi entry' cua G-a de sau - xem GHI_CHU.)",
    "luoi_goc": _TS,
    "bien_the": {
        "V0_goc": {"mo_ta": "luoi G06/G07 nguyen ban (doi chung, phai trung G07)"},
        "V1_buoc_rong": {"mo_ta": "khoang them tang x2 (21,2 -> 42,4 pip, he so 1,2 giu)", "tham_so": {"buoc": 42.4}},
        "V2_ro_10": {"mo_ta": "so tang toi da 5 -> 10", "tham_so": {"tran_tang": 10}},
        "V3_duoi_dinh": {"mo_ta": "bo TP 7,6 pip; kich hoat khi gia vuot TB ro + 7,6 pip, dong ca ro khi lui 3,8 pip tu dinh",
                         "duoi": [7.6, 3.8]},
        "V4_chot_usd": {"mo_ta": "bo TP pip; dong ca ro khi lai noi ro >= 1,0 USD (chuoi da nhan k)", "chot_usd": 1.0},
        "V5_dung_5_ngay": {"mo_ta": "luoi goc + dong ca ro tai gia mo nen khi ro song >= 120 gio", "dung_gio": 120.0},
    },
    "tai_san": {m: g07.KE_HOACH["tai_san"][m] for m in ("AUDCAD", "EURGBP")},
    "nam": [2018, 2019, 2020, 2021, 2022, 2024, 2025],
    "nam_ghi_chu": "giong G07 (2023 loai: HistData thieu nen); tu kiem lai do phu bang luat G07",
    "chuyen_tham_so": g07.KE_HOACH["chuyen_tham_so"],
    "thu_tu": "gan_open",
    "von_usd": 10000.0,
    "phi": {"xau": "spread cao + swap thang (dung cho luat va nhieu)", "bao_them": "spread thap + swap"},
    "nhieu": {"kieu": "dao dau tung nen M1 (G06 dao_dau)", "so": 20, "seed_tu": 7000,
              "ghi_chu": "CUNG 20 seed cho moi bien the (so sanh cap)"},
    "luat": {
        "nam_dat_luat_chu": "lai_xau (spread cao + swap) > 0 VA maxDD < 80 % VA khong stop-out; dem tren 7 nam x 2 tai san, "
                            "bao kem ti le nam dat cua NHIEU cung bien the",
        "LAI": "tong 7 nam (xau) > 0 VA moi nam maxDD < 80 % VA khong nam nao stop-out",
        "p_hon": "(1 + #nhieu_tong >= that_tong)/(N+1); HON_NHIEU neu <= 0,05",
        "p_hon_goc": "delta = tong(Vi) - tong(V0) tren gia that; so voi delta cung seed tren nhieu; (1+#>=)/(N+1)",
        "da_kiem": "6 bien the x 2 tai san = 12 phep so voi nhieu; 20 chuoi -> p nho nhat 0,048. Mot o p<=0,05 xay ra "
                   "do may ~46 % -> ket qua dat chi la UNG_VIEN, phai xac nhan tren doan khac truoc khi tin",
        "G_a": {"UNG_VIEN": "co (bien the, tai san) LAI va HON_NHIEU va p_hon_goc <= 0,05",
                "MOT_PHAN": "khong co UNG_VIEN nhung co (bien the, tai san) LAI HOAC HON_NHIEU HOAC p_hon_goc <= 0,05",
                "BAC_BO": "con lai"},
    },
    "khong_lam": "khong quet tham so; khong doi bien the sau khi thay so; khong toi uu theo nam",
}


def bam_ke_hoach() -> str:
    raw = json.dumps(KE_HOACH, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]
    if KE_HOACH_FILE.exists():
        cu = json.loads(KE_HOACH_FILE.read_text())
        if cu.get("sha256_16") != h:
            raise SystemExit(f"KE HOACH DA DOI so voi ban dong bang ({cu.get('sha256_16')} != {h}) - dung")
    else:
        KE_HOACH_FILE.write_text(json.dumps({"sha256_16": h, "ke_hoach": KE_HOACH}, ensure_ascii=False,
                                            indent=1, sort_keys=True) + "\n")
    return h


def ts_bien_the(ten: str) -> tuple[ThamSo, dict]:
    bt = KE_HOACH["bien_the"][ten]
    ts = dataclasses.replace(ThamSo(**KE_HOACH["luoi_goc"]), **bt.get("tham_so", {}))
    kw = {}
    if "duoi" in bt:
        kw["duoi"] = tuple(bt["duoi"])
    if "chot_usd" in bt:
        kw["chot_usd"] = bt["chot_usd"]
    if "dung_gio" in bt:
        kw["dung_gio"] = bt["dung_gio"]
    return ts, kw


_G: dict = {}


def chuan_bi(td: Path) -> dict:
    nams = KE_HOACH["nam"]
    rng = range(min(nams) - 1, max(nams) + 1)
    gia = {m: g07.doc_m1(td, m, rng) for m in KE_HOACH["tai_san"]}
    usdcad = g07.doc_m1(td, "USDCAD", rng)["close"]
    gbpusd = g07.doc_m1(td, "GBPUSD", rng)["close"]
    R = {m: g07.bien_do_ngay(d) for m, d in gia.items()}
    meta = {"k": {}, "spread_pip": {}, "hop_le": {}}
    for m, d in gia.items():
        sn = d.groupby(d.index.year).size()
        tv = float(sn.loc[2018:2025].median())                    # trung vi nhu G07 (2018-2025)
        mua, ban = g07.bang_swap(m)
        for y in nams:
            ok = int(sn.get(y, 0)) >= 0.90 * tv
            meta["hop_le"].setdefault(m, {})[y] = ok
            k = 1.0 if m == "AUDCAD" else float(R["AUDCAD"][y - 1] / R[m][y - 1])
            meta["k"].setdefault(m, {})[y] = k
            meta["spread_pip"].setdefault(m, {})[y] = [s * k / PIP for s in KE_HOACH["tai_san"][m]["spread_gia"]]
            if not ok:
                continue
            dy = d[d.index.year == y] * k
            if m == "AUDCAD":
                dv = usdcad.reindex(dy.index).ffill().bfill().to_numpy(float)
            else:
                dv = 1.0 / gbpusd.reindex(dy.index).ffill().bfill().to_numpy(float)
            _G[(m, y)] = (dy, dv, g06.swap_theo_nen(dy, mua, ban))
    return meta


def _viec(v):
    bt, ma, y, sp, seed = v
    df, dv, sw = _G[(ma, y)]
    if seed is not None:
        df = g06.dao_dau(df, seed)
    ts, kw = ts_bien_the(bt)
    t0 = time.time()
    kq = chay_duong(df, ts, KE_HOACH["von_usd"], KE_HOACH["thu_tu"], sp, quy_doi=dv, swap_nam=sw, **kw)
    nam = kq["ngay"] / 365.25
    kq = {k: (float(x) if isinstance(x, (np.floating, float)) else x) for k, x in kq.items()}
    kq["lai_nam_pct"] = kq["lai_tk"] / KE_HOACH["von_usd"] / nam * 100.0
    kq["giay"] = round(time.time() - t0, 1)
    return {"bt": bt, "ma": ma, "nam": y, "spread_pip": sp, "seed": seed, **kq}


def _dat(r) -> bool:
    return r["lai_tk"] > 0 and r["maxdd_pct"] < 80 and not r["cham_stopout"]


def tong_hop(kq: list, meta: dict) -> dict:
    seeds = sorted({r["seed"] for r in kq if r["seed"] is not None})
    ra = {}
    tong_nh = {}
    for bt in KE_HOACH["bien_the"]:
        for m in KE_HOACH["tai_san"]:
            nams = [y for y, ok in meta["hop_le"][m].items() if ok]
            sp_cao = {y: meta["spread_pip"][m][y][1] for y in nams}
            xau = {y: next(r for r in kq if r["bt"] == bt and r["ma"] == m and r["nam"] == y and r["seed"] is None
                           and r["spread_pip"] == sp_cao[y]) for y in nams}
            thap = {y: next(r for r in kq if r["bt"] == bt and r["ma"] == m and r["nam"] == y and r["seed"] is None
                            and r["spread_pip"] != sp_cao[y]) for y in nams}
            nh = [r for r in kq if r["bt"] == bt and r["ma"] == m and r["seed"] is not None and r["nam"] in nams]
            tn = np.array([sum(r["lai_tk"] for r in nh if r["seed"] == s) for s in seeds])
            tong_nh[(bt, m)] = tn
            tong = sum(r["lai_tk"] for r in xau.values())
            dd = max(r["maxdd_pct"] for r in xau.values())
            so = sum(bool(r["cham_stopout"]) for r in xau.values())
            ra.setdefault(bt, {})[m] = {
                "nam_hop_le": nams, "tong_lai_usd": tong, "maxdd_max_pct": dd, "nam_stopout": so,
                "LAI": bool(tong > 0 and dd < 80 and so == 0),
                "p_hon": float((1 + np.sum(tn >= tong)) / (len(tn) + 1)),
                "nam_dat_luat_chu": [y for y in nams if _dat(xau[y])],
                "trung_vi_pct_nam": float(np.median([r["lai_nam_pct"] for r in xau.values()])),
                "trung_vi_pct_nam_spread_thap": float(np.median([r["lai_nam_pct"] for r in thap.values()])),
                "nhieu": {"n": int(len(tn)), "tong_p5_p50_p95": [float(x) for x in np.percentile(tn, [5, 50, 95])],
                          "ti_le_nam_dat_luat_chu": float(np.mean([_dat(r) for r in nh])),
                          "trung_vi_pct_nam": float(np.median([r["lai_nam_pct"] for r in nh])),
                          "maxdd_max_pct": float(max(r["maxdd_pct"] for r in nh)),
                          "ti_le_nam_stopout": float(np.mean([bool(r["cham_stopout"]) for r in nh]))},
                "theo_nam": {y: {"lai_xau_usd": xau[y]["lai_tk"], "lai_xau_pct_nam": xau[y]["lai_nam_pct"],
                                 "lai_spread_thap_pct_nam": thap[y]["lai_nam_pct"], "maxdd_pct": xau[y]["maxdd_pct"],
                                 "stopout": bool(xau[y]["cham_stopout"]), "so_lenh": xau[y]["so_lenh"],
                                 "so_ro": xau[y]["so_ro"], "tang_max": xau[y]["tang_max"],
                                 "so_duoi": xau[y].get("so_duoi", 0), "so_dung_gio": xau[y].get("so_dung_gio", 0),
                                 "swap_usd": xau[y]["swap_tk"]} for y in nams},
            }
    for bt in KE_HOACH["bien_the"]:
        for m in KE_HOACH["tai_san"]:
            v = ra[bt][m]
            if bt == "V0_goc":
                v["p_hon_goc"] = None
                continue
            d_that = v["tong_lai_usd"] - ra["V0_goc"][m]["tong_lai_usd"]
            d_nh = tong_nh[(bt, m)] - tong_nh[("V0_goc", m)]
            v["delta_goc_usd"] = d_that
            v["delta_goc_nhieu_p5_p50_p95"] = [float(x) for x in np.percentile(d_nh, [5, 50, 95])]
            v["p_hon_goc"] = float((1 + np.sum(d_nh >= d_that)) / (len(d_nh) + 1))
    o = [(bt, m) for bt in ra for m in ra[bt]]
    uv = [f"{bt}/{m}" for bt, m in o if ra[bt][m]["LAI"] and ra[bt][m]["p_hon"] <= 0.05
          and (ra[bt][m]["p_hon_goc"] or 1) <= 0.05]
    mp = [f"{bt}/{m}" for bt, m in o if ra[bt][m]["LAI"] or ra[bt][m]["p_hon"] <= 0.05
          or (ra[bt][m]["p_hon_goc"] or 1) <= 0.05]
    ga = "UNG_VIEN" if uv else ("MOT_PHAN" if mp else "BAC_BO")
    return {"G_a": ga, "ung_vien": uv, "mot_phan": mp, "bien_the": ra}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--histdata", default="/workspace/du_lieu_fx/histdata")
    ap.add_argument("--nhan", type=int, default=7)
    a = ap.parse_args(argv)
    h = bam_ke_hoach()
    t0 = time.time()
    meta = chuan_bi(Path(a.histdata))
    viec = []
    for bt in KE_HOACH["bien_the"]:
        for (m, y) in _G:
            sp = meta["spread_pip"][m][y]
            viec += [(bt, m, y, sp[1], None), (bt, m, y, sp[0], None)]
            viec += [(bt, m, y, sp[1], KE_HOACH["nhieu"]["seed_tu"] + s) for s in range(KE_HOACH["nhieu"]["so"])]
    print(f"ke hoach {h} | {len(viec)} viec | chuan bi {time.time() - t0:.0f}s | hop le {meta['hop_le']}", flush=True)
    with Pool(a.nhan) as p:
        kq = []
        for i, r in enumerate(p.imap_unordered(_viec, viec, chunksize=1)):
            kq.append(r)
            if i % 50 == 0:
                print(f"{i}/{len(viec)} {time.time() - t0:.0f}s", flush=True)
    th = tong_hop(kq, meta)
    out = {"ke_hoach_sha256_16": h, **th, "meta": meta, "giay": round(time.time() - t0, 1),
           "chay": sorted(kq, key=lambda r: (r["bt"], r["ma"], r["nam"], r["seed"] or 0, r["spread_pip"])),
           "nhan": "MO PHONG - khong phai tien that"}
    RA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n")
    print("G-a:", th["G_a"], th["ung_vien"], th["mot_phan"])
    for bt, d in th["bien_the"].items():
        for m, v in d.items():
            print(bt, m, {k: v.get(k) for k in ("LAI", "p_hon", "p_hon_goc", "delta_goc_usd", "tong_lai_usd",
                                                "trung_vi_pct_nam", "trung_vi_pct_nam_spread_thap", "maxdd_max_pct",
                                                "nam_stopout", "nam_dat_luat_chu")})
            print("   nhieu", v["nhieu"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
