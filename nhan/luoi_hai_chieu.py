# -*- coding: utf-8 -*-
"""luoi_hai_chieu.py - EA LUOI / MARTINGALE HAI CHIEU / LUON VAO (HEDGE) KHONG CO TIN HIEU CHIEU (20/10/2026).

Van de: bo dich chi nhan TIN HIEU CHIEU (-1/0/1) va bo kiem dem so lan doi tin hieu -> EA luoi vo dieu kien (HelloSmart,
T17/T18Grid, cm_Martini, averaging_scalping, ...) ra KHONG_RA_SPEC_PY / IT_LENH du logic ro rang.

Bieu dien (truong "luoi" trong ban dich, the co tin_hieu {"kieu": "luoi", "luoi": {...}}):
    {"che_do": "luoi_hai_chieu" | "luon_vao" | "mot_chieu",
     "chieu": "hai" | "mua" | "ban",            # luoi_hai_chieu / luon_vao mac dinh "hai"
     "loc_python": "",                          # tuy chon: def tin_hieu(df) -> 1 cho ro MUA, -1 cho ro BAN, 2 ca hai, 0 khong
     "lot0": 0.01,                              # lot lenh dau (lot CHUAN cua tac gia, hop dong 100000)
     "buoc_diem": 300 | "buoc_pct": 0.003,      # khoang luoi / nhoi nguoc chieu
     "toi_da": 5,                               # so tang NHOI them (khong tinh lenh dau); 0 = khong nhoi
     "he_so_lot": 1.0,                          # lot tang k = lot0 x he_so^k (martingale > 1)
     "kieu_lot": "nhan" | "tuyen_tinh",         # tuyen_tinh: lot tang k = lot0 x (k+1) (EA LOT_TUYEN_TINH)
     "tp_diem" | "tp_pct" | "tp_tien": ...,     # chot RO tinh tu gia von binh quan (tien: USD tai lot0 cua tac gia)
     "hedge_khi_lo_pct": 0,                     # ro lo >= X % so du -> lenh khoa nguoc chieu (zone recovery gan dung)
     "cat_lo_tien" | "cat_lo_diem" | "cat_lo_pct": 0,   # cat ca ro (0 = khong SL); diem: SL lenh dau quy ra tien o lot0
     "nghi_gio": [13, 22]}                      # gio khong mo ro moi (tuy chon)
Ngu nghia (CUNG bo may quan tri `tai_khoan.chay_tk` va EA BRAIN_XuLiLenh VAO_CSV - mot ro moi chieu):
    o MOI nen (open nen k) phat lenh vao cho moi chieu duoc phep; bo may BO lenh neu da co ro cung chieu -> ro mo lai
    ngay sau khi chot. Lenh nhoi / TP ro / khoa / cat lo do bo may lam theo tham so tac gia (khong toi uu).
Gan dung (ghi ro trong the): tien cua tac gia quy ve gia theo lot0 x 100000 (TP ro bang tien doi thanh TP gia co dinh tu
gia von); EA mo nhieu cap moi nen (vd yzJohnWester) gom thanh mot ro moi chieu; martingale DAO CHIEU sau lenh lo chua
bieu dien duoc (bo may chua co lot theo ket qua lenh truoc).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HOP_DONG_TAC_GIA = 100000.0
CHE_DO = ("luoi_hai_chieu", "luon_vao", "mot_chieu")


def chuan_hoa(l: dict) -> tuple[dict, list[str]]:
    """-> (ban chuan hoa, loi[]). Khong nem loi."""
    loi = []
    if not isinstance(l, dict):
        return {}, ["luoi khong phai object"]
    x = dict(l)
    cd = str(x.get("che_do") or "luoi_hai_chieu")
    if cd not in CHE_DO:
        loi.append("che_do '%s' khong thuoc %s" % (cd, "/".join(CHE_DO)))
    x["che_do"] = cd
    ch = str(x.get("chieu") or ("hai" if cd != "mot_chieu" else "")).lower()
    ch = {"buy": "mua", "sell": "ban", "both": "hai", "1": "mua", "-1": "ban"}.get(ch, ch)
    if ch not in ("hai", "mua", "ban"):
        loi.append("chieu phai la hai/mua/ban")
    x["chieu"] = ch

    def so(k, md=0.0):
        try:
            return float(x.get(k) if x.get(k) not in (None, "") else md)
        except (TypeError, ValueError):
            loi.append("%s khong phai so" % k)
            return md
    x["lot0"] = so("lot0", 0.01)
    if x["lot0"] <= 0:
        loi.append("lot0 <= 0")
    x["toi_da"] = int(so("toi_da", 0))
    x["he_so_lot"] = so("he_so_lot", 1.0)
    x["kieu_lot"] = "tuyen_tinh" if str(x.get("kieu_lot") or "").lower() in ("tuyen_tinh", "linear", "cong") else "nhan"
    for k in ("buoc_diem", "buoc_pct", "tp_diem", "tp_pct", "tp_tien", "hedge_khi_lo_pct", "cat_lo_tien", "cat_lo_diem", "cat_lo_pct"):
        if k in x:
            x[k] = so(k)
    if x["toi_da"] > 0 and not (x.get("buoc_diem") or x.get("buoc_pct")):
        loi.append("co nhoi (toi_da > 0) nhung thieu buoc_diem / buoc_pct")
    if x["toi_da"] > 60:
        loi.append("toi_da > 60")
    if not (x.get("tp_diem") or x.get("tp_pct") or x.get("tp_tien")):
        loi.append("thieu TP ro (tp_diem / tp_pct / tp_tien)")
    if not isinstance(x.get("loc_python") or "", str):
        loi.append("loc_python phai la chuoi")
    x["loc_python"] = (x.get("loc_python") or "").strip()
    ng = x.get("nghi_gio") or []
    x["nghi_gio"] = [int(h) for h in ng if str(h).lstrip("-").isdigit() and 0 <= int(h) < 24] if isinstance(ng, list) else []
    return x, loi


def ql_tu_tac_gia(l: dict, gia_tc: float, point: float, hop_dong: float, qd: float, von: float) -> dict:
    """Tham so tac gia (diem / tien) -> dict ql cua ong_dan.quan_li_tu (phan cua gia, % von), CO DINH (khong toi uu).
    gia_tc: gia tham chieu (trung vi close); qd: USD cho 1 don vi gia x 1 don vi co so; hop_dong: cua bo may."""
    l, _ = chuan_hoa(l)
    g = max(float(gia_tc), 1e-12)
    buoc = l.get("buoc_pct") or ((l.get("buoc_diem") or 0.0) * point / g)
    if l.get("tp_pct"):
        tp = l["tp_pct"]
    elif l.get("tp_diem"):
        tp = l["tp_diem"] * point / g
    else:
        tp = l["tp_tien"] / (l["lot0"] * HOP_DONG_TAC_GIA * max(qd, 1e-12)) / g
    ty = hop_dong / HOP_DONG_TAC_GIA                      # tien tac gia (lot chuan) -> tien bo may (cung lot0)
    tien_cat = l.get("cat_lo_tien") or ((l.get("cat_lo_diem") or 0.0) * point * l["lot0"] * HOP_DONG_TAC_GIA * qd)
    cat = l.get("cat_lo_pct") or (100.0 * tien_cat * ty / max(von, 1e-9))
    return {"tp_pct": round(float(tp), 8), "dca_buoc_pct": round(float(buoc), 8) if l["toi_da"] > 0 else 0.003,
            "dca_toi_da": int(l["toi_da"]), "dca_he_so_lot": float(l["he_so_lot"]),
            "hedge_khi_lo_pct": float(l.get("hedge_khi_lo_pct") or 0.0), "cat_lo_pct": round(float(cat), 6),
            "lot_tren_1000": round(l["lot0"] * 1000.0 / max(von, 1e-9), 6), "luoi_tac_gia": True,
            "dca_lot_tuyen_tinh": l["kieu_lot"] == "tuyen_tinh"}


def cho_phep(l: dict, df: pd.DataFrame, s_loc: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """-> (cho_mua, cho_ban) bool theo nen (tai nen i: duoc mo ro o OPEN nen i+1). Chi dung du lieu den het nen i."""
    n = len(df)
    mua = np.full(n, l["chieu"] in ("hai", "mua"))
    ban = np.full(n, l["chieu"] in ("hai", "ban"))
    if s_loc is not None:
        s = np.asarray(s_loc, int)
        mua &= s > 0
        ban &= (s < 0) | (s == 2)
    if l.get("nghi_gio"):
        # nen i cho phep vao o open nen i+1 -> xet gio cua nen i+1 (gio da biet truoc, khong nhin truoc gia)
        gio = pd.DatetimeIndex(df.index).hour.to_numpy()
        gio_sau = np.r_[gio[1:], gio[-1:]]
        ok = ~np.isin(gio_sau, l["nghi_gio"])
        mua &= ok
        ban &= ok
    return mua, ban


def lenh_vao(df: pd.DataFrame, mua: np.ndarray, ban: np.ndarray, nguon: str, ma: str = "") -> list:
    """Nhu nguon_lenh.lenh_vao: cho phep o nen i -> LenhVao o OPEN nen i+1, moi chieu duoc phep mot lenh."""
    from nhan import nguon_lenh as NL
    o = df["open"].to_numpy(float)
    ev = []
    for i in np.nonzero(mua[:-1] | ban[:-1])[0]:
        k = int(i) + 1
        if mua[i]:
            ev.append(NL.LenhVao(nguon, k, float(o[k]), 1, ma))
        if ban[i]:
            ev.append(NL.LenhVao(nguon, k, float(o[k]), -1, ma))
    return ev


def rut_gon_csv(ev: list, kq_lenh: pd.DataFrame | None, du: int = 2) -> list:
    """CSV cho MT5: chi giu lenh vao o nen Python THAT mo ro (va `du` nen sau, chiu lech 1-2 nen khi EA chot ro tre)."""
    if kq_lenh is None or not len(kq_lenh):
        return ev
    goc = kq_lenh[~kq_lenh["khoa"].astype(bool)].groupby("ro").agg(mo=("mo", "min"), chieu=("chieu", "first"))
    giu = {(int(m) + d, int(c)) for m, c in zip(goc["mo"], goc["chieu"]) for d in range(du + 1)}
    return [e for e in ev if (int(e.chi_so), 1 if e.chieu > 0 else -1) in giu]
