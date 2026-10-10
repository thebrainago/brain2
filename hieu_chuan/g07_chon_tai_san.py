#!/usr/bin/env python3
"""G07 = G-b cua goi ban giao the-brain (file 06 / so tay gia thuyet 3) - 11/10/2026.

Cau hoi: CUNG mot bo luat luoi (cai dat 2023752 cua G06: buoc 21,2 pip x1,2, lot cong 0,25, TP 7,6, tia lenh,
5 tang, hai chieu) co lai sau phi (spread + swap thang) va maxDD < 80 % tren tai san "hoi quy" (cap cheo FX
AUDCAD, EURGBP; vang XAUUSD) nhung KHONG tren chi so (NASDAQ 100, S&P 500)? Va hon / kem chuoi nhieu cung
bien do (dao dau tung nen M1) tren CUNG tai san?

Chuyen tham so giua tai san (khong toi uu): moi nam y, gia tai san nhan k_y = R_AUDCAD(y-1) / R_ts(y-1),
R = trung vi bien do ngay (cao-thap theo ngay gio Helsinki) cua NAM TRUOC (khong nhin truoc). Buoc/TP/bien
tinh bang pip cua chuoi da nhan -> cung so "bien do ngay" moi tang nhu AUDCAD. Nhan gia giu nguyen %
bien dong; spread nhan cung k. AUDCAD: k = 1 (giong het G06, kiem cheo).

    /workspace/venv/bin/python hieu_chuan/g07_chon_tai_san.py [--so-nhieu 20] [--nhan 7]

Ke hoach DONG BANG: hieu_chuan/G07_KE_HOACH.json (sha256 in trong ket qua). TAT CA LA MO PHONG.
Gia HistData.com M1 (BID, EST -> gio Helsinki). Gia khong vao git.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
import zipfile
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(GOC / "hieu_chuan"))
from nhan.luoi import PIP, ThamSo  # noqa: E402
from nhan.luoi_duong import chay_duong  # noqa: E402
import g06_audcad_2023752 as g06  # noqa: E402

KE_HOACH_FILE = GOC / "hieu_chuan" / "G07_KE_HOACH.json"
RA = GOC / "hieu_chuan" / "g07_ket_qua.json"
LS_USD_EUR = GOC / "config" / "lai_suat_qua_dem_thang.csv"
LS_AUD_CAD = GOC / "config" / "lai_suat_aud_cad_thang.csv"
LS_GBP = GOC / "config" / "lai_suat_gbp_thang.csv"

KE_HOACH = {
    "gia_thuyet": "06 G-b / so tay the-brain gt_f0724d5962ceeda2 (id 3): luat luoi co lai sau phi + DD<80 % tren tai san hoi "
                  "quy (cap cheo FX, vang), KHONG co lai tren chi so (xu huong). Goi y the-brain (PMG 14/09: AUDCAD/EURGBP 8/8, "
                  "vang 7/8, US100 0/8) chi la goi y.",
    "tham_so": g06.KE_HOACH["tham_so"],
    "von_usd": 10000.0,
    "nam": [2018, 2025],
    "tai_san": {
        "AUDCAD": {"nhom": "hoi_quy", "quy_doi": "USDCAD", "spread_gia": [0.00015, 0.00028], "swap": "G06 (r_AUD-r_CAD, markup XM 13/09/2026)"},
        "EURGBP": {"nhom": "hoi_quy", "quy_doi": "1/GBPUSD", "spread_gia": [0.0001, 0.0002], "swap": "(r_EUR-r_GBP) thang, markup FXCE 22/08/2026"},
        "XAUUSD": {"nhom": "hoi_quy", "quy_doi": "1", "spread_gia": [0.2, 0.4], "swap": "mua -r_USD, ban +r_USD, markup FXCE 22/08/2026 (bo lease)"},
        "NSXUSD": {"nhom": "chi_so", "quy_doi": "1", "spread_gia": [1.0, 2.0], "swap": "GIA DINH mua -(r_USD+2,5 %), ban +(r_USD-2,5 %) (bo co tuc)"},
        "SPXUSD": {"nhom": "chi_so", "quy_doi": "1", "spread_gia": [0.4, 0.8], "swap": "GIA DINH mua -(r_USD+2,5 %), ban +(r_USD-2,5 %) (bo co tuc)"},
    },
    "chuyen_tham_so": "k_y = R_AUDCAD(y-1)/R_ts(y-1), R = trung vi (cao-thap ngay Helsinki, ngay >= 600 nen M1); AUDCAD k=1",
    "thu_tu": "gan_open (M1: G06 do 4 thu tu lech <= 0,1 %/nam)",
    "bien_the": ["spread thap + swap", "spread cao + swap", "spread thap khong swap (chi bao)"],
    "nhieu": {"kieu": "dao dau tung nen M1 (G06 dao_dau)", "so": 20, "seed_tu": 7000, "bien_the": "spread cao + swap"},
    "do_phu": "nam bi loai neu so nen M1 < 0,90 x trung vi so nen/nam cua tai san; tai san < 5 nam hop le -> CHUA_DO_DUOC",
    "luat_tai_san": {
        "LAI": "tong lai (bien the xau nhat co swap, cong cac nam) > 0 VA moi nam maxDD < 80 % VA khong nam nao stop-out",
        "p_hon": "(1 + #nhieu_tong >= that_tong)/(N+1) <= 0,05 -> HON_NHIEU",
        "p_kem": "(1 + #nhieu_tong <= that_tong)/(N+1) <= 0,05 -> KEM_NHIEU",
        "bao_them": "ti le nam lai, trung vi %/nam, maxDD lon nhat, so nam stop-out, cung so lieu cho nhieu",
    },
    "luat_G_b": {
        "UNG_HO": "moi tai san hoi_quy LAI va HON_NHIEU; moi chi_so KHONG LAI",
        "BAC_BO": "khong tai san hoi_quy nao LAI, HOAC khong tai san hoi_quy nao HON_NHIEU",
        "MOT_PHAN": "con lai (ghi ro tai san nao dat gi)",
    },
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


def doc_m1(td: Path, ma: str, nam: range) -> pd.DataFrame:
    kho = g06.CACHE / f"g07_{ma.lower()}_m1.pkl"
    if kho.exists():
        return pd.read_pickle(kho)
    phan = []
    for y in nam:
        with zipfile.ZipFile(td / f"DAT_ASCII_{ma}_M1_{y}.zip") as z:
            ten = [t for t in z.namelist() if t.endswith(".csv")][0]
            d = pd.read_csv(io.BytesIO(z.read(ten)), sep=";", header=None,
                            names=["t", "open", "high", "low", "close", "v"])
        t = pd.to_datetime(d["t"], format="%Y%m%d %H%M%S") + pd.Timedelta(hours=5)
        d.index = t.dt.tz_localize("UTC").dt.tz_convert("Europe/Helsinki").dt.tz_localize(None)
        phan.append(d[["open", "high", "low", "close"]].astype("float64"))
    df = pd.concat(phan).sort_index()
    df = df[~df.index.duplicated()]
    df.index.name = "time"
    df.to_pickle(kho)
    return df


def bien_do_ngay(df: pd.DataFrame) -> pd.Series:
    """R theo nam = trung vi (max high - min low) cac ngay co >= 600 nen M1."""
    g = df.groupby(df.index.normalize())
    r = pd.DataFrame({"r": g["high"].max() - g["low"].min(), "n": g.size()})
    r = r[r["n"] >= 600]
    return r["r"].groupby(r.index.year).median()


def _lai_suat() -> pd.DataFrame:
    a = pd.read_csv(LS_USD_EUR, index_col=0)[["USD", "EUR"]]
    b = pd.read_csv(LS_AUD_CAD, index_col=0)
    c = pd.read_csv(LS_GBP, index_col=0)
    ls = a.join(b, how="outer").join(c, how="outer") / 100.0
    ls.index = pd.PeriodIndex(ls.index, freq="M")
    return ls.ffill()


# do 22/08/2026 (config/chi_phi_do.json, FXCE): phi_nam (duong = mat) -> thu nhap = -phi
_DO_FXCE = {"EURGBP": (-0.0305, 0.00439), "XAUUSD": (-0.04477, 0.03709)}


def bang_swap(ma: str) -> tuple[pd.Series, pd.Series]:
    if ma == "AUDCAD":
        mua, ban, _ = g06.bang_swap()
        return mua, ban
    ls = _lai_suat()
    if ma == "EURGBP":
        cong = ls["EUR"] - ls["GBP"]
    else:
        cong = -ls["USD"]
    if ma in _DO_FXCE:
        t = pd.Period("2026-08", freq="M")
        m_mua = cong[t] - _DO_FXCE[ma][0]
        m_ban = -cong[t] - _DO_FXCE[ma][1]
        return cong - m_mua, -cong - m_ban
    return cong - 0.025, -cong - 0.025          # chi so: GIA DINH benchmark +- 2,5 %


_G: dict = {}


def _viec(v):
    ma, y, sp, co_swap, seed = v
    df, dv, sw = _G[(ma, y)]
    if seed is not None:
        df = g06.dao_dau(df, seed)
    ts = ThamSo(**KE_HOACH["tham_so"])
    t0 = time.time()
    kq = chay_duong(df, ts, KE_HOACH["von_usd"], "gan_open", sp, quy_doi=dv, swap_nam=sw if co_swap else None)
    nam = kq["ngay"] / 365.25
    kq = {k: (float(x) if isinstance(x, (np.floating, float)) else x) for k, x in kq.items()}
    kq["lai_nam_pct"] = kq["lai_tk"] / KE_HOACH["von_usd"] / nam * 100.0
    kq["giay"] = round(time.time() - t0, 1)
    return {"ma": ma, "nam": y, "spread_pip": sp, "swap": co_swap, "seed": seed, **kq}


def chuan_bi(td: Path) -> dict:
    y0, y1 = KE_HOACH["nam"]
    nam = range(y0 - 1, y1 + 1)
    gia = {m: doc_m1(td, m, nam) for m in KE_HOACH["tai_san"]}
    usdcad = doc_m1(td, "USDCAD", nam)["close"]
    gbpusd = doc_m1(td, "GBPUSD", nam)["close"]
    R = {m: bien_do_ngay(d) for m, d in gia.items()}
    meta = {"R": {m: {int(k): float(x) for k, x in r.items()} for m, r in R.items()}, "k": {}, "spread_pip": {},
            "so_nen": {}, "hop_le": {}}
    for m, d in gia.items():
        sn = d.groupby(d.index.year).size()
        meta["so_nen"][m] = {int(k): int(x) for k, x in sn.items()}
        tv = float(sn.loc[y0:y1].median())
        mua, ban = bang_swap(m)
        for y in range(y0, y1 + 1):
            ok = int(sn.get(y, 0)) >= 0.90 * tv
            meta["hop_le"].setdefault(m, {})[y] = ok
            k = 1.0 if m == "AUDCAD" else float(R["AUDCAD"][y - 1] / R[m][y - 1])
            meta["k"].setdefault(m, {})[y] = k
            spp = [s * k / PIP for s in KE_HOACH["tai_san"][m]["spread_gia"]]
            meta["spread_pip"].setdefault(m, {})[y] = spp
            if not ok:
                continue
            dy = d[d.index.year == y] * k
            if m == "AUDCAD":
                dv = usdcad.reindex(dy.index).ffill().bfill().to_numpy(float)
            elif m == "EURGBP":
                dv = 1.0 / gbpusd.reindex(dy.index).ffill().bfill().to_numpy(float)
            else:
                dv = np.ones(len(dy))
            _G[(m, y)] = (dy, dv, g06.swap_theo_nen(dy, mua, ban))
    return meta


def tong_hop(kq: list, meta: dict, n_nhieu: int) -> dict:
    ra = {}
    for m, cfg in KE_HOACH["tai_san"].items():
        nams = [y for y, ok in meta["hop_le"][m].items() if ok]
        that = [r for r in kq if r["ma"] == m and r["seed"] is None]
        theo_nam = {}
        for y in nams:
            sw = [r for r in that if r["nam"] == y and r["swap"]]
            xau = min(sw, key=lambda r: r["lai_tk"])
            ns = next(r for r in that if r["nam"] == y and not r["swap"])
            theo_nam[y] = {"lai_xau_usd": xau["lai_tk"], "lai_xau_pct_nam": xau["lai_nam_pct"],
                           "lai_khong_swap_pct": ns["lai_nam_pct"], "swap_usd": xau["swap_tk"],
                           "maxdd_pct": max(r["maxdd_pct"] for r in sw), "stopout": any(r["cham_stopout"] for r in sw),
                           "so_lenh": xau["so_lenh"], "tang_max": xau["tang_max"]}
        if len(nams) < 5:
            ra[m] = {"nhom": cfg["nhom"], "ket": "CHUA_DO_DUOC", "nam_hop_le": nams, "theo_nam": theo_nam}
            continue
        tong = sum(v["lai_xau_usd"] for v in theo_nam.values())
        dd = max(v["maxdd_pct"] for v in theo_nam.values())
        so = sum(v["stopout"] for v in theo_nam.values())
        lai = tong > 0 and dd < 80 and so == 0
        nh = [r for r in kq if r["ma"] == m and r["seed"] is not None and r["nam"] in nams]
        tong_nh = np.array([sum(r["lai_tk"] for r in nh if r["seed"] == s) for s in sorted({r["seed"] for r in nh})])
        p_hon = float((1 + np.sum(tong_nh >= tong)) / (len(tong_nh) + 1))
        p_kem = float((1 + np.sum(tong_nh <= tong)) / (len(tong_nh) + 1))
        nh_nam_lai = float(np.mean([r["lai_tk"] > 0 for r in nh]))
        ra[m] = {"nhom": cfg["nhom"], "nam_hop_le": nams, "LAI": bool(lai),
                 "HON_NHIEU": p_hon <= 0.05, "KEM_NHIEU": p_kem <= 0.05, "p_hon": p_hon, "p_kem": p_kem,
                 "tong_lai_usd": tong, "ti_le_nam_lai": float(np.mean([v["lai_xau_usd"] > 0 for v in theo_nam.values()])),
                 "trung_vi_pct_nam": float(np.median([v["lai_xau_pct_nam"] for v in theo_nam.values()])),
                 "trung_vi_khong_swap_pct_nam": float(np.median([v["lai_khong_swap_pct"] for v in theo_nam.values()])),
                 "maxdd_max_pct": dd, "nam_stopout": int(so),
                 "nhieu": {"n": int(len(tong_nh)), "tong_p5_p50_p95": [float(x) for x in np.percentile(tong_nh, [5, 50, 95])],
                           "ti_le_nam_lai": nh_nam_lai,
                           "trung_vi_pct_nam": float(np.median([r["lai_nam_pct"] for r in nh])),
                           "maxdd_max_pct": float(max(r["maxdd_pct"] for r in nh)),
                           "ti_le_nam_stopout": float(np.mean([r["cham_stopout"] for r in nh]))},
                 "theo_nam": theo_nam}
    hq = [v for v in ra.values() if v["nhom"] == "hoi_quy" and "LAI" in v]
    cs = [v for v in ra.values() if v["nhom"] == "chi_so" and "LAI" in v]
    if any(v.get("ket") == "CHUA_DO_DUOC" for v in ra.values() if v["nhom"] == "hoi_quy") or not cs:
        gb = "CHUA_DO_DUOC"
    elif all(v["LAI"] and v["HON_NHIEU"] for v in hq) and not any(v["LAI"] for v in cs):
        gb = "UNG_HO"
    elif not any(v["LAI"] for v in hq) or not any(v["HON_NHIEU"] for v in hq):
        gb = "BAC_BO"
    else:
        gb = "MOT_PHAN"
    return {"G_b": gb, "tai_san": ra}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--histdata", default="/workspace/du_lieu_fx/histdata")
    ap.add_argument("--so-nhieu", type=int, default=KE_HOACH["nhieu"]["so"])
    ap.add_argument("--nhan", type=int, default=7)
    a = ap.parse_args(argv)
    h = bam_ke_hoach()
    t0 = time.time()
    meta = chuan_bi(Path(a.histdata))
    viec = []
    for (m, y) in _G:
        sp = meta["spread_pip"][m][y]
        viec += [(m, y, sp[0], True, None), (m, y, sp[1], True, None), (m, y, sp[0], False, None)]
    for (m, y) in _G:
        sp = meta["spread_pip"][m][y]
        viec += [(m, y, sp[1], True, KE_HOACH["nhieu"]["seed_tu"] + s) for s in range(a.so_nhieu)]
    print(f"ke hoach {h} | {len(viec)} viec | chuan bi {time.time() - t0:.0f}s", flush=True)
    with Pool(a.nhan) as p:
        kq = []
        for i, r in enumerate(p.imap_unordered(_viec, viec, chunksize=1)):
            kq.append(r)
            if i % 50 == 0:
                print(f"{i}/{len(viec)} {time.time() - t0:.0f}s", flush=True)
    th = tong_hop(kq, meta, a.so_nhieu)
    out = {"ke_hoach_sha256_16": h, **th, "meta": meta, "giay": round(time.time() - t0, 1),
           "chay": sorted(kq, key=lambda r: (r["ma"], r["nam"], r["seed"] or 0, r["spread_pip"], r["swap"])),
           "nhan": "MO PHONG - khong phai tien that"}
    RA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n")
    print("G-b:", th["G_b"])
    for m, v in th["tai_san"].items():
        print(m, {k: v.get(k) for k in ("nhom", "LAI", "HON_NHIEU", "KEM_NHIEU", "p_hon", "p_kem", "ti_le_nam_lai",
                                       "trung_vi_pct_nam", "trung_vi_khong_swap_pct_nam", "maxdd_max_pct", "nam_stopout",
                                       "tong_lai_usd", "ket")})
        if "nhieu" in v:
            print("   nhieu", v["nhieu"])
        for y, r in v["theo_nam"].items():
            print(f"   {y} xau {r['lai_xau_pct_nam']:+.2f} %/nam (khong swap {r['lai_khong_swap_pct']:+.2f}) "
                  f"DD {r['maxdd_pct']:.1f} so {r['stopout']} lenh {r['so_lenh']} tang {r['tang_max']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
