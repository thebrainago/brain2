#!/usr/bin/env python3
"""P4 (goi ban giao the-brain): DOI CHUNG NHIEU cap duong ong - chuoi gia CHI CO NHIEU lot cong bao nhieu?

    python hieu_chuan/p4_nhieu.py                       # A + B, 100 seed, 5 tien trinh
    python hieu_chuan/p4_nhieu.py --phan A --seeds 20   # chi duong ong vong_thu_nghiem
    python hieu_chuan/p4_nhieu.py --phan R              # luat R2 (P1) tren o tot nhat cua B (can B)

Chi DO, khong doi cong. Moi so la MO PHONG tren gia GIA LAP (khong co loi the nao cai san), nen
MOI lan "dat" o day la DUONG TINH GIA. Ra: hieu_chuan/p4_ket_qua.json (+ in bang).

Phan A - DUNG duong ong robot that: `vong_thu_nghiem.chay_mot_file` (boc co che tu .mq5 -> toi uu
  70 % dau -> kiem 30 % sau -> cong t/lenh + cong ro/luoi: tai khoan, placebo cung cau truc 99 lan,
  chay/nam) tren moi EA cua `mau_thu/*.mq5` (bo mac dinh cua vong) va `mau_thu/mo_rong/**.mq5`,
  phi EURUSD that (`mo_hinh_chi_phi`), tai khoan mac dinh. Gia: `du_lieu_gia_lap_duong` (buoc
  ngau nhien dung duong gia, ~5,5 %/nam - chinh placebo cua vong) va bien the GARCH(1,1) ~9 %/nam
  (kieu the-brain). Seed tu 1000 (khong trung seed 1-5/42 da dung khi chinh vong).
  Ghi tung co che: GIU (cong brain2), nhan 25/09 (lai sau phi phan kiem, maxDD < 80 %, khong chay),
  placebo p <= 0,05 rieng, nguong t/lenh rieng.
Phan B - quet luoi ThamSo kieu the-brain (o tot nhat cua luot quet -> ngoai mau): luoi hai chieu
  72 o (buoc 20/40/80 x tp 10/20/40 x tia x lot 0,01/0,03 x lot phang/nhan 1,5; 8 tang), chon o lai/nam cao nhat (khong chay, DD < 80 %) tren 60 % dau, kiem 40 % sau theo 25/09
  (lai > 0, DD < 80 %, khong cham stop-out). Hai dong co: `luoi_duong.chay_duong` (P1: bam MT5) va
  `luoi.chay` v3 (P1: lac quan) - tat swap, spread 2 pip, von 10.000 USD. Kem 1 o chon bua.
  ThamSo khong co tin hieu vao -> khong co placebo chieu; cong brain2 khong ap duoc truc tiep
  (nhanh robot dung `mo_phong.chay_he`, do o phan A).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
import vong_thu_nghiem as V  # noqa: E402
from nhan import luoi as L  # noqa: E402
from nhan.luoi_duong import chay_duong  # noqa: E402

VON = 10_000.0


def gia_lap_garch_duong(n: int, seed: int, buoc: int = 60, vol_nam: float = 0.09,
                        a: float = 0.05, b: float = 0.94) -> pd.DataFrame:
    """Nhu `V.du_lieu_gia_lap_duong` (bar dung tu `buoc` buoc con, high/low = cuc tri that)
    nhung do lech chuan TUNG GIO theo GARCH(1,1) (cum bien dong), trung binh ~`vol_nam`/nam.
    Van la martingale: KHONG co loi the nao."""
    rng = np.random.default_rng(seed)
    var0 = (vol_nam / math.sqrt(V.BAR_NAM["H1"])) ** 2
    w = var0 * (1 - a - b)
    sd = np.empty(n)
    v, e = var0, 0.0
    for i in range(n):
        v = w + a * e * e + b * v
        sd[i] = math.sqrt(v)
        e = rng.normal(0, sd[i])
    con = rng.normal(0, 1, (n, buoc)) * (sd[:, None] / math.sqrt(buoc))
    duong = np.r_[1.10, 1.10 * np.exp(np.cumsum(con.ravel()))]
    khoi = np.lib.stride_tricks.sliding_window_view(duong, buoc + 1)[::buoc][:n]
    idx = pd.date_range("2021-01-04", periods=n, freq="h")
    return pd.DataFrame({"open": khoi[:, 0], "high": khoi.max(axis=1), "low": khoi.min(axis=1),
                         "close": khoi[:, -1], "tick_volume": rng.integers(200, 2000, n)},
                        index=idx)


def tao_gia(mo_hinh: str, n: int, seed: int) -> pd.DataFrame:
    if mo_hinh == "rw":
        return V.du_lieu_gia_lap_duong(n, seed, "H1")
    if mo_hinh == "garch":
        return gia_lap_garch_duong(n, seed)
    raise ValueError(mo_hinh)


# ---------------------------------------------------------------- phan A
def file_ea() -> list[Path]:
    goc = sorted((GOC / "mau_thu").glob("*.mq5"))
    rong = sorted((GOC / "mau_thu" / "mo_rong").rglob("*.mq5"))
    return [(p, "mau_thu") for p in goc] + [(p, "mo_rong") for p in rong]


def _loai(d: dict) -> str:
    if d.get("loai_ro") == "luoi":
        return "luoi"
    if d.get("loai_ro") == "hedge":
        return "hedge"
    return "le"


def chay_A(viec) -> list[dict]:
    mo_hinh, n, seed, n_placebo = viec
    df = tao_gia(mo_hinh, n, seed)
    cp = V.mo_hinh_chi_phi(df)
    da_thay: set = set()
    ra = []
    for p, bo in file_ea():
        try:
            dongs = V.chay_mot_file(p, df, "H1", True, 20, 2.0, 1.5, da_thay, cp=cp,
                                    tai_khoan=dict(V.TAI_KHOAN_MAC_DINH), n_placebo=n_placebo,
                                    p_placebo=0.05, p_chay_nam=0.05)
        except Exception as e:  # noqa: BLE001 - boc that bai: ghi, khong dem
            ra.append({"seed": seed, "file": p.name, "bo": bo, "loi_file": f"{type(e).__name__}: {e}"})
            continue
        for d in dongs:
            r = {"seed": seed, "file": p.name, "bo": bo, "ten": str(d.get("ten"))[:60]}
            if d.get("trung") or d.get("khong_hop_khung") or "loi" in d:
                r["bo_qua"] = "trung" if d.get("trung") else (
                    "khong_hop_khung" if d.get("khong_hop_khung") else d.get("loi", "")[:80])
                ra.append(r)
                continue
            cl = d.get("cong_luoi") or {}
            dat_t = bool(d["t_tu"] >= 2.0 and d["t_kiem"] >= 1.5 and not d.get("it_lenh")
                         and not d.get("kiem_cu_phap"))
            n25 = d["tieu_chi_25_09"]
            r.update(loai=_loai(d), giu=bool(d["giu_lai"]), n25=bool(n25["dat"]),
                     n25_ly_do=n25["ly_do"], maxdd=n25["maxdd_pct"], dat_t=dat_t,
                     t_tu=d["t_tu"], t_kiem=d["t_kiem"], it_lenh=bool(d.get("it_lenh")),
                     so_lenh_kiem=d["tot_kiem"]["so_lenh"], loi_log_kiem=d["tot_kiem"]["loi_log"],
                     p_placebo=cl.get("p"), placebo_bo_qua=cl.get("placebo_bo_qua"),
                     cong_ro_dat=cl.get("dat"), cong_ro_ly_do=cl.get("ly_do"))
            ra.append(r)
    return ra


# ---------------------------------------------------------------- phan B
def luoi_o() -> list[L.ThamSo]:
    o = []
    for buoc in (20.0, 40.0, 80.0):
        for tp in (10.0, 20.0, 40.0):
            for tia in (False, True):
                for lot in (0.01, 0.03):
                    for kl, hs in (("phang", 1.0), ("nhan", 1.5)):
                        o.append(L.ThamSo(buoc=buoc, tp=tp, tran_tang=8, che_do="hai_chieu",
                                          lot=lot, kieu_lot=kl, he_so_lot=hs, tia_lenh=tia,
                                          bien_cap=4.0, cap_moi_bar=1))
    return o


def _v3(df, ts, spread_pip=2.0) -> dict:
    """`luoi.chay` (v3) nguyen trang, TAT swap - cung cach do voi `hieu_chuan/p1_chay.chay_v3`."""
    hi, lo, cl = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    sp = np.full(len(df), spread_pip * L.PIP)
    dem = np.zeros(len(df))
    lai = np.zeros(len(df))
    treo = np.zeros(len(df))
    cuoi = 0.0
    for c in (1, -1):
        a, b, k = L._mot_ro(hi, lo, cl, sp, dem, c, ts)
        lai += a
        treo += b
        cuoi += sum(c * (cl[-1] - g) * l for g, l in k["vao_cuoi"]) * L.HOP_DONG
    eq = VON + lai - treo
    dinh = np.maximum.accumulate(np.maximum(eq, VON))
    dd = float(np.max((dinh - eq) / dinh)) * 100.0
    # stop-out xap xi nhu `luoi.chay`: ky quy theo tang_max (than trong)
    return {"lai": float(lai[-1] + cuoi), "maxdd_pct": dd, "chay": bool(eq.min() <= 0)}


def _duong(df, ts) -> dict:
    r = chay_duong(df, ts, VON, "gan_open", 2.0)
    return {"lai": float(r["lai_tk"]), "maxdd_pct": float(r["maxdd_pct"]),
            "chay": bool(r["cham_stopout"])}


def _dat(r) -> bool:
    return r["lai"] > 0 and r["maxdd_pct"] < V.DD_25_09 and not r["chay"]


def chay_B(viec) -> dict:
    mo_hinh, n, seed = viec
    df = tao_gia(mo_hinh, n, seed)
    cat = int(n * 0.6)
    tu, kiem = df.iloc[:cat], df.iloc[cat:]
    o = luoi_o()
    rng = np.random.default_rng(seed + 7)
    j_bua = int(rng.integers(0, len(o)))
    ra = {"seed": seed}
    for ten, ham in (("duong", _duong), ("v3", _v3)):
        kq = [ham(tu, ts) for ts in o]
        diem = [r["lai"] if (r["maxdd_pct"] < V.DD_25_09 and not r["chay"]) else -1e18 for r in kq]
        j = int(np.argmax(diem))
        k_tot, k_bua = ham(kiem, o[j]), ham(kiem, o[j_bua])
        ra[ten] = {"o_tot": j, "tu_dat_ti_le": float(np.mean([_dat(r) for r in kq])),
                   "tot_tu": kq[j], "tot_kiem": k_tot, "tot_kiem_dat": _dat(k_tot),
                   "bua_kiem": k_bua, "bua_kiem_dat": _dat(k_bua)}
    return ra


# ---------------------------------------------------------------- phan R (luat R2 tren nhieu)
SPREAD_R2 = (1.5, 2.5)


def chay_R2(viec) -> dict:
    """Luat R2 cua P1 (luoi_duong lai > 0 o bien the XAU NHAT: 4 thu tu gia x spread 1,5/2,5)
    ap len o tot nhat (dong co duong) da chon o phan B, tren 40 % ngoai mau cua cung chuoi nhieu.
    Hoi: R2 chan duoc bao nhieu 'dat 25/09' gia?"""
    from nhan.luoi_duong import THU_TU
    mo_hinh, n, seed, j = viec
    df = tao_gia(mo_hinh, n, seed)
    kiem = df.iloc[int(n * 0.6):]
    ts = luoi_o()[j]
    bt = {}
    for t in THU_TU:
        for s in SPREAD_R2:
            r = chay_duong(kiem, ts, VON, t, s)
            bt[f"{t}|{s}"] = {"lai": float(r["lai_tk"]), "maxdd_pct": float(r["maxdd_pct"]),
                              "chay": bool(r["cham_stopout"])}
    return {"seed": seed, "o": j, "bien_the": bt,
            "xau_nhat_lai": min(v["lai"] for v in bt.values()),
            "moi_bien_the_dat_25_09": all(_dat(v) for v in bt.values())}


def tong_R2(rows: list[dict], b_rows: list[dict]) -> dict:
    goc = {r["seed"]: r["duong"]["tot_kiem_dat"] for r in b_rows}
    dat_goc = [r for r in rows if goc[r["seed"]]]
    return {
        "n_chuoi": len(rows),
        "goc_gan_open_2pip_dat_25_09": ti(len(dat_goc), len(rows)),
        "R2_xau_nhat_lai_gt_0": ti(sum(r["xau_nhat_lai"] > 0 for r in rows), len(rows)),
        "R2_va_moi_bien_the_dat_25_09": ti(sum(r["moi_bien_the_dat_25_09"] for r in rows), len(rows)),
        "trong_so_dat_goc_R2_con_lot": ti(sum(r["moi_bien_the_dat_25_09"] for r in dat_goc), len(dat_goc)),
    }


# ---------------------------------------------------------------- tong hop
def wilson(k: int, n: int) -> list:
    if n == 0:
        return [None, None]
    z, p = 1.96, k / n
    m = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(max(0, m - h), 4), round(min(1, m + h), 4)]


def ti(k, n):
    return {"k": int(k), "n": int(n), "ti_le": round(k / n, 4) if n else None, "ci95": wilson(k, n)}


def tong_A(rows: list[dict]) -> dict:
    chay = [r for r in rows if "loai" in r]
    out = {"so_dong": len(rows), "so_co_che_chay": len(chay),
           "bo_qua": int(sum(1 for r in rows if "bo_qua" in r)),
           "loi_file": int(sum(1 for r in rows if "loi_file" in r))}

    def _bang(ds):
        pl = [r for r in ds if r["p_placebo"] is not None]
        return {
            "giu_cong_brain2": ti(sum(r["giu"] for r in ds), len(ds)),
            "nhan_25_09": ti(sum(r["n25"] for r in ds), len(ds)),
            "lai_kiem_sau_phi": ti(sum(r["loi_log_kiem"] > 0 for r in ds), len(ds)),
            "nguong_t_lenh_rieng": ti(sum(r["dat_t"] for r in ds), len(ds)),
            "placebo_p05_rieng": ti(sum(r["p_placebo"] <= 0.05 for r in pl), len(pl)),
            "n25_va_placebo_p05": ti(sum(r["n25"] and r["p_placebo"] <= 0.05 for r in pl), len(pl)),
            "n25_va_nguong_t": ti(sum(r["n25"] and r["dat_t"] for r in ds), len(ds)),
            "it_lenh": ti(sum(r["it_lenh"] for r in ds), len(ds)),
        }
    out["tat_ca"] = _bang(chay)
    for loai in ("luoi", "hedge", "le"):
        ds = [r for r in chay if r["loai"] == loai]
        if ds:
            out[f"loai_{loai}"] = _bang(ds)
    for bo in ("mau_thu", "mo_rong"):
        ds = [r for r in chay if r["bo"] == bo]
        if ds:
            out[f"bo_{bo}"] = _bang(ds)
    # cap chuoi: it nhat MOT co che "dat" tren ca lan chay vong (mot chuoi gia)
    seeds = sorted({r["seed"] for r in rows})
    theo = {s: [r for r in chay if r["seed"] == s] for s in seeds}
    out["cap_chuoi"] = {
        "co_it_nhat_1_giu": ti(sum(any(r["giu"] for r in d) for d in theo.values()), len(seeds)),
        "co_it_nhat_1_nhan_25_09": ti(sum(any(r["n25"] for r in d) for d in theo.values()), len(seeds)),
        "so_co_che_moi_chuoi_tb": round(float(np.mean([len(d) for d in theo.values()])), 2) if seeds else None,
    }
    # tung co che (ten file) - ti le nhan 25/09 / giu
    tung: dict = {}
    for r in chay:
        k = f"{r['file']}|{r['ten'][:40]}"
        t = tung.setdefault(k, {"loai": r["loai"], "n": 0, "giu": 0, "n25": 0, "p05": 0, "co_p": 0})
        t["n"] += 1
        t["giu"] += r["giu"]
        t["n25"] += r["n25"]
        if r["p_placebo"] is not None:
            t["co_p"] += 1
            t["p05"] += r["p_placebo"] <= 0.05
    out["tung_co_che"] = tung
    return out


def tong_B(rows: list[dict]) -> dict:
    out = {"n_chuoi": len(rows)}
    for e in ("duong", "v3"):
        ds = [r[e] for r in rows]
        out[e] = {
            "o_tot_nhat_qua_ngoai_mau_25_09": ti(sum(d["tot_kiem_dat"] for d in ds), len(ds)),
            "o_chon_bua_qua_ngoai_mau_25_09": ti(sum(d["bua_kiem_dat"] for d in ds), len(ds)),
            "ti_le_o_dat_trong_mau_tb": round(float(np.mean([d["tu_dat_ti_le"] for d in ds])), 4),
            "lai_kiem_o_tot_trung_vi_usd": round(float(np.median([d["tot_kiem"]["lai"] for d in ds])), 2),
            "dd_kiem_o_tot_trung_vi_pct": round(float(np.median([d["tot_kiem"]["maxdd_pct"] for d in ds])), 2),
        }
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phan", default="AB")
    ap.add_argument("--seeds", type=int, default=100)
    ap.add_argument("--seeds-garch", type=int, default=50)
    ap.add_argument("--tu-seed", type=int, default=1000)
    ap.add_argument("--tien-trinh", type=int, default=5)
    ap.add_argument("--n-A", type=int, default=24 * 400, help="so bar phan A (= mac dinh vong)")
    ap.add_argument("--n-B", type=int, default=24 * 260 * 4, help="so bar phan B (~4 nam giao dich)")
    ap.add_argument("--n-placebo", type=int, default=99)
    ap.add_argument("--ra", default=str(GOC / "hieu_chuan" / "p4_ket_qua.json"))
    a = ap.parse_args(argv)
    seeds = list(range(a.tu_seed, a.tu_seed + a.seeds))
    seeds_g = list(range(a.tu_seed, a.tu_seed + a.seeds_garch))
    f_ra = Path(a.ra)
    # gop vao ket qua cu (chay tung phan khong xoa phan da do)
    ket = json.loads(f_ra.read_text(encoding="utf-8")) if f_ra.exists() else {}
    ket["nhan"] = "MO PHONG tren gia GIA LAP chi co nhieu - moi 'dat' la duong tinh gia; khong phai tien"
    ket.setdefault("cau_hinh_theo_phan", {})
    for ph in a.phan:
        ket["cau_hinh_theo_phan"][ph] = vars(a)
    ket.setdefault("cau_hinh", vars(a))
    t0 = time.time()
    with Pool(a.tien_trinh) as pool:
        if "A" in a.phan:
            for mh, ss in (("rw", seeds), ("garch", seeds_g)):
                rows = [r for ds in pool.imap_unordered(chay_A, [(mh, a.n_A, s, a.n_placebo) for s in ss])
                        for r in ds]
                ket[f"A_{mh}"] = tong_A(rows)
                ket[f"A_{mh}_dong"] = rows
                print(f"A {mh}: {len(ss)} chuoi xong {time.time() - t0:.0f}s", flush=True)
        if "B" in a.phan:
            for mh, ss in (("rw", seeds), ("garch", seeds_g)):
                rows = list(pool.imap_unordered(chay_B, [(mh, a.n_B, s) for s in ss]))
                ket[f"B_{mh}"] = tong_B(rows)
                ket[f"B_{mh}_dong"] = rows
                print(f"B {mh}: {len(ss)} chuoi xong {time.time() - t0:.0f}s", flush=True)
        if "R" in a.phan:
            for mh in ("rw", "garch"):
                b_rows = ket.get(f"B_{mh}_dong")
                if not b_rows:
                    print(f"R {mh}: CHUA DO DUOC (thieu B_{mh}_dong - chay --phan B truoc)", flush=True)
                    continue
                nb = int(ket["cau_hinh_theo_phan"].get("B", ket["cau_hinh"])["n_B"])
                viec = [(mh, nb, r["seed"], r["duong"]["o_tot"]) for r in b_rows]
                rows = list(pool.imap_unordered(chay_R2, viec))
                ket[f"R2_{mh}"] = tong_R2(rows, b_rows)
                ket[f"R2_{mh}_dong"] = rows
                print(f"R {mh}: {len(rows)} chuoi xong {time.time() - t0:.0f}s", flush=True)
    ket[f"giay_{a.phan}"] = round(time.time() - t0, 1)
    tam = f_ra.with_suffix(".tmp")
    tam.write_text(json.dumps(ket, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    tam.replace(f_ra)   # ghi nguyen tu: khong de file do dang
    for k, v in ket.items():
        if k.startswith(("A_", "B_", "R2_")) and not k.endswith("_dong"):
            v = {x: y for x, y in v.items() if x != "tung_co_che"}
            print(k, json.dumps(v, ensure_ascii=False, indent=1))
    print(f"Da ghi {a.ra} ({ket[f'giay_{a.phan}']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
