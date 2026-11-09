# -*- coding: utf-8 -*-
"""v3_wf.py - VONG 3 (09/11/2026): P1 tai sinh CSV vao dai 2009-2026 + P2 walk-forward 12/3 rieng tung cap.

Thiet ke: /workspace/quy_trinh_v3/QUY_TRINH_VONG3_2026-11-09.md §2.4, §4 (P1/P2), Anh da duyet.
- Luat vao lay tu `tin_hieu` cua the trong data/ong_dan/tho_box.sqlite (cung duong `ong_dan.tin_hieu` + loc gio doi ngay
  nhu `ong_dan.chuan_bi`), tinh tren gia H1 2008-2023 (HistData, hd_dai) noi M5 2024-10/2026 (hd28), gio server NY+7.
- Moi quy: chon he so chu ky chi bao m (0,5..1,5; he khong co chu ky -> chi m=1) va k lot CHI tren 12 thang train;
  chi phat lenh cho 3 thang test. Khong holdout 2 nam, khong be tham so tu cap khac (moi he chi chay tren cap cua no).
- Quan li lenh (TP %, buoc DCA %, so tang, he so lot) CO DINH = bo .set cua viec V1/V2 tren may nha, vi EA chua co lich
  tham so (E1 chua lam): CSV chi mang duoc gio vao, chieu, lot (k). Bo quan li nay da duoc chon tren 2024-2026 -> doan OOS
  2024-2026 KHONG sach ve quan li; 2009-2023 sach. Ca hai duoc in rieng.
- Them so V3 da duyet: tran giu 30 ngay (H4 180 nen / H1 720 nen), InpMarginMin 300 %, spread >= p90 do (phi_xm_micro.json),
  swap XM do, don bay 1:500, von 10.000 USD, stop-out 20 %.
- Quy tac k (de xuat §2.4, Anh duyet): k lon nhat trong luoi 0,1..10 ma DD train <= 60 % va khong stop-out; m chon o k=0,1; train lo o k=0,1 -> k=0
  (quy do khong vao). Train < 20 ro -> giu bo cua quy truoc.
Moi so la MO PHONG Python (`nhan/tai_khoan.chay_tk`). CLI: python -m nhan.v3_wf [he ...]
"""
from __future__ import annotations

import copy
import dataclasses
import json
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import nguon_lenh as NL
from nhan import ong_dan as OD
from nhan import tai_khoan as TK
from nhan import gio_san as GS

GOC = Path(__file__).resolve().parent.parent
RA = GOC / "reports" / "v3"
FX = Path("/workspace/du_lieu_fx")
VON = 10000.0
DON_BAY = 500
DD_TRAIN_MAX = 60.0
RO_TRAIN_MIN = 20
LUOI_M = [0.5, 0.75, 1.0, 1.25, 1.5]
LUOI_K = [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
K_REF = LUOI_K[0]          # chon m o lot nho nhat (diem lai/DD gan nhu khong doi theo k khi chua cham stop-out)
GIU_NGAY = 30
MARGIN_MIN = 300.0
OOS_TU = "2009-01-01"
CHI_BAO_CHU_KY = {"sma", "ema", "wma", "rsi", "cci", "atr", "adx", "stochastic", "bollinger", "donchian", "macd", "momentum"}

DU_LIEU = {
    "CADJPY": [FX / "hd_dai/cadjpy_h1_2008_2023_ny7.csv", FX / "hd28/cadjpy_m5.csv"],
    "GBPCAD": [FX / "hd_dai/gbpcad_h1_2008_2023_ny7.csv", FX / "hd28/gbpcad_m5.csv"],
    "GBPNZD": [FX / "hd_dai/gbpnzd_h1_2008_2023_ny7.csv", FX / "hd28/gbpnzd_m5.csv"],
    "NZDUSD": [FX / "hd_dai/nzdusd_h1_2008_2023_ny7.csv", FX / "hd28/nzdusd_m5_histdata_ny7_den202610.csv"],
}

# he -> the, cap, khung, viec V1 (lay .set quan li), bien the (V2 mo phong duoc tren Python + CSV)
CAC_HE = {
    "skea61c": dict(the="sk_ea_61c21a2049", ma="CADJPY", khung="H4", viec="lot_skea61c21a2049_H4",
                    csv_cu="reports/phan_viec/viec_mt5/sk_ea_61c21a2049/od_skea61c21a2049_XM_CSV_vao.csv",
                    bien_the={"goc": {}}),
    "ghep_0bf2": dict(the="ghep_0bf2c31fbfc9dea0", ma="GBPCAD", khung="H4", viec="lot_ghep0bf2c31fbfc9dea0_H4",
                      csv_cu="reports/phan_viec/viec_mt5/ghep_0bf2c31fbfc9dea0/od_ghep0bf2c31fbfc9dea0_XM_CSV_vao.csv",
                      bien_the={"goc": {}}),
    "ghepe9b4": dict(the="ghep_e9b41c33d4deee54", ma="GBPNZD", khung="H4", viec="lot_ghepe9b41c33d4deee54_H4",
                     csv_cu="reports/phan_viec/viec_mt5/ghep_e9b41c33d4deee54/od_ghepe9b41c33d4deee54_XM_CSV_vao.csv",
                     bien_the={"goc": {}, "adxngang": {"adx_max": 25.0}, "catlo40": {"cat_lo_pct": 40.0}}),
    "ghep60ff": dict(the="ghep_60ff9350c26c63ee", ma="GBPCAD", khung="H1", viec="lot_ghep60ff9350c26c63ee_H1",
                     csv_cu="reports/phan_viec/viec_mt5/ghep_60ff9350c26c63ee/od_ghep60ff9350c26c63ee_XM_CSV_vao.csv",
                     bien_the={"goc": {}, "catlo40": {"cat_lo_pct": 40.0}, "adxngang": {"adx_max": 25.0}}),
    "2600ea39": dict(the="2600ea39abbd7b0f", ma="GBPNZD", khung="H1", viec="lot_2600ea39abbd7b0f_H1",
                     csv_cu="reports/phan_viec/viec_mt5/2600ea39abbd7b0f/od_2600ea39abbd7b0f_XM_CSV_vao.csv",
                     bien_the={"goc": {}}),
    "mql5344": dict(the="mql5_344ed0d8ab12c7f0", ma="NZDUSD", khung="H1", viec="lot_mql5344ed0d8ab12c7f0_H1",
                    csv_cu=None, bien_the={"goc": {}}),
}


def the(the_id: str) -> dict:
    c = sqlite3.connect(GOC / "data" / "ong_dan" / "tho_box.sqlite")
    return json.loads(c.execute("select json from the where id=?", (the_id,)).fetchone()[0])


def viec_v1(ten: str) -> dict:
    for d in ("da_test", "can_test"):
        p = GOC / "hang_doi" / d / (ten + ".json")
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(ten)


def ql_tu_set(ts: dict, von_viec: float) -> dict:
    """.set BRAIN_XuLiLenh (VAO_CSV, % gia) -> ql dict cua ong_dan (lot_tren_1000)."""
    nhoi = int(ts.get("InpNhoi", 0)) and float(ts.get("InpBuocPct", 0)) > 0
    return {"tp_pct": float(ts["InpTPPct"]) or None,
            "dca_buoc_pct": float(ts["InpBuocPct"]) if nhoi else None,
            "dca_toi_da": int(ts["InpMaxTang"]) - 1 if nhoi else 0,
            "dca_he_so_lot": float(ts["InpHeSoLot"]) if int(ts.get("InpKieuLot", 0)) == 2 else 1.0,
            "dca_lot_tuyen_tinh": int(ts.get("InpKieuLot", 0)) == 1,
            "hedge_khi_lo_pct": float(ts.get("InpHedgeKhiLoPct", 0)),
            "cat_lo_pct": float(ts.get("InpCatLoPct", 0)),
            "lot_tren_1000": float(ts["InpLot0"]) * 1000.0 / float(von_viec)}


def gia(ma: str, khung: str) -> pd.DataFrame:
    df = OD._doc_h1([str(x) for x in DU_LIEU[ma]])
    return NL.doi_khung(df, khung)


def nhan_chu_ky(th: dict, m: float) -> tuple[dict, int]:
    """Nhan moi `n` cua chi bao co chu ky voi m (khong dung do tre `tre`). -> (tin_hieu moi, so cho da nhan)."""
    th = copy.deepcopy(th)
    dem = [0]

    def di(x):
        if isinstance(x, dict):
            if x.get("chi_bao") in CHI_BAO_CHU_KY and isinstance(x.get("n"), (int, float)):
                x["n"] = max(2, int(round(x["n"] * m)))
                dem[0] += 1
            for v in x.values():
                di(v)
        elif isinstance(x, list):
            for v in x:
                di(v)
    di(th)
    return th, dem[0]


def adx_wilder(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    h, l, c = df["high"], df["low"], df["close"]
    up, dn = h.diff(), -l.diff()
    dmp = ((up > dn) & (up > 0)) * up.clip(lower=0)
    dmm = ((dn > up) & (dn > 0)) * dn.clip(lower=0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    a = 1.0 / n
    atr = tr.ewm(alpha=a, adjust=False).mean().replace(0, np.nan)
    dip = 100 * dmp.ewm(alpha=a, adjust=False).mean() / atr
    dim = 100 * dmm.ewm(alpha=a, adjust=False).mean() / atr
    dx = 100 * (dip - dim).abs() / (dip + dim).replace(0, np.nan)
    return dx.ewm(alpha=a, adjust=False).mean().to_numpy()


def su_kien(t: dict, df: pd.DataFrame, m: float, bt: dict) -> tuple[np.ndarray, np.ndarray]:
    """-> (j: chi so nen vao lenh (open), chieu). Nhu ong_dan.chuan_bi: tin hieu close nen i, vao open nen i+1, cam gio doi ngay."""
    th, _ = nhan_chu_ky(t["tin_hieu"], m)
    s = OD.tin_hieu({"tin_hieu": th, "id": t["id"]}, df, {}, "")
    tu, den = GS.cam_doi_ngay("XM")
    s = NL.ap_loc(s, cho_ca=NL.bo_loc_gio(df, den, tu))
    if bt.get("adx_max"):
        adx = adx_wilder(df, 14)
        s = NL.ap_loc(s, cho_ca=~(np.nan_to_num(adx, nan=1e9) >= bt["adx_max"]))
    s = np.asarray(s, int)
    i = np.nonzero(s[:-1] != 0)[0]
    return i + 1, s[i]


@dataclasses.dataclass
class Moi:
    df: pd.DataFrame
    hs: TK.HoSoPhi
    tk: TK.TaiKhoan
    ql: TK.QuanLi
    nguon: str
    ma: str


def chuan_bi_moi(he: str, bt_ten: str) -> tuple[Moi, dict, dict, dict]:
    cf = CAC_HE[he]
    t = the(cf["the"])
    v1 = viec_v1(cf["viec"])
    qld = ql_tu_set(v1["ts"], float(v1.get("von") or 1000))
    bt = cf["bien_the"][bt_ten]
    if bt.get("cat_lo_pct"):
        qld["cat_lo_pct"] = bt["cat_lo_pct"]
    df = gia(cf["ma"], cf["khung"])
    hs = TK.ho_so_phi(cf["ma"], "XM")
    _px = json.loads((GOC / "config" / "phi_xm_micro.json").read_text(encoding="utf-8"))
    if cf["ma"] in _px:
        p90 = _px[cf["ma"]]["spread_p90_gia"]
    else:                               # vd NZDUSD: khong co trong phi_xm_micro -> dung load_phi cua cong phi (fallback ghi nhan cua no)
        sys.path.insert(0, str(GOC / "reports" / "vong3"))
        import loc_phi_nhanh as LP
        p90 = LP.load_phi(cf["ma"]).spread_p90_gia
    hs = dataclasses.replace(hs, spread_gio=[max(float(x), float(p90)) for x in hs.spread_gio],
                             nhan=hs.nhan + " | spread >= p90 %.5f" % p90)
    tk = OD.don_bay_viec(TK.ho_so_tai_khoan("XM_MICRO_TAM", VON), don_bay=DON_BAY)
    ql = OD.quan_li_tu(qld, VON)
    ql.go_cheo = False
    ql.mot_ro_moi_chieu = True
    ql.giu_toi_da_nen = {"H4": 180, "H1": 720}[cf["khung"]]       # 30 ngay giao dich (thiet ke §2.3)
    ql.margin_min_pct = MARGIN_MIN
    ql.gio_cam = (int(v1["ts"].get("InpGioCamTu", 23)), int(v1["ts"].get("InpGioCamDen", 2)))   # nhu .set EA
    return Moi(df, hs, tk, ql, cf["the"], cf["ma"]), t, qld, v1


def lot_k(mo: Moi, k: float) -> float:
    """lot dau cho k: lam tron so NGUYEN lot micro (>= 1) de CSV '#' (0,01 lot chuan = 1 micro) khop dung."""
    return float(max(1, int(round(mo.ql.lot0 * k))))


def mo_phong(mo: Moi, a: int, b: int, j: np.ndarray, ch: np.ndarray, lot: np.ndarray, ghi_lenh=False, ghi_von=True) -> dict:
    sel = (j >= a) & (j < b)
    o = mo.df["open"].to_numpy(float)
    ev = [TK.LenhVao(mo.nguon, int(x - a), float(o[x]), int(c), "", float(l)) for x, c, l in zip(j[sel], ch[sel], lot[sel])]
    return TK.chay_tk({"": mo.df.iloc[a:b]}, ev, mo.ql, mo.tk, {"": mo.hs}, ghi_von=ghi_von, ghi_lenh=ghi_lenh)


def cac_quy(df: pd.DataFrame, tu: str = OOS_TU) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    q0 = pd.Timestamp(tu)
    het = df.index[-1]
    ra = []
    while q0 <= het:
        q1 = q0 + pd.DateOffset(months=3)
        ra.append((q0, q1))
        q0 = q1
    return ra


def diem_train(r: dict) -> float:
    return r["lai_pct_nam"] / max(r["sut_giam_pct"], 10.0)


def walk_forward(he: str, bt_ten: str = "goc", in_ra=print) -> dict:
    t0 = time.time()
    mo, t, qld, v1 = chuan_bi_moi(he, bt_ten)
    df, idx = mo.df, mo.df.index
    _, so_ck = nhan_chu_ky(t["tin_hieu"], 1.0)
    luoi_m = LUOI_M if so_ck else [1.0]
    bt = CAC_HE[he]["bien_the"][bt_ten]
    sk = {m: su_kien(t, df, m, bt) for m in luoi_m}
    lich, prev = [], None
    J, C, L = [], [], []
    for q0, q1 in cac_quy(df):
        a = int(idx.searchsorted(q0 - pd.DateOffset(months=12)))
        b = int(idx.searchsorted(q0))
        c = int(idx.searchsorted(q1))
        dong = {"tu": str(q0.date()), "den": str(q1.date()), "train_tu": str((q0 - pd.DateOffset(months=12)).date())}
        if b >= len(idx) or c <= b:
            break
        if idx[a] > q0 - pd.DateOffset(months=12) + pd.Timedelta(days=10) or b - a < 100:
            dong.update(m=None, k=0.0, ly_do="thieu_du_lieu_train")
            lich.append(dong)
            continue
        tot = None
        thu_m = {}
        for m in luoi_m:
            j, ch = sk[m]
            r = mo_phong(mo, a, b, j, ch, np.full(len(j), lot_k(mo, K_REF)), ghi_von=False)
            thu_m[m] = {"lai": r["lai_pct_nam"], "dd": r["sut_giam_pct"], "ro": r["so_ro"], "so": r["so_stop_out"]}
            if r["so_ro"] >= RO_TRAIN_MIN and not r["chay"] and r["so_stop_out"] == 0:
                if tot is None or diem_train(r) > diem_train(tot[1]):
                    tot = (m, r)
        if tot is None:
            if prev is None:
                dong.update(m=None, k=0.0, ly_do="train_<20_ro_va_chua_co_bo_truoc", thu_m=thu_m)
                lich.append(dong)
                continue
            m, k = prev
            dong.update(m=m, k=k, ly_do="train_<20_ro_giu_bo_quy_truoc", thu_m=thu_m)
        else:
            m, r1 = tot
            if r1["lai_pct_nam"] <= 0:
                k, ly = 0.0, "train_lo_o_k_ref_khong_vao"
            else:
                k, ly = 0.0, "k_lon_nhat_dd_train_<=60"
                j, ch = sk[m]
                for kk in LUOI_K:
                    rk = mo_phong(mo, a, b, j, ch, np.full(len(j), lot_k(mo, kk)), ghi_von=False)
                    if rk["sut_giam_pct"] <= DD_TRAIN_MAX and rk["so_stop_out"] == 0 and not rk["chay"]:
                        k = kk
                        dong.setdefault("train_k", {})[kk] = [rk["lai_pct_nam"], rk["sut_giam_pct"]]
                    else:
                        dong.setdefault("train_k", {})[kk] = [rk["lai_pct_nam"], rk["sut_giam_pct"], "vuot"]
                        break
            dong.update(m=m, k=k, ly_do=ly, train_lai_kref=r1["lai_pct_nam"], train_dd_kref=r1["sut_giam_pct"],
                        train_ro=r1["so_ro"], thu_m=thu_m)
            prev = (m, k)
        j, ch = sk[m]
        sel = (j >= b) & (j < c)
        if k > 0:
            J.append(j[sel]); C.append(ch[sel]); L.append(np.full(int(sel.sum()), lot_k(mo, k)))
        dong["so_lenh_csv"] = int(sel.sum()) if k > 0 else 0
        lich.append(dong)
        in_ra("  %s %s q%s m=%s k=%s csv=%d (%s)" % (he, bt_ten, dong["tu"], m, k, dong["so_lenh_csv"], dong["ly_do"]))
    J = np.concatenate(J) if J else np.zeros(0, int)
    C = np.concatenate(C) if C else np.zeros(0, int)
    L = np.concatenate(L) if L else np.zeros(0)
    a0 = int(idx.searchsorted(pd.Timestamp(OOS_TU)))
    kq = mo_phong(mo, a0, len(idx), J, C, L, ghi_lenh=True)
    # NHAN (khong phai cong): cung lich m, nhung k CO DINH = K_REF moi quy (ke ca quy k=0) -> loi the vao + quan li khi khong nang lot
    Jn, Cn = [], []
    for dong in lich:
        if dong.get("m") is None:
            continue
        j, ch = sk[dong["m"]]
        b, c = int(idx.searchsorted(pd.Timestamp(dong["tu"]))), int(idx.searchsorted(pd.Timestamp(dong["den"])))
        sel = (j >= b) & (j < c)
        Jn.append(j[sel]); Cn.append(ch[sel])
    Jn = np.concatenate(Jn) if Jn else np.zeros(0, int)
    Cn = np.concatenate(Cn) if Cn else np.zeros(0, int)
    kn = mo_phong(mo, a0, len(idx), Jn, Cn, np.full(len(Jn), lot_k(mo, K_REF)))
    return {"he": he, "bien_the": bt_ten, "mo": mo, "the": t, "qld": qld, "v1": v1, "lich": lich, "J": J, "C": C, "L": L,
            "a0": a0, "kq": kq, "kq_k_co_dinh": kn, "giay": round(time.time() - t0, 1), "luoi_m": luoi_m}


# ------------------------------------------------------------------ cham, xuat CSV / lich / .set / .ini
def _cagr(v0: float, v1: float, nam: float) -> float:
    return -100.0 if v1 <= 0 or v0 <= 0 else ((v1 / v0) ** (1.0 / max(nam, 1e-9)) - 1.0) * 100.0


def cham_doan(kq: dict, tu: str, den: str | None) -> dict:
    idx = pd.DatetimeIndex(kq["chi_muc"])
    ec, ex = np.asarray(kq["duong_von"], float), np.asarray(kq["von_xau"], float)
    a = int(idx.searchsorted(pd.Timestamp(tu)))
    b = int(idx.searchsorted(pd.Timestamp(den))) if den else len(idx)
    if b - a < 2:
        return {}
    v0 = ec[a - 1] if a > 0 else VON
    nam = (idx[b - 1] - (idx[a - 1] if a > 0 else idx[0])).days / 365.25
    dinh = np.maximum.accumulate(np.maximum(np.concatenate([[v0], ec[a:b]]), 1e-9))[1:]
    dd = float(np.max((dinh - ex[a:b]) / dinh)) * 100.0
    return {"tu": str(idx[a].date()), "den": str(idx[b - 1].date()), "nam": round(nam, 2), "von_dau": round(float(v0), 2),
            "von_cuoi": round(float(ec[b - 1]), 2), "cagr_pct": round(_cagr(v0, ec[b - 1], nam), 2), "dd_pct": round(min(dd, 100.0), 2)}


def lai_theo_nam(kq: dict) -> dict:
    idx = pd.DatetimeIndex(kq["chi_muc"])
    ec = pd.Series(np.asarray(kq["duong_von"], float), index=idx)
    cuoi = ec.groupby(idx.year).last()
    dau = cuoi.shift(1).fillna(VON)
    return {int(y): round(float((cuoi[y] / dau[y] - 1) * 100.0), 2) if dau[y] > 0 else None for y in cuoi.index}


def mua_giu(mo: Moi, a0: int) -> dict:
    """Mua & giu 1x (danh nghia = von) tu dau OOS den het, swap MUA XM do moi dem (x3 thu Tu), quy doi nhu engine."""
    df = mo.df.iloc[a0:]
    hs = mo.hs
    p0 = float(df["open"].iloc[0])
    don_vi = VON / (p0 * hs.qd(p0))
    c = df["close"].to_numpy(float)
    dem = TK._dem_qua_dem(df.index, hs.ngay_x3)
    sw = np.cumsum(hs.swap_mua_diem * hs.point * don_vi * np.array([hs.qd(x) for x in c]) * dem)
    eq = VON + don_vi * (c - p0) * np.array([hs.qd(x) for x in c]) + sw
    nam = (df.index[-1] - df.index[0]).days / 365.25
    dinh = np.maximum.accumulate(np.maximum(eq, 1e-9))
    gia_thuan = VON + don_vi * (c[-1] - p0) * hs.qd(c[-1])
    return {"cagr_pct": round(_cagr(VON, eq[-1], nam), 2), "cagr_chua_swap_pct": round(_cagr(VON, gia_thuan, nam), 2),
            "dd_pct": round(float(np.max((dinh - eq) / dinh)) * 100, 2), "tong_swap_usd": round(float(sw[-1]), 2),
            "nam": round(nam, 2), "gia_dau": p0, "gia_cuoi": float(c[-1])}


def doi_chieu_csv_cu(he: str, r: dict) -> dict | None:
    """P1: CSV moi (m=1, khong WF) vs CSV cu 2024-2026 cung luat: ti le timestamp trung (can >= 95 %)."""
    cu = CAC_HE[he].get("csv_cu")
    if not cu or not (GOC / cu).exists():
        return None
    b = pd.read_csv(GOC / cu)
    tcu = pd.to_datetime(b["thoi_gian"], format="%Y.%m.%d %H:%M:%S")
    mo, t = r["mo"], r["the"]
    j, ch = su_kien(t, mo.df, 1.0, CAC_HE[he]["bien_the"][r["bien_the"]] if r["bien_the"] == "goc" else {})
    tm = pd.DatetimeIndex(mo.df.index[j])
    lo, hi = tcu.min() + pd.Timedelta(days=30), tcu.max()
    scu = set(tcu[(tcu >= lo) & (tcu <= hi)])
    smoi = set(tm[(tm >= lo) & (tm <= hi)])
    if not scu:
        return None
    return {"csv_cu": cu, "tu": str(lo.date()), "den": str(hi.date()), "so_cu": len(scu), "so_moi": len(smoi),
            "trung_pct_cua_cu": round(100.0 * len(scu & smoi) / len(scu), 2),
            "trung_pct_cua_moi": round(100.0 * len(scu & smoi) / max(len(smoi), 1), 2),
            "mua_pct_moi_toan_ky": round(100.0 * float((ch > 0).mean()), 2) if len(ch) else None}


def ghi_lenh_mt5(r: dict, tep: Path) -> int:
    """Lenh OOS Python -> dinh dang _lenh_mt5.csv cua EA (';'), position = ID RO (gop tang DCA) de cong phi danh gia theo ro."""
    L = r["kq"]["lenh"]
    idx = r["mo"].df.index[r["a0"]:]
    dong = ["thoi_gian;deal;position;vao_ra;chieu;khoi_luong;gia;loi;swap;hoa_hong;phu"]
    n = 0
    for x in L.itertuples():
        if x.dong is None or pd.isna(x.dong):
            continue
        sw = float(getattr(x, "swap", 0.0) or 0.0)
        dong.append("%s;%d;%d;in;%d;%.2f;%.6f;0;0;0;py" % (idx[int(x.mo)].strftime("%Y.%m.%d %H:%M:%S"), 2 * n, x.ro, x.chieu, x.lot, x.gia_mo))
        dong.append("%s;%d;%d;out;%d;%.2f;%.6f;%.4f;%.4f;0;py" % (idx[int(x.dong)].strftime("%Y.%m.%d %H:%M:%S"), 2 * n + 1, x.ro,
                                                                -x.chieu, x.lot, x.gia_dong, float(x.lai_tien) - sw, sw))
        n += 1
    tep.write_text("\n".join(dong) + "\n", encoding="ascii")
    return n


def cong_phi(r: dict, tep_lenh: Path, oos: dict) -> dict:
    sys.path.insert(0, str(GOC / "reports" / "vong3"))
    import loc_phi_nhanh as LP          # cung logic /workspace/quy_trinh_v3/loc_phi_nhanh.py (ban sao trong repo)
    return LP.danh_gia_tu_lenh(tep_lenh, r["mo"].ma, von=VON, cagr_pct=oos.get("cagr_pct"), dd_pct=oos.get("dd_pct"),
                               nhan="%s_%s" % (r["he"], r["bien_the"]))


def bang_csv(r: dict, ma_san: str, chia: float = 1.0) -> pd.DataFrame:
    mo = r["mo"]
    o = np.argsort(r["J"], kind="stable")
    J, C, L = r["J"][o], r["C"][o], r["L"][o]
    return pd.DataFrame({"thoi_gian": mo.df.index[J].strftime("%Y.%m.%d %H:%M:%S"), "ma": ma_san,
                         "chieu": [1 if c > 0 else -1 for c in C], "gia": np.round(mo.df["open"].to_numpy()[J], 6),
                         "nguon": mo.nguon, "lot": [("%.4f" % (x / chia)).rstrip("0").rstrip(".") for x in L]})


def ts_v3(r: dict, ten_csv: str) -> dict:
    """.set V3: tu .set viec V1 (quan li co dinh) + tran giu, MarginMin 300, ADX loc trong CSV (EA tat), lot tu CSV."""
    ts = dict(r["v1"]["ts"])
    cf = CAC_HE[r["he"]]
    ts.update({"InpFileCsv": ten_csv, "InpCsvChung": "true", "InpCsvMa": "", "InpVao": 4,
               "InpGiuToiDaNen": r["mo"].ql.giu_toi_da_nen, "InpMarginMin": MARGIN_MIN, "InpAdxMax": 0.0, "InpAdxMin": 0.0,
               "InpCatLoPct": float(r["mo"].ql.cat_lo_pct or 0.0), "InpLot0": 0.01, "InpLogChung": "false",
               "InpTF": {"H4": 16388, "H1": 16385}[cf["khung"]]})
    return ts


def ini(ten: str, ma: str, khung: str, tu: str, den: str) -> str:
    return ("[Tester]\nExpert=BRAIN\\BRAIN_XuLiLenh.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=4\nExecutionMode=0\n"
            "Optimization=0\nOptimizationCriterion=0\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=%d\nCurrency=USD\n"
            "Leverage=1:%d\nReport=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n") % (ten, ma, khung, tu, den, int(VON), DON_BAY, ten)


def chay_va_ghi(he: str, bt: str = "goc", in_ra=print) -> dict:
    r = walk_forward(he, bt, in_ra=lambda s: None)
    mo, kq, cf = r["mo"], r["kq"], CAC_HE[he]
    d = RA / he
    d.mkdir(parents=True, exist_ok=True)
    ten = "v3a_%s_%s_%s" % (he, bt, cf["khung"])
    het = str(mo.df.index[-1].date())
    oos = {"toan_ky": cham_doan(kq, OOS_TU, None), "2009_2023": cham_doan(kq, OOS_TU, "2024-01-01"),
           "2024_2026": cham_doan(kq, "2024-01-01", None)}
    a24 = int(mo.df.index.searchsorted(pd.Timestamp("2024-01-01")))
    kb = mo_phong(mo, a24, len(mo.df), r["J"], r["C"], r["L"])            # = luot B MT5: von moi 10.000 tu 2024-01
    oos["luot_B_von_moi_2024"] = dict(cham_doan(kb, "2024-01-01", None), chay=bool(kb["chay"]), so_stop_out=int(kb["so_stop_out"]),
                                      so_ro=int(kb["so_ro"]))
    kn = r["kq_k_co_dinh"]
    oos["nhan_k_co_dinh_%s" % K_REF] = dict(cham_doan(kn, OOS_TU, None), chay=bool(kn["chay"]), so_stop_out=int(kn["so_stop_out"]),
                                             so_ro=int(kn["so_ro"]), lot0_micro=lot_k(mo, K_REF), nhan="NHÃN, không phải cổng")
    nk = kq["nhat_ky"]
    ngay_chay = None
    if kq["chay"] or kq["so_stop_out"]:
        so = nk[nk["boi"] == "stop_out"] if len(nk) else nk
        if len(so):
            ngay_chay = str(pd.DatetimeIndex(kq["chi_muc"])[int(so["dong"].iloc[0])].date())
    tep_lenh = d / (ten + "_py_lenh_mt5.csv")
    n_lenh = ghi_lenh_mt5(r, tep_lenh)
    gate = cong_phi(r, tep_lenh, oos["toan_ky"]) if n_lenh else {"ket_luan": "CHUA_DO", "ly_do": "0 lenh OOS"}
    bh = mua_giu(mo, r["a0"])
    mua_pct = round(100.0 * float((r["C"] > 0).mean()), 2) if len(r["C"]) else None
    # CSV: ban micro (tho may nha, ma *micro, lot micro; tho tu doi sang '#' va chia 100) + ban '#' (chay tay)
    b_micro = bang_csv(r, cf["ma"] + "micro")
    b_hash = bang_csv(r, cf["ma"] + "#", chia=100.0)
    OD.ghi_csv_vao(b_micro, d / (ten + "_vao.csv"))
    OD.ghi_csv_vao(b_hash, d / (ten + "_vao_hash.csv"))
    for luot, tu in (("A", "2009.01.01"), ("B", "2024.01.01")):
        tn = ten.replace("v3a_", "v3%s_" % luot.lower())
        ts = ts_v3(r, ten + "_vao_hash.csv")
        (d / (tn + ".set")).write_text("\n".join("%s=%s" % kv for kv in sorted(ts.items())) + "\n", encoding="ascii")
        (d / (tn + ".ini")).write_text(ini(tn, cf["ma"] + "#", cf["khung"], tu, "2026.10.10"), encoding="ascii")
    # viec cho tho (chua dua vao hang_doi/can_test - parent quyet)
    for luot, tu in (("a", "2009.01.01"), ("b", "2024.01.01")):
        v = {"id": "v3%s_%s_%s_%s" % (luot, he, bt, cf["khung"]), "loai": "mt5_backtest", "uu_tien": 95, "che_do": "ong_dan_csv",
             "ea_file": "BRAIN_XuLiLenh", "ma": cf["ma"] + "micro", "tf": cf["khung"], "tu": tu, "den": "2026.10.10", "model": 4,
             "von": int(VON), "tien": "USD", "don_bay": DON_BAY, "ts": ts_v3(r, ten + "_vao.csv"), "tham_so_lot": None,
             "csv_vao": "reports/v3/%s/%s_vao.csv" % (he, ten), "he_so_lot": [1.0], "lich_wf": "reports/v3/%s/%s_lich_wf.json" % (he, ten),
             "cua_so": "OOS", "lan": "co_ma_nguon", "nguon": cf["the"],
             "ghi_chu": "V3 luot %s: CSV WF 12/3 (k trong cot lot, chon tren train); KHONG chon k tren cua so do" % luot.upper()}
        (d / (v["id"] + "_viec.json")).write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    dc = doi_chieu_csv_cu(he, r) if bt == "goc" else None
    tom = {"he": he, "bien_the": bt, "the": cf["the"], "ma": cf["ma"], "khung": cf["khung"], "du_lieu_den": het,
           "ql_co_dinh": r["qld"], "giu_toi_da_nen": mo.ql.giu_toi_da_nen, "margin_min_pct": MARGIN_MIN,
           "luoi_m": r["luoi_m"], "luoi_k": LUOI_K, "k_ref": K_REF, "lot0_micro_k1": mo.ql.lot0,
           "oos": oos, "lai_theo_nam": lai_theo_nam(kq),
           "chay": bool(kq["chay"]), "so_stop_out": int(kq["so_stop_out"]), "ngay_stop_out_dau": ngay_chay,
           "so_ro": int(kq["so_ro"]), "so_lenh": int(kq["so_lenh"]), "so_tp": int(kq["so_tp"]), "so_het_gio": int(kq["so_het_gio"]),
           "so_cat_lo": int(kq["so_cat_lo"]), "ro_mo_max": int(kq["ro_mo_max"]), "lot_mo_max_micro": float(kq["lot_mo_max"]),
           "giu_max_ngay": round(kq["ket_nen_max"] * NL.KHUNG_PHUT[cf["khung"]] / 1440.0, 1),
           "phi_usd": kq["phi"], "so_dong_csv": len(b_micro), "mua_pct_csv": mua_pct,
           "quy": {"tong": len(r["lich"]), "co_vao": sum(1 for x in r["lich"] if x.get("k", 0) > 0),
                   "k0": sum(1 for x in r["lich"] if not x.get("k"))},
           "mua_giu_1x": bh, "cong_phi": gate, "doi_chieu_csv_cu": dc, "giay": r["giay"]}
    ok = (tom["oos"]["toan_ky"].get("dd_pct", 100) < 80 and tom["oos"]["toan_ky"].get("cagr_pct", -100) > 10
          and not tom["chay"] and tom["so_stop_out"] == 0)
    can_bh = mua_pct is not None and mua_pct >= 95.0
    tom["can_so_mua_giu"] = can_bh
    tom["thang_mua_giu"] = (tom["oos"]["toan_ky"].get("cagr_pct", -100) > bh["cagr_pct"]) if can_bh else None
    b = tom["oos"]["luot_B_von_moi_2024"]
    tom["luot_B_dat"] = bool(not b.get("chay", True) and b.get("dd_pct", 100) < 80)   # thiet ke §4: Luot B khong chay, DD < 80
    tom["dat_python"] = bool(ok and tom["luot_B_dat"] and (not can_bh or tom["thang_mua_giu"]) and gate.get("ket_luan") == "PASS")
    tom["gui_mt5"] = tom["dat_python"]
    (d / (ten + "_lich_wf.json")).write_text(json.dumps({"he": he, "bien_the": bt, "quy_tac": __doc__.split("Moi so")[0].strip(),
                                                          "lich": r["lich"]}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (d / (ten + "_ket_qua_py.json")).write_text(json.dumps(tom, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    in_ra("%s %s: OOS CAGR %s DD %s chay=%s stop_out=%s | 09-23 %s | B(2024 von moi) %s/%s | B&H %s | phi %s | dat=%s (%.0fs)" % (
        he, bt, oos["toan_ky"].get("cagr_pct"), oos["toan_ky"].get("dd_pct"), tom["chay"], tom["so_stop_out"],
        oos["2009_2023"].get("cagr_pct"), oos["luot_B_von_moi_2024"].get("cagr_pct"), oos["luot_B_von_moi_2024"].get("dd_pct"), bh["cagr_pct"], gate.get("ket_luan"), tom["dat_python"], r["giay"]))
    return tom


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    ds = []
    for he in (argv or list(CAC_HE)):
        for bt in CAC_HE[he]["bien_the"]:
            ds.append(chay_va_ghi(he, bt))
    tong = [{k: x[k] for k in ("he", "bien_the", "ma", "khung", "oos", "chay", "so_stop_out", "mua_giu_1x", "thang_mua_giu",
                               "dat_python", "gui_mt5")} | {"cong_phi": x["cong_phi"].get("ket_luan"), "ly_do_phi": x["cong_phi"].get("ly_do")}
            for x in ds]
    (RA / "V3_CSV_TONG_HOP_py.json").write_text(json.dumps(tong, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    return ds


if __name__ == "__main__":
    main()
