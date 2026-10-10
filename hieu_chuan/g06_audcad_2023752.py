#!/usr/bin/env python3
"""G06 (goi ban giao the-brain, file 06 / so tay gia thuyet 4) - 11/10/2026.

Cau hoi: cai dat luoi AUDCAD BOC TU LICH SU LENH cua tin hieu cong khai 2023752 (song ~3,1 nam, the-brain
`03` R6: buoc 21,2 pip, he so buoc 1,20, lot cong 0,25, TP 7,6 pip, tia lenh, toi da 5 tang, hai chieu)
co LAI SAU PHI (spread + swap theo thang) va maxDD < 80 % tren AUDCAD M1 2018-01 -> 2023-07, tuc TRUOC
khi tin hieu bat dau? Va lai do co HON chuoi nhieu cung bien do (dao dau tung nen M1 = pha hoi quy) khong?
  - co lai + hon nhieu  -> co che (hoi quy AUDCAD) - ung vien dang lam lai ("cua ta");
  - co lai, khong hon nhieu -> dac tinh luoi (P4) - tin hieu co the chi gap may / chon tai san dung luc;
  - lo -> cai dat nay khong song truoc 2023 tren gia cua brain2.

    python hieu_chuan/g06_audcad_2023752.py [--histdata DIR] [--so-nhieu 40] [--nhan 6]

Ke hoach DONG BANG truoc khi chay: `hieu_chuan/G06_KE_HOACH.json` (sha256 in trong ket qua); doi ke hoach
ma khong doi file -> dung. Gia: HistData.com M1 BID cong khai (EST co dinh -> gio Helsinki = gio may chu
kieu XM), USDCAD M1 doi CAD -> USD tung phut. Swap: (r_AUD - r_CAD) thang (FRED IRSTCI01AUM156N /
IRSTCI01CAM156N) + markup XM do 13/09/2026 (gia dinh khong doi). Spread: chua co lich su -> 1,5 va 2,8 pip
(2,8 = spread bar XM do duoc, chan tren). Mo phong `nhan/luoi_duong` (P1: dong dau MT5 117/120).
TAT CA LA MO PHONG. Lot that cua tin hieu khong biet -> chi so DAU va hinh dang, khong so do lon.
Ra: hieu_chuan/g06_ket_qua.json. Gia khong vao git.
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
from nhan.luoi import ThamSo  # noqa: E402
from nhan.luoi_duong import THU_TU, chay_duong  # noqa: E402

KE_HOACH_FILE = GOC / "hieu_chuan" / "G06_KE_HOACH.json"
LAI_SUAT = GOC / "config" / "lai_suat_aud_cad_thang.csv"
RA = GOC / "hieu_chuan" / "g06_ket_qua.json"
CACHE = Path("/workspace/du_lieu_fx")

KE_HOACH = {
    "gia_thuyet": "so tay the-brain gt_204263a93f1f43a4 (id 4) / 06 G-c: cai dat 2023752 co lai TRUOC khi tin hieu song",
    "tham_so": {"buoc": 21.2, "he_so_buoc": 1.2, "tp": 7.6, "tran_tang": 5, "che_do": "hai_chieu",
                "lot": 0.01, "kieu_lot": "cong", "he_so_lot": 0.25, "tia_lenh": True,
                "bien_cap": 4.0, "cap_moi_bar": 999, "don_bay": 100.0, "muc_stopout": 0.5},
    "gia_dinh_khong_tu_tin_hieu": ["bien_cap 4 pip (mac dinh the-brain)", "cap_moi_bar 999",
                                   "lot goc 0,01 + lam tron 0,01", "don_bay 100, stop-out 50 %"],
    "von_usd": 10000.0,
    "kham_pha": ["2018-01-02", "2023-07-02"],
    "xac_nhan_khong_doc_lap": ["2023-07-03", "2025-02-17"],
    "khung": "M1 HistData",
    "spread_pip": [1.5, 2.8],
    "thu_tu": list(THU_TU),
    "swap": "(r_AUD - r_CAD)(thang) - markup XM 13/09/2026, theo tung lot mo qua rollover",
    "nhieu": {"kieu": "dao dau tung nen M1 (giu bien do, pha tu tuong quan)", "so": 40, "seed_tu": 6000,
              "bien_the": "spread 2.8, gan_open, swap lich su"},
    "luat": {
        "DAT_mo_phong": "kham_pha: lai rong > 0 o MOI bien the (4 thu tu x 2 spread) VA maxDD < 80 % VA khong stop-out "
                        "VA lai bien the quyet dinh > nhieu voi p <= 0,05",
        "LAI_NHUNG_KHONG_HON_NHIEU": "dieu kien luat chu (lai + DD) dat nhung p > 0,05",
        "AM": "lai rong <= 0 o bien the xau nhat hoac maxDD >= 80 % hoac stop-out",
        "CHUA_DO_DUOC": "thieu > 5 % phut giao dich trong mot nam cua kham_pha, hoac dau lai doi giua cac bien the "
                        "(co bien the > 0 va co bien the <= 0) -> bao khoang",
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


def doc_m1(thu_muc: Path, ma: str, nam: range) -> pd.DataFrame:
    kho = CACHE / f"g06_{ma.lower()}_m1.pkl"
    if kho.exists():
        return pd.read_pickle(kho)
    phan = []
    for y in nam:
        with zipfile.ZipFile(thu_muc / f"DAT_ASCII_{ma}_M1_{y}.zip") as z:
            ten = [t for t in z.namelist() if t.endswith(".csv")][0]
            d = pd.read_csv(io.BytesIO(z.read(ten)), sep=";", header=None,
                            names=["t", "open", "high", "low", "close", "v"])
        t = pd.to_datetime(d["t"], format="%Y%m%d %H%M%S") + pd.Timedelta(hours=5)
        d.index = t.dt.tz_localize("UTC").dt.tz_convert("Europe/Helsinki").dt.tz_localize(None)
        phan.append(d[["open", "high", "low", "close"]])
    df = pd.concat(phan).sort_index()
    df = df[~df.index.duplicated()]
    df.index.name = "time"
    df.to_pickle(kho)
    return df


def kiem_thieu(df: pd.DataFrame) -> dict:
    """Ti le phut co nen / phut giao dich mong doi (CN 00:00 -> T6 23:59 gio Helsinki ~ 120 h x 60)."""
    ra = {}
    for y, g in df.groupby(df.index.year):
        tuan = g.index.to_period("W").nunique()
        ra[int(y)] = round(len(g) / (tuan * 120 * 60), 4)
    return ra


def bang_swap() -> tuple[pd.Series, pd.Series, dict]:
    ls = pd.read_csv(LAI_SUAT, index_col=0)
    d = (ls["AUD"] - ls["CAD"]) / 100.0
    d.index = pd.PeriodIndex(d.index, freq="M")
    # XM AUDCADmicro 13/09/2026 (config/chi_phi_do.json): thu nhap/nam mua +0,602 %, ban -3,714 %
    d_nay = float(d.iloc[-1])
    m_mua = d_nay - 0.00602
    m_ban = -d_nay + 0.03714
    mua, ban = d - m_mua, -d - m_ban
    return mua, ban, {"d_cuoi": d_nay, "thang_cuoi": str(d.index[-1]), "markup_mua": m_mua, "markup_ban": m_ban}


def swap_theo_nen(df, mua, ban) -> np.ndarray:
    p = df.index.to_period("M")
    a = mua.reindex(p).ffill().to_numpy(float)
    b = ban.reindex(p).ffill().to_numpy(float)
    return np.column_stack([a, b])


def dao_dau(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Nhieu cung bien do: moi nen M1 giu |log(open/close_truoc)|, |log(h/o)|, |log(l/o)|, |log(c/o)| nhung
    dau ngau nhien (lat ca nen: cao <-> thap) -> pha moi tu tuong quan/hoi quy, giu phan phoi bien do."""
    r = np.random.default_rng(seed)
    o, h, l, c = (np.log(df[k].to_numpy(float)) for k in ("open", "high", "low", "close"))
    gap = np.concatenate([[0.0], o[1:] - c[:-1]])
    s = r.choice([-1.0, 1.0], size=len(o))
    ho, lo_, co = h - o, l - o, c - o
    nh = np.where(s > 0, ho, -lo_)
    nl = np.where(s > 0, lo_, -ho)
    nc = s * co
    goc = o[0]
    ccl = goc + np.cumsum(s * gap + nc)       # log close: close_i = close_{i-1} + s*gap_i + nc_i
    no = ccl - nc                             # log open
    out = pd.DataFrame({"open": np.exp(no), "high": np.exp(no + nh), "low": np.exp(no + nl),
                        "close": np.exp(ccl)}, index=df.index)
    return out


_G = {}


def _viec(v):
    kieu, cua_so, thu_tu, sp, co_swap, seed = v
    df, dv, sw = _G[cua_so]
    if kieu == "nhieu":
        df = dao_dau(df, seed)
    ts = ThamSo(**KE_HOACH["tham_so"])
    t0 = time.time()
    kq = chay_duong(df, ts, KE_HOACH["von_usd"], thu_tu, sp, quy_doi=dv, swap_nam=sw if co_swap else None)
    nam = kq["ngay"] / 365.25
    kq = {k: (float(x) if isinstance(x, (np.floating, float)) else x) for k, x in kq.items()}
    kq["lai_nam_pct"] = kq["lai_tk"] / KE_HOACH["von_usd"] / nam * 100.0
    kq["giay"] = round(time.time() - t0, 1)
    return {"kieu": kieu, "cua_so": cua_so, "thu_tu": thu_tu, "spread": sp, "swap": co_swap, "seed": seed, **kq}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--histdata", default="/workspace/du_lieu_fx/histdata")
    ap.add_argument("--so-nhieu", type=int, default=KE_HOACH["nhieu"]["so"])
    ap.add_argument("--nhan", type=int, default=6)
    a = ap.parse_args(argv)
    h = bam_ke_hoach()
    td = Path(a.histdata)
    aud = doc_m1(td, "AUDCAD", range(2018, 2026))
    usd = doc_m1(td, "USDCAD", range(2018, 2026))["close"]
    mua, ban, sw_meta = bang_swap()
    for ten, (tu, den) in (("kp", KE_HOACH["kham_pha"]), ("xn", KE_HOACH["xac_nhan_khong_doc_lap"])):
        d = aud[(aud.index >= tu) & (aud.index < pd.Timestamp(den) + pd.Timedelta(days=1))]
        dv = usd.reindex(d.index).ffill().bfill().to_numpy(float)
        _G[ten] = (d, dv, swap_theo_nen(d, mua, ban))
    for y in range(2018, 2024):
        d = _G["kp"][0]
        d = d[d.index.year == y]
        _G[f"y{y}"] = (d, usd.reindex(d.index).ffill().bfill().to_numpy(float), swap_theo_nen(d, mua, ban))
    thieu = kiem_thieu(_G["kp"][0])
    viec = []
    for cs in ("kp", "xn"):
        viec += [("that", cs, t, s, True, None) for t in THU_TU for s in KE_HOACH["spread_pip"]]
        viec.append(("that", cs, "gan_open", 1.5, False, None))
    viec += [("that", f"y{y}", "gan_open", 2.8, True, None) for y in range(2018, 2024)]
    viec += [("nhieu", "kp", "gan_open", 2.8, True, KE_HOACH["nhieu"]["seed_tu"] + k) for k in range(a.so_nhieu)]
    t0 = time.time()
    with Pool(a.nhan) as p:
        kq = p.map(_viec, viec, chunksize=1)
    that = [r for r in kq if r["kieu"] == "that"]
    kp = [r for r in that if r["cua_so"] == "kp" and r["swap"]]
    quyet = next(r for r in kp if r["thu_tu"] == "gan_open" and r["spread"] == 2.8)
    nh = np.array([r["lai_tk"] for r in kq if r["kieu"] == "nhieu"])
    p_nhieu = float((1 + np.sum(nh >= quyet["lai_tk"])) / (len(nh) + 1)) if len(nh) else None
    lai = [r["lai_tk"] for r in kp]
    dd = max(r["maxdd_pct"] for r in kp)
    so = any(r["cham_stopout"] for r in kp)
    if min(thieu.values()) < 0.95:
        ket = "CHUA_DO_DUOC (thieu du lieu)"
    elif min(lai) > 0 and max(lai) > 0 and dd < 80 and not so:
        ket = "DAT_mo_phong" if p_nhieu is not None and p_nhieu <= 0.05 else "LAI_NHUNG_KHONG_HON_NHIEU"
    elif max(lai) <= 0 or dd >= 80 or so:
        ket = "AM"
    else:
        ket = "CHUA_DO_DUOC (dau doi giua bien the)"
    out = {"ke_hoach_sha256_16": h, "ket_luan_kham_pha": ket, "p_nhieu": p_nhieu,
           "lai_kp_min_max_usd": [min(lai), max(lai)], "maxdd_kp_max_pct": dd, "stopout_kp": so,
           "ti_le_phut_co_nen_theo_nam": thieu, "swap_meta": sw_meta,
           "nhieu_lai_usd": {"n": int(len(nh)), "tb": float(nh.mean()) if len(nh) else None,
                             "p5_p50_p95": [float(x) for x in np.percentile(nh, [5, 50, 95])] if len(nh) else None,
                             "ti_le_lai_duong": float(np.mean(nh > 0)) if len(nh) else None,
                             "ti_le_dat_luat_chu": float(np.mean([(r["lai_tk"] > 0 and r["maxdd_pct"] < 80
                                                                   and not r["cham_stopout"])
                                                                  for r in kq if r["kieu"] == "nhieu"])) if len(nh) else None},
           "giay": round(time.time() - t0, 1), "chay": kq,
           "nhan": "MO PHONG - khong phai tien that; lot that cua tin hieu khong biet"}
    RA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"ke hoach {h} | ket luan kham pha: {ket} | p nhieu {p_nhieu}")
    print(f"phut co nen/nam: {thieu}")
    for r in that:
        print(f"{r['cua_so']:>5} {r['thu_tu']:>10} sp{r['spread']} swap={r['swap']!s:5} lai {r['lai_tk']:9.1f} USD "
              f"({r['lai_nam_pct']:+.2f} %/nam) DD {r['maxdd_pct']:5.1f} % lenh {r['so_lenh']} swap {r['swap_tk']:8.1f} "
              f"tang_max {r['tang_max']} so {r['cham_stopout']}")
    print("nhieu:", out["nhieu_lai_usd"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
