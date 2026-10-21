# -*- coding: utf-8 -*-
"""vong2.py - VONG 2 cho cac he DAT MT5 vong 1 (20/10/2026, Grok Bot). Thiet ke: tai_lieu/VONG_2.md.

Khong goi LLM / ai-box. Chi dung: the da dich (data/ong_dan/trang_thai.sqlite), lenh MT5 that
(reports/ong_dan/ket_qua_mt5/*_lenh_mt5.csv + *_gia.csv), gia H1 tren box (config/ong_dan.json).

Phan:
  A. phan_tich_mt5  : tai dung DUONG VON (equity, tinh lenh dang mo theo gia H1 cua chinh lan chay MT5) tu lenh MT5,
                      walk-forward 3 doan, Monte Carlo xao thu tu lenh, stress phi (spread x1.5, hoa hong 7 USD/100k).
  B. python_v2      : luoi tham so tho (khung, cap, quan li, input chi bao) + chong qua khop (cao nguyen tham so, OOS 30%).
  C. ghep_cung_cap  : A + B (khac phong cach, cung cap): xac_nhan / them_lenh / nguoc (hedge).
  D. danh_muc_v2    : danh muc tu lenh MT5 that, DD tren equity tai dung (sua caveat "chi lenh dong").
  E. hang_cho       : viec MT5 vong 2 -> reports/vong2/hang_cho_vong2.jsonl (may nha chi doc khi BRAIN_VONG2=1).

Chay:  python -m nhan.vong2 [--top 12] [--ngan-sach 90] [--khong-python]
So MT5 = ĐO THẬT; moi so Python / Monte Carlo / stress = MÔ PHỎNG.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import sqlite3
import time
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parent.parent
GOC_DU_LIEU = Path(os.environ.get("BRAIN_GOC_DU_LIEU") or GOC)     # worktree tam: tro ve repo chinh (data/ git bo qua)
KQ_MT5 = GOC / "reports" / "ong_dan" / "ket_qua_mt5"
UNG_VIEN = GOC / "reports" / "UNG_VIEN.md"
HANG_CHO_OD = GOC / "reports" / "ong_dan" / "hang_cho_mt5.jsonl"
RA = GOC / "reports" / "vong2"
HANG_CHO_V2 = RA / "hang_cho_vong2.jsonl"
VIEC_V2 = RA / "viec"

# ---------------------------------------------------------------------------------------------- NGUONG (tang)
NGUONG = {
    "A": {"ten": "TẦNG A (vàng)", "nam_mt5_min": 2.5, "lai_kep_stress_min": 15.0, "dd_equity_max": 60.0,
          "mc_dd_p95_max": 80.0, "doan_wf_lai_min": 5.0, "so_lenh_min": 100, "py_mt5": (0.8, 1.25),
          "ti_le_cap_khac_khong_lo_min": 0.5, "oos_python_lai_min": 10.0, "cao_nguyen_min": 0.6},
    "B": {"ten": "TẦNG B (bạc)", "nam_mt5_min": 2.0, "lai_kep_stress_min": 10.0, "dd_equity_max": 80.0,
          "mc_dd_p95_max": 95.0, "doan_wf_lai_min": 0.0, "so_lenh_min": 30, "py_mt5": (0.7, 1.4),
          "ti_le_cap_khac_khong_lo_min": 0.3, "oos_python_lai_min": 0.0, "cao_nguyen_min": 0.4},
}
STRESS = {"spread_he_so": 1.5, "hoa_hong_usd_100k_khu_hoi": 7.0}
MC_LAN = 1000


# ---------------------------------------------------------------------------------------------- A. MT5
def doc_vi_the(tep_lenh: Path) -> pd.DataFrame:
    """CSV deal MT5 -> moi POSITION mot dong: mo, dong, khoi_luong, gia_vao, gia_ra, loi (loi+swap+hoa hong), k (USD / 1 don vi gia)."""
    b = pd.read_csv(tep_lenh, sep=";")
    if b.empty:
        return pd.DataFrame()
    b["t"] = pd.to_datetime(b["thoi_gian"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    vr = b["vao_ra"].astype(str).str.lower()
    vao, ra = b[vr == "in"], b[vr.isin(["out", "out_by", "inout"])]
    ds = []
    for pos, g in ra.groupby("position"):
        v = vao[vao["position"] == pos]
        if v.empty:
            continue
        v = v.iloc[0]
        kl = g["khoi_luong"].astype(float).sum()
        gia_ra = float((g["gia"].astype(float) * g["khoi_luong"].astype(float)).sum() / max(kl, 1e-12))
        loi_gia = float(g["loi"].astype(float).sum())
        tong = loi_gia + float(g["swap"].astype(float).sum() + g["hoa_hong"].astype(float).sum())
        ds.append({"position": pos, "mo": v["t"], "dong": g["t"].max(), "chieu": int(v["chieu"]), "kl": float(v["khoi_luong"]),
                   "gia_vao": float(v["gia"]), "gia_ra": gia_ra, "loi_gia": loi_gia, "loi": tong,
                   "het_ky": bool(g["phu"].astype(str).str.contains("end of test", case=False).any())})
    # lenh con mo cuoi ky: EA khong ghi deal "out" (tester dong o cuoi) -> giu, gia_ra = NaN, dong = NaT (danh gia lai o cuoi)
    da = {d["position"] for d in ds}
    for _, v in vao[~vao["position"].isin(da)].iterrows():
        ds.append({"position": v["position"], "mo": v["t"], "dong": pd.NaT, "chieu": int(v["chieu"]), "kl": float(v["khoi_luong"]),
                   "gia_vao": float(v["gia"]), "gia_ra": np.nan, "loi_gia": 0.0, "loi": 0.0, "het_ky": True})
    p = pd.DataFrame(ds)
    if p.empty:
        return p
    d = p["gia_ra"] - p["gia_vao"]
    ok = (d.abs() > 1e-9) & p["gia_ra"].notna()
    p["k"] = np.where(ok, p["loi_gia"] / d.where(ok, 1.0), np.nan)
    # lenh dong dung gia vao: k = trung vi |k|/kl cung chieu * kl, dau theo chieu (suy tu lenh co k)
    co = p[ok & (p["k"].abs() > 0)]
    if len(co):
        dau = {c: float(np.sign(np.median(co[co["chieu"] == c]["k"]))) if (co["chieu"] == c).any() else None for c in p["chieu"].unique()}
        mua = [c for c, s in dau.items() if s and s > 0]
        dv = float(np.median((co["k"].abs() / co["kl"]).to_numpy()))
        for i in p.index[~ok | p["k"].isna()]:
            s = dau.get(p.at[i, "chieu"]) or (1.0 if (mua and p.at[i, "chieu"] in mua) else -1.0)
            p.at[i, "k"] = s * dv * p.at[i, "kl"]
    else:
        p["k"] = 0.0
    return p.sort_values("mo").reset_index(drop=True)


def doc_gia_mt5(tep_gia: Path) -> pd.DataFrame:
    g = pd.read_csv(tep_gia)
    g.index = pd.to_datetime(g["time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    return g[~g.index.isna()].sort_index()


def duong_von(p: pd.DataFrame, g: pd.DataFrame, von: float = 1000.0, chi_phi_them: pd.Series | None = None) -> pd.DataFrame:
    """Equity TAI DUNG moi nen: von + lai da dong + lai noi (k*(gia - gia_vao)) cua lenh dang mo.
    `xau` dung gia bat loi trong nen (low cho k>0, high cho k<0) -> DD xau nhat trong nen."""
    t = g.index
    n = len(t)
    noi = np.zeros(n); noi_xau = np.zeros(n); dong = np.zeros(n)
    c, h, l = g["close"].to_numpy(float), g["high"].to_numpy(float), g["low"].to_numpy(float)
    p = p.copy()
    mo_cuoi = p["dong"].isna()
    if mo_cuoi.any():                                # lenh con mo cuoi ky: dong o gia close nen cuoi (nhu tester)
        p.loc[mo_cuoi, "loi"] = p.loc[mo_cuoi, "k"] * (c[-1] - p.loc[mo_cuoi, "gia_vao"])
        p.loc[mo_cuoi, "dong"] = t[-1]
    loi = p["loi"].to_numpy(float) - (chi_phi_them.to_numpy(float) if chi_phi_them is not None else 0.0)
    for i, r in enumerate(p.itertuples()):
        a = t.searchsorted(r.mo, "left")
        b = t.searchsorted(r.dong, "left")          # nen chua lenh dong: tinh la da dong
        if b >= n:
            b = n - 1
        if b < n:
            dong[b] += loi[i]
        if b > a:
            noi[a:b] += r.k * (c[a:b] - r.gia_vao)
            noi_xau[a:b] += r.k * ((l[a:b] if r.k > 0 else h[a:b]) - r.gia_vao)
    eq_dong = von + np.cumsum(dong)
    return pd.DataFrame({"dong": eq_dong, "equity": eq_dong + noi, "equity_xau": eq_dong + noi_xau}, index=t)


def dd_pct(x) -> float:
    x = np.asarray(x, float)
    if not len(x):
        return 0.0
    dinh = np.maximum.accumulate(np.maximum(x, 1e-9))
    return float(np.max((dinh - x) / dinh) * 100)


def lai_kep(v0: float, v1: float, nam: float) -> float:
    if nam <= 0 or v0 <= 0:
        return 0.0
    return ((max(v1, 1e-9) / v0) ** (1 / nam) - 1) * 100


def chi_phi_stress(p: pd.DataFrame, g: pd.DataFrame, diem: float | None = None) -> pd.Series:
    """Phi them MOI lenh khi stress: +50% spread (spread_point*point tai luc mo) + hoa hong 7 USD/100k USD danh nghia."""
    if diem is None:
        so = g["close"].astype(str).str.split(".").str[-1].str.len().max()
        diem = 10.0 ** (-int(so or 5))
    sp = g["spread_point"].astype(float) if "spread_point" in g else pd.Series(0.0, index=g.index)
    hop = (sp > 0) & (sp <= 2000)                    # file _gia.csv co dong hong (am / hang tram nghin diem)
    sp = sp.where(hop, float(sp[hop].median()) if hop.any() else 0.0)
    i = g.index.searchsorted(p["mo"], "right") - 1
    spg = sp.to_numpy()[np.clip(i, 0, len(sp) - 1)] * diem
    them_sp = (STRESS["spread_he_so"] - 1.0) * spg * p["k"].abs().to_numpy()
    hh = STRESS["hoa_hong_usd_100k_khu_hoi"] / 1e5 * p["k"].abs().to_numpy() * p["gia_vao"].to_numpy()
    return pd.Series(them_sp + hh, index=p.index)


def walk_forward(dv: pd.DataFrame, doan: int = 3) -> list[dict]:
    t = dv.index
    moc = [t[0] + (t[-1] - t[0]) * k / doan for k in range(doan + 1)]
    ra = []
    for a, b in zip(moc[:-1], moc[1:]):
        x = dv[(dv.index >= a) & (dv.index <= b)]
        if len(x) < 10:
            continue
        nam = (x.index[-1] - x.index[0]).days / 365.25
        ra.append({"tu": str(x.index[0].date()), "den": str(x.index[-1].date()),
                   "lai_kep_pct_nam": round(lai_kep(x["equity"].iloc[0], x["equity"].iloc[-1], nam), 2),
                   "dd_equity_pct": round(dd_pct(x["equity_xau"]), 2)})
    return ra


def monte_carlo(loi: np.ndarray, von: float, lan: int = MC_LAN, hat: int = 7) -> dict:
    """Xao thu tu lai/lo lenh dong (permutation) + bootstrap co hoan lai. Chi tren lenh dong -> nhan MÔ PHỎNG.
    Voi he DCA / khong SL, DD lenh dong gan 0 -> xem them monte_carlo_equity."""
    rng = np.random.default_rng(hat)
    loi = np.asarray(loi, float)
    if len(loi) < 5:
        return {"loi": "ít lệnh"}
    dd_x, cuoi_b, chay = [], [], 0
    for _ in range(lan):
        e = von + np.cumsum(rng.permutation(loi)); dd_x.append(dd_pct(np.r_[von, e]))
        e2 = von + np.cumsum(rng.choice(loi, len(loi))); cuoi_b.append(e2[-1])
        chay += int(np.min(e2) <= 0)
    return {"dd_dong_xao_p50": round(float(np.percentile(dd_x, 50)), 2), "dd_dong_xao_p95": round(float(np.percentile(dd_x, 95)), 2),
            "von_cuoi_bootstrap_p5": round(float(np.percentile(cuoi_b, 5)), 2), "ti_le_chay_bootstrap": round(chay / lan, 4),
            "nhan": "MÔ PHỎNG (xáo %d lần, trên lệnh đã đóng)" % lan}


def monte_carlo_equity(dv: pd.DataFrame, lan: int = MC_LAN, khoi_ngay: int = 10, hat: int = 11) -> dict:
    """Xao KHOI ngay (block bootstrap, giu chuoi ngay lien nhau `khoi_ngay`) cua lai/lo EQUITY ngay + do sut trong ngay
    (equity_xau thap nhat so voi dong cua hom truoc). Do duoc DD cho he DCA / hedge khong SL. MÔ PHỎNG."""
    rng = np.random.default_rng(hat)
    c = dv["equity"].resample("1D").last().dropna()
    lo = dv["equity_xau"].resample("1D").min().reindex(c.index)
    if len(c) < 3 * khoi_ngay:
        return {"loi": "ít ngày"}
    truoc = c.shift(1).fillna(float(dv["equity"].iloc[0])).clip(lower=1e-6)
    d = (c / truoc).clip(lower=0.0).to_numpy()                   # LOI SUAT ngay (khong dung USD: he lai kep)
    dip = np.minimum((lo / truoc).to_numpy(), d)                 # muc thap nhat trong ngay / dong cua hom truoc
    n = len(d); khoi = [(i, min(i + khoi_ngay, n)) for i in range(0, n, khoi_ngay)]
    v0 = 1.0; dds, cuoi, chay = [], [], 0
    for _ in range(lan):
        ph = []
        while sum(len(x) for x in ph) < n:
            ph.append(np.arange(*khoi[int(rng.integers(len(khoi)))]))
        idx = np.concatenate(ph)[:n]
        eq = np.cumprod(d[idx])
        thap = np.r_[v0, eq[:-1]] * np.minimum(dip[idx], 1.0)
        x = np.empty(2 * n); x[0::2] = thap; x[1::2] = eq
        dds.append(min(dd_pct(np.r_[v0, x]), 100.0)); cuoi.append(eq[-1]); chay += int(np.min(x) <= 0.0)
    return {"dd_equity_p50": round(float(np.percentile(dds, 50)), 2), "dd_equity_p95": round(float(np.percentile(dds, 95)), 2),
            "he_so_von_cuoi_p5": round(float(np.percentile(cuoi, 5)), 3), "ti_le_chay": round(chay / lan, 4),
            "nhan": "MÔ PHỎNG (block bootstrap %d ngày, %d lần, equity tái dựng)" % (khoi_ngay, lan)}


def _khop_net(dv: pd.DataFrame, lech: float) -> pd.DataFrame:
    """Lenh con mo cuoi ky thieu swap trong log EA -> cong phan lech (net bao cao - net tai dung) vao nen cuoi."""
    if lech:
        dv = dv.copy(); dv.iloc[-1] = dv.iloc[-1] + lech
    return dv


def phan_tich_mt5(ten: str, thu_muc: Path = KQ_MT5, von: float = 1000.0, net_bao_cao: float | None = None) -> dict:
    tl, tg = thu_muc / (ten + "_vao.csv_lenh_mt5.csv"), thu_muc / (ten + "_vao.csv_gia.csv")
    if not tl.exists() or not tg.exists():
        return {"ten": ten, "loi": "CHƯA ĐO ĐƯỢC: thiếu lệnh/giá MT5"}
    p, g = doc_vi_the(tl), doc_gia_mt5(tg)
    if p.empty or g.empty:
        return {"ten": ten, "loi": "CHƯA ĐO ĐƯỢC: không có lệnh"}
    dv = duong_von(p, g, von)
    net_td = float(dv["equity"].iloc[-1] - von)
    lech = (float(net_bao_cao) - net_td) if net_bao_cao is not None else 0.0
    dv = _khop_net(dv, lech)
    cp = chi_phi_stress(p, g)
    dvs = _khop_net(duong_von(p, g, von, cp), lech)
    nam = (g.index[-1] - g.index[0]).days / 365.25
    # MC: DD lenh dong xao, quy doi sang equity bang ti le DD_equity/DD_dong do that cua chinh he
    mc = monte_carlo(p.sort_values("dong")["loi"].to_numpy(), von)
    ddd, dde = dd_pct(dv["dong"]), dd_pct(dv["equity_xau"])
    mc["equity"] = monte_carlo_equity(dvs)               # MC tren equity SAU stress phi
    ngay = dv["equity"].resample("1D").last().dropna()
    return {"ten": ten, "_dv": dv, "so_lenh": int(len(p)), "so_lenh_het_ky": int(p["het_ky"].sum()), "so_nam": round(nam, 2),
            "tu": str(g.index[0].date()), "den": str(g.index[-1].date()),
            "lai_kep_pct_nam": round(lai_kep(von, dv["equity"].iloc[-1], nam), 2),
            "lai_kep_stress_pct_nam": round(lai_kep(von, dvs["equity"].iloc[-1], nam), 2),
            "phi_stress_usd": round(float(cp.sum()), 2), "lai_rong_tai_dung": round(net_td, 2),
            "lech_net_khop_cuoi_ky": round(lech, 2),
            "dd_dong_pct": round(ddd, 2), "dd_equity_dong_nen_pct": round(dd_pct(dv["equity"]), 2),
            "dd_equity_pct": round(dde, 2), "dd_equity_stress_pct": round(dd_pct(dvs["equity_xau"]), 2),
            "walk_forward": walk_forward(dv), "monte_carlo": mc,
            "lai_ngay": {str(k.date()): round(float(v), 2) for k, v in ngay.diff().dropna().items()},
            "nhan": "ĐO THẬT (lệnh MT5 real tick); equity TÁI DỰNG theo giá H1 của chính lần chạy; stress/MC = MÔ PHỎNG"}


# ---------------------------------------------------------------------------------------------- doc ung vien
def ung_vien_dat(p: Path = UNG_VIEN) -> list[dict]:
    from nhan import so_co_che as SO
    ra, thay = [], set()
    for r in SO.doc_ung_vien(p):
        if r["ket_luan"] == "ĐẠT" and r["ten"] not in thay:
            thay.add(r["ten"]); ra.append(r)
    # Py/MT5 tu bang xep hang
    tl = {}
    for d in p.read_text(encoding="utf-8").splitlines() if p.exists() else []:
        c = [x.strip() for x in d.strip().strip("|").split("|")]
        if len(c) >= 12 and c[0].isdigit() and c[1].startswith("od_"):
            try:
                tl[c[1]] = float(c[10])
            except ValueError:
                pass
    for r in ra:
        r["py_mt5"] = tl.get(r["ten"])
    return ra


def viec_goc(ten: str, p: Path = HANG_CHO_OD) -> dict | None:
    if not p.exists():
        return None
    for x in p.read_text(encoding="utf-8").splitlines():
        if ('"%s"' % ten) in x:
            v = json.loads(x)
            if v.get("ten") == ten:
                return v
    return None


def xep_tang(m: dict, py: dict | None = None) -> dict:
    """Ap NGUONG -> tang A / B / C. Thieu so do -> ghi 'chưa đo' (khong tinh la dat)."""
    py = py or {}
    kq = {}
    for t, n in NGUONG.items():
        ly = []
        if m.get("loi"):
            ly.append(m["loi"])
        else:
            if m["so_nam"] < n["nam_mt5_min"]:
                ly.append("lịch sử MT5 %.1f < %.1f năm" % (m["so_nam"], n["nam_mt5_min"]))
            if m["lai_kep_stress_pct_nam"] < n["lai_kep_stress_min"]:
                ly.append("lãi kép sau stress %.1f < %.0f%%" % (m["lai_kep_stress_pct_nam"], n["lai_kep_stress_min"]))
            if m["dd_equity_stress_pct"] > n["dd_equity_max"]:
                ly.append("DD equity stress %.1f > %.0f%%" % (m["dd_equity_stress_pct"], n["dd_equity_max"]))
            q = (m.get("monte_carlo") or {}).get("equity", {}).get("dd_equity_p95")
            if q is None or q > n["mc_dd_p95_max"]:
                ly.append("MC DD p95 %s > %.0f%%" % (q, n["mc_dd_p95_max"]))
            wf = [d["lai_kep_pct_nam"] for d in m.get("walk_forward") or []]
            if not wf or min(wf) < n["doan_wf_lai_min"]:
                ly.append("đoạn WF tệ nhất %s < %.0f%%" % (min(wf) if wf else None, n["doan_wf_lai_min"]))
            if m["so_lenh"] < n["so_lenh_min"]:
                ly.append("lệnh %d < %d" % (m["so_lenh"], n["so_lenh_min"]))
        r = py.get("py_mt5")
        if r is None or not (n["py_mt5"][0] <= r <= n["py_mt5"][1]):
            ly.append("Python/MT5 %s ngoài %s–%s" % (r, *n["py_mt5"]))
        tc = py.get("ti_le_cap_khac_khong_lo")
        if tc is None or tc < n["ti_le_cap_khac_khong_lo_min"]:
            ly.append("đa cặp %s < %.0f%%" % (None if tc is None else round(tc * 100), n["ti_le_cap_khac_khong_lo_min"] * 100))
        oo = py.get("oos_lai")
        if oo is None or oo < n["oos_python_lai_min"]:
            ly.append("OOS Python %s < %.0f%%" % (oo, n["oos_python_lai_min"]))
        cn_ = py.get("cao_nguyen")
        if cn_ is None or cn_ < n["cao_nguyen_min"]:
            ly.append("cao nguyên %s < %.1f" % (cn_, n["cao_nguyen_min"]))
        kq[t] = ly
    tang = "A" if not kq["A"] else ("B" if not kq["B"] else "C")
    return {"tang": tang, "thieu_A": kq["A"], "thieu_B": kq["B"]}


# ---------------------------------------------------------------------------------------------- B. Python
LUOI_QL = {"tp_pct": [0.001, 0.0015, 0.002, 0.003, 0.005], "dca_buoc_pct": [0.002, 0.003, 0.005, 0.008, 0.012],
           "dca_toi_da": [0, 3, 5, 7], "dca_he_so_lot": [1.0, 1.3, 1.6, 2.0]}
# lot KHONG nam trong luoi: lot chi doi don bay (lai/DD gan tuyen tinh) -> giu lot cua he vong 1


def _diem(r: dict) -> float:
    if r.get("loi") or r.get("chay") or r.get("so_stop_out"):
        return -100.0
    dd = float(r.get("sut_giam_pct") or 100)
    if dd > 80:
        return -50.0
    lai = float(r["lai_pct_nam"])
    if lai < 10.0:
        return lai / 10.0 - 1.0                                   # duoi chuan vong 1 (>= 10 %/nam) -> am
    return lai / max(dd, 10.0) * 10        # lai tren rui ro, chong chon DD cao


def _gan(v, ds):
    return min(range(len(ds)), key=lambda i: abs(ds[i] - v)) if v is not None else 0


KHONG_CO_CHU_KY = {"tre", "ngay_trong_tuan", "gio", "phut", "hang"}
HE_SO_N = [0.5, 0.75, 1.0, 1.25, 1.5]


def nhan_chu_ky(t: dict, he: float) -> dict:
    """Spec DSL: nhan moi chu ky chi bao (`n`, tru do tre / lich) voi `he` (input chi bao cua tac gia = he 1.0)."""
    if he == 1.0 or (t.get("tin_hieu") or {}).get("kieu") != "spec":
        return t

    def di(x):
        if isinstance(x, dict):
            y = {k: di(v) for k, v in x.items()}
            if "n" in y and isinstance(y["n"], (int, float)) and y.get("chi_bao") not in KHONG_CO_CHU_KY:
                y["n"] = max(2, int(round(y["n"] * he)))
            return y
        if isinstance(x, list):
            return [di(v) for v in x]
        return x
    th = dict(t["tin_hieu"], specs=[dict(sp, vao=di(sp.get("vao"))) for sp in t["tin_hieu"]["specs"]])
    return dict(t, id="%s_n%s" % (t["id"], str(he).replace(".", "")), tin_hieu=th)


def python_v2(t: dict, thu: dict, cfg: dict, ngan_sach: int = 90, hat: int = 1, ds_ma: list[str] | None = None) -> dict:
    """Luoi tho quanh thu goc: (1) mac dinh tac gia, (2) khung H1/H4, (3) da cap, (4) luoi quan li + input chi bao,
    cao nguyen = ti le hang xom (+-1 nac moi chieu) van >= 70% diem goc va khong stop-out."""
    from nhan import ong_dan as OD
    rng = np.random.default_rng(hat)
    t0 = time.time()

    def chay(x, he=1.0):
        r = OD.danh_gia(nhan_chu_ky(t, he), x, cfg)
        return {k: (float(v) if isinstance(v, (np.floating, np.integer)) else v) for k, v in r.items()
                if k in ("lai_pct_nam", "sut_giam_pct", "so_lenh", "so_stop_out", "chay", "so_nam", "loi")} | \
               {"oos": {k: float(v) if isinstance(v, (np.floating,)) else v for k, v in (r.get("oos") or {}).items()}}
    goc = chay(thu)
    mac_dinh = chay(dict(thu, tham={})) if thu.get("tham") else goc
    khung = {k: chay(dict(thu, khung=k)) for k in ("H1", "H4") if k != thu["khung"]}
    khung[thu["khung"]] = goc
    ds_ma = ds_ma if ds_ma is not None else OD.ma_co_du_lieu(cfg)
    ma = {}
    if not (t.get("tin_hieu") or {}).get("ma"):            # the gan voi ma cu the -> khong thu da cap
        for m in ds_ma:
            if m != thu["ma"]:
                ma[m] = chay(dict(thu, ma=m))
    khac = [r for r in ma.values() if not r.get("loi")]
    ti_le = (sum(1 for r in khac if r["lai_pct_nam"] > 0 and not r.get("so_stop_out") and not r.get("chay")) / len(khac)) if khac else None
    # luoi: toa do = chi so trong LUOI_QL + khoang tin hieu
    kg = {k: list(v) for k, v in ((t.get("tin_hieu") or {}).get("khoang") or {}).items() if isinstance(v, list) and len(v) > 1}
    chieu = {**{"ql." + k: v for k, v in LUOI_QL.items()}, **{"th." + k: v for k, v in kg.items()}}
    if (t.get("tin_hieu") or {}).get("kieu") == "spec":
        chieu["sp.he_so_n"] = HE_SO_N
    ten_c = list(chieu)
    g0 = tuple(_gan(thu["ql"].get(k[3:]) if k.startswith("ql.") else
                    (1.0 if k == "sp.he_so_n" else (thu.get("tham") or {}).get(k[3:])), chieu[k]) for k in ten_c)

    def he_cua(toa):
        return chieu["sp.he_so_n"][toa[ten_c.index("sp.he_so_n")]] if "sp.he_so_n" in chieu else 1.0

    def thu_tu(toa):
        ql = dict(thu["ql"]); th = dict(thu.get("tham") or {})
        for k, i in zip(ten_c, toa):
            if k.startswith("ql."):
                ql[k[3:]] = chieu[k][i]
            elif k.startswith("th."):
                th[k[3:]] = chieu[k][i]
        return dict(thu, ql=ql, tham=th)
    luoi = {g0: goc}
    diem_luoi = []
    # hang xom +-1 cua goc truoc (do cao nguyen goc), roi ngau nhien
    for j in range(len(ten_c)):
        for d in (-1, 1):
            x = list(g0); x[j] += d
            if 0 <= x[j] < len(chieu[ten_c[j]]):
                diem_luoi.append(tuple(x))
    nua = max(ngan_sach // 2, len(diem_luoi))
    while len(diem_luoi) < nua:
        diem_luoi.append(tuple(int(rng.integers(len(chieu[k]))) for k in ten_c))

    def hang_xom(toa):
        for j in range(len(ten_c)):
            for d in (-1, 1):
                x = list(toa); x[j] += d
                if 0 <= x[j] < len(chieu[ten_c[j]]):
                    yield tuple(x)
    for toa in diem_luoi:
        if toa not in luoi:
            luoi[toa] = chay(thu_tu(toa), he_cua(toa))
    # pha 2: do du hang xom cua cac diem tot nhat (de do cao nguyen), toi het ngan sach
    da_mo = set()
    while len(luoi) < ngan_sach + 1:
        ung = [k for k in sorted(luoi, key=lambda k: -_diem(luoi[k])) if k not in da_mo and _diem(luoi[k]) > 0]
        if not ung:
            break
        da_mo.add(ung[0])
        for x in hang_xom(ung[0]):
            if x not in luoi and len(luoi) < ngan_sach + 1:
                luoi[x] = chay(thu_tu(x), he_cua(x))

    def cao_nguyen(toa):
        s0 = _diem(luoi[toa]); hx = []
        for j in range(len(ten_c)):
            for d in (-1, 1):
                x = list(toa); x[j] += d
                if tuple(x) in luoi:
                    hx.append(_diem(luoi[tuple(x)]))
        if not hx or s0 <= 0:
            return None, len(hx)
        return round(sum(1 for h in hx if h >= 0.7 * s0) / len(hx), 2), len(hx)
    xep = []
    for toa, r in luoi.items():
        cn_, n_hx = cao_nguyen(toa)
        oos = (r.get("oos") or {}).get("lai_pct_nam")
        xep.append({"toa": toa, "diem": _diem(r), "cao_nguyen": cn_, "so_hang_xom": n_hx, "oos": oos, "r": r})
    # chon: phai co >=2 hang xom do, cao nguyen >= 0.6, OOS > 0; diem cao nguyen = diem * cao_nguyen
    tot = [x for x in xep if x["cao_nguyen"] is not None and x["so_hang_xom"] >= 2 and x["cao_nguyen"] >= 0.6 and (x["oos"] or -1) > 0]
    tot.sort(key=lambda x: -x["diem"] * x["cao_nguyen"])
    cn_goc, _ = cao_nguyen(g0)
    return {"goc": goc, "mac_dinh_tac_gia": mac_dinh, "khung": khung, "da_cap": ma, "ti_le_cap_khac_khong_lo": ti_le,
            "cao_nguyen_goc": cn_goc, "so_phep_thu": len(luoi) + len(ma) + len(khung),
            "tot_nhat": [{"thu": thu_tu(x["toa"]), "he_so_n": he_cua(x["toa"]), "diem": round(x["diem"], 2), "cao_nguyen": x["cao_nguyen"],
                          "lai_pct_nam": x["r"].get("lai_pct_nam"), "sut_giam_pct": x["r"].get("sut_giam_pct"),
                          "oos_lai_pct_nam": x["oos"], "so_lenh": x["r"].get("so_lenh")} for x in tot[:3]],
            "giay": round(time.time() - t0, 1), "nhan": "MÔ PHỎNG (Python, dữ liệu box)"}


# ---------------------------------------------------------------------------------------------- C. ghep cung cap
def ban_ghep(cn, a_id: str, ma: str, so_ghi: list[dict], toi_da: int = 3) -> list[dict]:
    """Chon B cho A tren cung cap tu so co che: B chay duoc Python, KHAC phong cach vao, uu tien DAT_MT5 > DAT_PY > GAN_DAT."""
    a = next((r for r in so_ghi if r["id"] == a_id), None) or {}
    pa = set(a.get("phong_cach") or [])
    hang = {"DAT_MT5": 0, "DAT_PY": 1, "GAN_DAT": 2}
    ds = []
    for r in so_ghi:
        if r["id"] == a_id or r.get("trang_thai") not in hang or not r.get("chay_python"):
            continue
        pb = set(r.get("phong_cach") or [])
        if not pb or pb == pa:
            continue
        cung_ma = ma in (r.get("ma") or [])
        ds.append((hang[r["trang_thai"]] - (0.5 if cung_ma else 0), -(r.get("python") or {}).get("lai_pct_nam", 0) or 0, r))
    ds.sort(key=lambda x: (x[0], x[1]))
    out = []
    for _, _, r in ds:
        row = cn.execute("SELECT json FROM the WHERE id=?", (r["id"],)).fetchone()
        if row and json.loads(row[0]).get("tin_hieu"):
            out.append({"id": r["id"], "tin_hieu": json.loads(row[0])["tin_hieu"], "phong_cach": r.get("phong_cach")})
        if len(out) >= toi_da:
            break
    return out


def the_ghep(a: dict, b: dict, kieu: str) -> dict:
    """kieu: xac_nhan (A chi vao khi B cung chieu <=3 nen) | them_lenh (A + B, go cheo) | nguoc (B chi vao NGUOC A = hedge)."""
    th = {"kieu": "to_hop", "nguon": a["tin_hieu"], "bo_loc": []}
    if kieu == "xac_nhan":
        th["bo_loc"] = [{"tham": {"kieu": "xac_nhan", "cua_so": 3}, "nguon": b["tin_hieu"]}]
    else:
        th["nguon_b"] = b["tin_hieu"]
        th["kieu_b"] = "them" if kieu == "them_lenh" else "nguoc"
    i = "v2g_" + hashlib.sha1(json.dumps([a["id"], b["id"], kieu]).encode()).hexdigest()[:10]
    return {"id": i, "tin_hieu": th, "ghep_v2": {"a": a["id"], "b": b["id"], "kieu": kieu}}


# ---------------------------------------------------------------------------------------------- D. danh muc
def danh_muc_v2(phan_tich: dict[str, dict], tq_max: float = 0.3, toi_da: int = 4, von: float = 1000.0) -> list[dict]:
    """Tham lam theo lai/DD: lai ngay tu equity TAI DUNG (lenh MT5 that); them he neu tuong quan ngay voi moi he trong
    danh muc <= tq_max va diem (lai/DD equity) cua danh muc tang. DD tinh tren equity cong theo GIO (khong chi lenh dong)."""
    ok = {k: v for k, v in phan_tich.items() if not v.get("loi") and v["so_nam"] >= 1.5 and v.get("_dv") is not None}
    if len(ok) < 2:
        return []
    ngay = pd.DataFrame({k: pd.Series(v["lai_ngay"]) for k, v in ok.items()}).fillna(0.0)
    tq = ngay.corr()

    def do(nhom):
        dv = pd.DataFrame({k: ok[k]["_dv"]["equity_xau"] - von for k in nhom}).sort_index().ffill().dropna()
        dvc = pd.DataFrame({k: ok[k]["_dv"]["equity"] - von for k in nhom}).sort_index().ffill().dropna()
        v0 = von * len(nhom)
        eq, eqc = v0 + dv.sum(axis=1), v0 + dvc.sum(axis=1)
        nam = (eq.index[-1] - eq.index[0]).days / 365.25
        lai = lai_kep(v0, eqc.iloc[-1], nam); dd = dd_pct(eq)
        m = tq.loc[list(nhom), list(nhom)].to_numpy()
        return {"he": list(nhom), "lai_kep_pct_nam": round(lai, 2), "dd_equity_pct": round(dd, 2),
                "tuong_quan_ngay_max": round(float(np.max(m[np.triu_indices_from(m, 1)])), 3) if len(nhom) > 1 else 0.0,
                "so_nam": round(nam, 2), "tu": str(eq.index[0].date()), "den": str(eq.index[-1].date()), "von": v0,
                "diem": lai / max(dd, 5.0),
                "nhan": "ĐO THẬT từ lệnh MT5; DD trên EQUITY tái dựng theo giờ (gồm lệnh đang mở, giá bất lợi trong nến)"}
    xep = sorted(ok, key=lambda k: -(ok[k]["lai_kep_stress_pct_nam"] / max(ok[k]["dd_equity_pct"], 5)))
    ra, thay = [], set()
    for goc in xep[:8]:
        nhom = [goc]; cur = do(nhom)
        for k in xep:
            if k in nhom or len(nhom) >= toi_da or any(tq.at[k, x] > tq_max for x in nhom):
                continue
            th = do(nhom + [k])
            if th["diem"] > cur["diem"] and th["dd_equity_pct"] <= 80:
                nhom, cur = nhom + [k], th
        key = tuple(sorted(nhom))
        if len(nhom) >= 2 and key not in thay:
            thay.add(key); ra.append(cur)
    ra.sort(key=lambda m: -m["diem"])
    return ra


# ---------------------------------------------------------------------------------------------- E. hang cho
def _doi_ten(v: dict, hau_to: str) -> dict:
    """Doi ten viec + file CSV/.set/.ini sang od_v2..., tranh dung so cai vong 1."""
    cu = v["ten"]
    moi = "od_v2%s_%s" % (hau_to, cu[3:])
    if len(moi) > 60:                                     # gioi han ten (bao cao MT5 / Common\Files)
        moi = moi[:47] + hashlib.sha1(moi.encode()).hexdigest()[:6] + "_XM_CSV"
    d = GOC / Path(v["csv_vao"]).parent
    for duoi in ("_vao.csv", ".set", ".ini"):
        f = d / (cu + duoi)
        if f.exists():
            txt = f.read_text(encoding="ascii").replace(cu, moi)
            (d / (moi + duoi)).write_text(txt, encoding="ascii"); f.unlink()
    v = dict(v, ten=moi, csv_vao=str((Path(v["csv_vao"]).parent / (moi + "_vao.csv")).as_posix()))
    v["ts"] = {k: (x.replace(cu, moi) if isinstance(x, str) else x) for k, x in v["ts"].items()}
    return v


def sinh_viec_v2(t: dict, thu: dict, r: dict, cfg: dict, pha: str, hau_to: str, diem: float, them: dict | None = None) -> list[dict]:
    from nhan import ong_dan as OD
    d = VIEC_V2 / re.sub(r"[^A-Za-z0-9_]", "", t["id"])[:40]
    d.mkdir(parents=True, exist_ok=True)
    cfg = dict(cfg, san_mt5={k: v for k, v in (cfg.get("san_mt5") or {}).items() if k == "XM"})   # XM micro (chuan vong 1)
    ra = []
    for v in OD.viec_csv(t, thu, r, cfg, d):
        v = _doi_ten(v, hau_to)
        v.update({"pha": pha, "nguon": "ong_dan", "vong": 2, "diem": diem, **(them or {})})
        ra.append(v)
    return ra


def ghi_hang_cho(ds: list[dict], tep: Path = HANG_CHO_V2) -> int:
    tep.parent.mkdir(parents=True, exist_ok=True)
    cu = {}
    if tep.exists():
        for x in tep.read_text(encoding="utf-8").splitlines():
            try:
                v = json.loads(x); cu[v["ten"]] = v
            except (ValueError, KeyError):
                pass
    for v in ds:
        cu[v["ten"]] = v
    # ghep trung: hai B khac id nhung cung tin hieu (vd 2 the dich tu cung mot EA) -> cung so Python + cung so lenh CSV
    thay, bo = set(), []
    for k in sorted(cu):
        v = cu[k]
        if v.get("pha") == "V2_GHEP":
            kh = (v.get("vong2_goc"), (v.get("ghep_v2") or {}).get("kieu"), v.get("so_lenh_csv"),
                  json.dumps(v.get("python"), sort_keys=True, default=str))
            if kh in thay:
                bo.append(k); continue
            thay.add(kh)
    for k in bo:
        v = cu.pop(k)
        for duoi in ("_vao.csv", ".set", ".ini"):
            f = GOC / Path(v["csv_vao"]).parent / (k + duoi)
            if f.exists():
                f.unlink()
    tep.write_text("".join(json.dumps(cu[k], ensure_ascii=False, sort_keys=True, default=str) + "\n" for k in sorted(cu)), encoding="utf-8")
    return len(cu)


# ---------------------------------------------------------------------------------------------- dieu phoi
def _so(x):
    if isinstance(x, dict):
        return {k: _so(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, (list, tuple)):
        return [_so(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    return x


def chay(top: int = 12, ngan_sach: int = 90, co_python: bool = True, in_ra=print) -> dict:
    from nhan import ong_dan as OD
    from nhan import so_co_che as SO
    RA.mkdir(parents=True, exist_ok=True)
    uv = ung_vien_dat()
    in_ra("vong2: %d hệ ĐẠT vòng 1" % len(uv), flush=True)
    pt = {}
    for r in uv:
        m = phan_tich_mt5(r["ten"], net_bao_cao=r.get("lai_rong"))
        m.update({"the_id": r["the_id"], "symbol": r["symbol"], "tf": r["tf"], "py_mt5": r.get("py_mt5"),
                  "dd_bao_cao_pct": r["dd_von_pct"], "lai_kep_bao_cao": r["lai_kep_pct_nam"],
                  "lai_rong_bao_cao": r["lai_rong"]})
        pt[r["ten"]] = m
    dm = danh_muc_v2(pt)
    py_kq, ghep_kq, viec = {}, [], []
    if co_python:
        cfg = OD.cau_hinh()
        cfg["du_lieu"] = {k: v for k, v in (cfg.get("du_lieu") or {}).items()}
        cn = sqlite3.connect(str(GOC_DU_LIEU / "data" / "ong_dan" / "trang_thai.sqlite"))
        so_ghi = SO.doc()
        chay_duoc = []
        for k, m in pt.items():
            row = cn.execute("SELECT json, kq FROM the WHERE id=?", (m["the_id"],)).fetchone()
            if not row or not (json.loads(row[0]).get("tin_hieu")) or not (json.loads(row[1] or "{}").get("tot_nhat") or {}).get("thu"):
                py_kq[k] = {"loi": "CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM)"}
            elif not m.get("loi"):
                chay_duoc.append((k, row))
        chay_duoc.sort(key=lambda z: -(pt[z[0]]["lai_kep_stress_pct_nam"] / max(pt[z[0]]["dd_equity_stress_pct"], 5)))
        for ten, row in chay_duoc[:top]:
            m = pt[ten]
            v0 = viec_goc(ten) or {}
            t, kq = json.loads(row[0]), json.loads(row[1] or "{}")
            thu = (kq.get("tot_nhat") or {}).get("thu")
            if v0.get("python_ql") and thu:
                thu = dict(thu, ql=v0["python_ql"], khung=m["tf"])
            if not thu:
                py_kq[ten] = {"loi": "CHƯA ĐO ĐƯỢC: thẻ không có phép thử tốt nhất"}; continue
            in_ra("  python_v2 %s (%s %s)" % (ten, thu["ma"], thu["khung"]), flush=True)
            try:
                p2 = python_v2(t, thu, cfg, ngan_sach=ngan_sach)
            except Exception as e:                        # the hong / thieu cache dich -> ghi, khong dung ca vong
                py_kq[ten] = {"loi": "LỖI: %s" % str(e)[:200]}; continue
            py_kq[ten] = p2
            m["xep"] = xep_tang(m, {"py_mt5": m.get("py_mt5"), "ti_le_cap_khac_khong_lo": p2["ti_le_cap_khac_khong_lo"],
                                    "oos_lai": (p2["goc"].get("oos") or {}).get("lai_pct_nam"), "cao_nguyen": p2["cao_nguyen_goc"]})
            # viec MT5: cao nguyen tot nhat, cap khac tot nhat (2), khung khac
            for j, x in enumerate(p2["tot_nhat"][:1]):
                viec += sinh_viec_v2(nhan_chu_ky(t, x.get("he_so_n", 1.0)), x["thu"], x, cfg, "V2_CAO_NGUYEN", "cn", 70 + min(x["lai_pct_nam"] or 0, 40) / 4,
                                     {"vong2_goc": ten, "nhan_python": "MÔ PHỎNG", "cao_nguyen": x["cao_nguyen"],
                                      "he_so_chu_ky": x.get("he_so_n", 1.0)})
            cap = sorted([(k, r) for k, r in p2["da_cap"].items() if not r.get("loi") and _diem(r) > 0 and
                          (r.get("oos") or {}).get("lai_pct_nam", -1) > 0], key=lambda z: -_diem(z[1]))[:2]
            for k, r in cap:
                viec += sinh_viec_v2(t, dict(thu, ma=k), r, cfg, "V2_DA_CAP", "cap" + k.lower(), 65 + min(r["lai_pct_nam"], 40) / 4,
                                     {"vong2_goc": ten, "nhan_python": "MÔ PHỎNG"})
            for k, r in p2["khung"].items():
                if k != thu["khung"] and not r.get("loi") and _diem(r) > 0:
                    viec += sinh_viec_v2(t, dict(thu, khung=k), r, cfg, "V2_KHUNG", "tf" + k.lower(), 62, {"vong2_goc": ten})
            # ghep cung cap (C)
            a = {"id": t["id"], "tin_hieu": t["tin_hieu"]}
            for b in ban_ghep(cn, t["id"], thu["ma"], so_ghi):
                for kieu in ("xac_nhan", "them_lenh", "nguoc"):
                    tg = the_ghep(a, b, kieu)
                    try:
                        rg = OD.danh_gia(tg, thu, cfg)
                    except Exception as e:
                        rg = {"loi": str(e)[:200]}
                    g = {"goc": ten, "a": t["id"], "b": b["id"], "phong_cach_b": b["phong_cach"], "kieu": kieu,
                         "ma": thu["ma"], "khung": thu["khung"],
                         **{k: _so(rg.get(k)) for k in ("lai_pct_nam", "sut_giam_pct", "so_lenh", "so_stop_out", "oos", "loi")},
                         "goc_lai": p2["goc"].get("lai_pct_nam"), "goc_dd": p2["goc"].get("sut_giam_pct"), "nhan": "MÔ PHỎNG"}
                    ghep_kq.append(g)
                    if not rg.get("loi") and _diem(rg) > _diem(p2["goc"]) and (rg.get("oos") or {}).get("lai_pct_nam", -1) > 0:
                        viec += sinh_viec_v2(tg, thu, rg, cfg, "V2_GHEP", "g" + kieu[:2], 66 + min(rg["lai_pct_nam"], 40) / 4,
                                             {"vong2_goc": ten, "ghep_v2": tg["ghep_v2"], "nhan_python": "MÔ PHỎNG"})
        cn.close()
    for m in pt.values():
        if "xep" not in m:
            m["xep"] = xep_tang(m, {"py_mt5": m.get("py_mt5")})
    n = ghi_hang_cho(viec) if viec else (len(HANG_CHO_V2.read_text().splitlines()) if HANG_CHO_V2.exists() else 0)
    kq = {"luc": time.strftime("%Y-%m-%d %H:%M"), "nguong": NGUONG, "stress": STRESS, "mt5": _so(pt), "python": _so(py_kq),
          "ghep_cung_cap": ghep_kq, "danh_muc": _so(dm), "so_viec_moi": len(viec), "so_viec_hang_cho": n}
    for m in pt.values():
        m.pop("lai_ngay", None)
    (RA / "ket_qua_vong2.json").write_text(json.dumps(_so(kq), ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (RA / "KET_QUA_VONG2.md").write_text(ghi_md(kq), encoding="utf-8")
    in_ra("vong2: %d việc MT5 mới, hàng chờ %d" % (len(viec), n))
    return kq


def _f(x, d=1):
    return "—" if x is None else (("%." + str(d) + "f") % x if isinstance(x, (int, float)) else str(x))


def ghi_md(kq: dict) -> str:
    L = ["# Vòng 2 — kết quả (tự sinh bởi `python -m nhan.vong2`)", "",
         "Lúc chạy: %s (giờ box, UTC+7). Ngưỡng tầng: xem `tai_lieu/VONG_2.md`." % kq["luc"], "",
         "**Nhãn:** cột MT5 = ĐO THẬT (lệnh real tick vòng 1); equity *tái dựng* từ lệnh + giá H1 của chính lần chạy MT5; "
         "stress phí, Monte Carlo, Python = **MÔ PHỎNG**.", "",
         "## 1. Kiểm tra chặt trên lệnh MT5 thật", "",
         "| id | Symbol | TF | Năm | Lệnh | Lãi kép BC % | Lãi kép tái dựng % | Lãi kép stress % (MÔ PHỎNG) | DD BC % | DD equity tái dựng % | DD lệnh đóng % | DD stress % | MC DD equity p95 % (stress, MÔ PHỎNG) | WF 3 đoạn %/năm | Py/MT5 | Tầng |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    mt = kq["mt5"]
    for k in sorted(mt, key=lambda k: {"A": 0, "B": 1, "C": 2}.get(mt[k].get("xep", {}).get("tang"), 3)):
        m = mt[k]
        if m.get("loi"):
            L.append("| %s | %s | %s | | | | | | | | | | | %s | | CHƯA ĐO ĐƯỢC |" % (k, m.get("symbol"), m.get("tf"), m["loi"])); continue
        wf = " / ".join(_f(d["lai_kep_pct_nam"], 0) for d in m["walk_forward"])
        L.append("| %s | %s | %s | %.2f | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k, m["symbol"], m["tf"], m["so_nam"], m["so_lenh"], _f(m.get("lai_kep_bao_cao")), _f(m["lai_kep_pct_nam"]),
            _f(m["lai_kep_stress_pct_nam"]), _f(m.get("dd_bao_cao_pct")), _f(m["dd_equity_pct"]), _f(m["dd_dong_pct"]),
            _f(m["dd_equity_stress_pct"]), _f(m["monte_carlo"].get("equity", {}).get("dd_equity_p95")), wf, _f(m.get("py_mt5"), 2),
            m["xep"]["tang"]))
    L += ["", "Lí do chưa lên tầng (rút gọn):", ""]
    for k, m in mt.items():
        x = m.get("xep") or {}
        if x.get("tang") in ("B", "C"):
            L.append("- `%s` (%s): thiếu A: %s%s" % (k, x["tang"], "; ".join(x["thieu_A"][:4]),
                                                    ("" if x["tang"] == "B" else " — thiếu B: " + "; ".join(x["thieu_B"][:4]))))
    L += ["", "## 2. Python (MÔ PHỎNG): mặc định tác giả, khung, đa cặp, lưới + cao nguyên", "",
          "| id | Gốc %/năm | Gốc DD % | OOS 30% %/năm | Mặc định tác giả %/năm | Khung khác | Cặp khác không lỗ | Cao nguyên gốc | Tốt nhất (cao nguyên) | Phép thử | Giây |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, p in kq["python"].items():
        if p.get("loi"):
            L.append("| %s | %s |||||||||" % (k, p["loi"])); continue
        g, md = p["goc"], p["mac_dinh_tac_gia"]
        kh = ", ".join("%s %s/%s" % (a, _f(r.get("lai_pct_nam"), 0), _f(r.get("sut_giam_pct"), 0)) for a, r in p["khung"].items() if r is not g)
        tn = p["tot_nhat"][0] if p["tot_nhat"] else None
        tn_s = ("%s%%/năm, DD %s%%, OOS %s, CN %s" % (_f(tn["lai_pct_nam"]), _f(tn["sut_giam_pct"]), _f(tn["oos_lai_pct_nam"]), tn["cao_nguyen"])) if tn else "không có điểm qua chống quá khớp"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %s |" % (
            k, _f(g.get("lai_pct_nam")), _f(g.get("sut_giam_pct")), _f((g.get("oos") or {}).get("lai_pct_nam")),
            _f(md.get("lai_pct_nam")), kh, "—" if p["ti_le_cap_khac_khong_lo"] is None else "%d%% (%d cặp)" % (round(p["ti_le_cap_khac_khong_lo"] * 100), len(p["da_cap"])),
            _f(p["cao_nguyen_goc"], 2), tn_s, p["so_phep_thu"], _f(p["giay"], 0)))
    L += ["", "## 3. Ghép cùng cặp (MÔ PHỎNG)", "",
          "| Gốc | B | Phong cách B | Kiểu | %/năm | DD % | OOS %/năm | Lệnh | Gốc %/năm / DD % |", "|---|---|---|---|---|---|---|---|---|"]
    for g in kq["ghep_cung_cap"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
            g["goc"], g["b"], ",".join(g["phong_cach_b"] or []), g["kieu"], _f(g.get("lai_pct_nam")), _f(g.get("sut_giam_pct")),
            _f((g.get("oos") or {}).get("lai_pct_nam")), _f(g.get("so_lenh"), 0), _f(g["goc_lai"]), _f(g["goc_dd"])))
    L += ["", "## 4. Danh mục từ lệnh MT5 thật, DD trên equity tái dựng theo giờ", "",
          "| # | Hệ | Lãi kép %/năm | DD equity % | Tương quan ngày max | Kỳ |", "|---|---|---|---|---|---|"]
    for i, d in enumerate(kq["danh_muc"][:8], 1):
        L.append("| %d | %s | %s | %s | %s | %s → %s |" % (i, "<br>".join(d["he"]), _f(d["lai_kep_pct_nam"]), _f(d["dd_equity_pct"]),
                                                     _f(d["tuong_quan_ngay_max"], 2), d["tu"], d["den"]))
    L += ["", "## 5. Hàng chờ MT5 vòng 2", "", "Việc mới lần này: %d; tổng trong `reports/vong2/hang_cho_vong2.jsonl`: %d. "
          "Máy nhà chỉ lấy khi đặt `BRAIN_VONG2=1`." % (kq["so_viec_moi"], kq["so_viec_hang_cho"]), ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--ngan-sach", type=int, default=90)
    ap.add_argument("--khong-python", action="store_true")
    a = ap.parse_args(argv)
    chay(a.top, a.ngan_sach, not a.khong_python)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
