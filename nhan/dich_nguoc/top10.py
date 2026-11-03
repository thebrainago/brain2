# -*- coding: utf-8 -*-
"""Dịch ngược hàng loạt CSV tín hiệu MQL5 (data/cong_khai/csv/<id>.history.csv) -> JSON số đo.
    python -m nhan.dich_nguoc.top10 --ra data/dich_nguoc/top10.json
Giá H1 lấy từ /workspace/du_lieu_fx (ngoài repo, HistData/Dukascopy BID, giờ server NY+7)."""
from __future__ import annotations
import argparse, glob, json, re
from pathlib import Path
import numpy as np
import pandas as pd
from . import doc_lich_su as DL, phan_tich as PT, dac_trung as DT

FX = "/workspace/du_lieu_fx/"
GIA = {"EURUSD": FX + "eurusd_h1_tu_histdata_m1_server.csv", "GBPUSD": FX + "gbpusd_h1_duka_ba_2024_2026.csv",
       "AUDUSD": FX + "audusd_h1_duka_ba_2024_2026.csv", "USDJPY": FX + "usdjpy_h1_duka_ba_2024_2026.csv",
       "XAUUSD": FX + "xauusd_h1_tu_histdata_m5_ny7.csv", "AUDCAD": FX + "audcad_h1_tu_histdata_m5_ny7.csv",
       "EURGBP": FX + "eurgbp_h1_tu_histdata_m5_ny7.csv"}


def goc(sym: str) -> str:
    s = sym.upper()
    if s.startswith("GOLD"): return "XAUUSD"
    return s[:6] if re.match(r"^[A-Z]{6}", s) else s


def von_va_loi_suat(df: pd.DataFrame, von: pd.DataFrame) -> dict:
    """Số dư ĐÓNG lệnh (không có equity nổi) + dòng tiền -> TWR, CAGR, DD trên chỉ số TWR theo ngày."""
    lai = df.dropna(subset=["dong_luc"]).groupby(df["dong_luc"].dt.normalize())["loi_nhuan"].sum()
    dong = von.groupby(von["luc"].dt.normalize())["so_tien"].sum()
    nap = float(von.loc[von.so_tien > 0, "so_tien"].sum()); rut = float(-von.loc[von.so_tien < 0, "so_tien"].sum())
    ngay = lai.index.union(dong.index).sort_values()
    lai = lai.reindex(ngay, fill_value=0.0); dong = dong.reindex(ngay, fill_value=0.0)
    b = 0.0; chi_so = [1.0]; ok = True
    for d in ngay:
        truoc = b + dong[d]            # dòng tiền đầu ngày
        if truoc <= 0 and lai[d] != 0: ok = False
        r = lai[d] / truoc if truoc > 0 else 0.0
        chi_so.append(chi_so[-1] * (1 + r)); b = truoc + lai[d]
    ci = np.array(chi_so[1:]); nam = max((ngay[-1] - ngay[0]).days, 1) / 365.25
    dd = float(np.max(1 - ci / np.maximum.accumulate(ci)))
    cagr = float(ci[-1] ** (1 / nam) - 1) if ci[-1] > 0 else -1.0
    return {"nap": round(nap, 2), "rut": round(rut, 2), "lai_rong_dong_lenh": round(float(df.loi_nhuan.sum()), 2),
            "so_du_cuoi_uoc": round(b, 2), "so_nam": round(nam, 2), "twr_tong": round(float(ci[-1] - 1), 4),
            "cagr_twr": round(cagr, 4), "dd_max_so_du_dong": round(dd, 4), "dong_tien_hop_le": ok,
            "lai_tren_nap": round(float(df.loi_nhuan.sum()) / nap, 3) if nap > 0 else None}


def lenh_cho(path: str) -> dict:
    s = open(path, encoding="utf-8", errors="replace").read()
    return {"stop": len(re.findall(r";(Buy|Sell) Stop;", s)), "limit": len(re.findall(r";(Buy|Sell) Limit;", s))}


def phien(df) -> dict:
    h = df["mo_luc"].dt.hour
    return {"a_0_8": round(float((h < 9).mean()), 3), "au_9_14": round(float(((h >= 9) & (h < 15)).mean()), 3),
            "my_15_23": round(float((h >= 15).mean()), 3)}


def phan_loai(tq, cho, sltp) -> str:
    l = tq["lot"]; t = []
    if cho["stop"] > 0.3 * tq["so_lenh"]: t.append("breakout lệnh chờ STOP")
    if cho["limit"] > 0.3 * tq["so_lenh"]: t.append("lệnh chờ LIMIT (lưới/đảo chiều)")
    if l["ty_le_ro_nhieu_lenh"] > 0.15:
        hs = l["he_so_lot_trung_vi"] or 1
        t.append("martingale" if hs > 1.05 else ("lưới/DCA lot đều" if abs(hs - 1) <= 0.05 else "lưới lot giảm"))
    else:
        t.append("lệnh đơn lẻ (không lưới đáng kể)")
    if tq["hedge"]["co_hedge"]: t.append("có hedge")
    if sltp.get("khong_co_cot_sltp"): t.append("SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal không có cột S/L, T/P)")
    else: t.append("có SL" if sltp["sl_ty_le_co"] > 0.5 else "không SL cứng")
    return ", ".join(t)


def mot(path: str) -> dict:
    sid = Path(path).name.split(".")[0]
    df = DL.doc(path); von = DL.doc_von(path)
    df["symbol"] = df["symbol"].map(goc)
    tq = PT.tong_quat(df); cho = lenh_cho(path)
    if df["sl"].isna().all() and df["tp"].isna().all(): tq["tp_sl"]["khong_co_cot_sltp"] = True
    kq = {"id": sid, "url": f"https://www.mql5.com/en/signals/{sid}", "tong_quat": tq, "lenh_cho": cho,
          "phien_gio_server": phien(df), "von": von_va_loi_suat(df, von)}
    kq["phong_cach"] = phan_loai(tq, cho, tq["tp_sl"])
    sym = df["symbol"].value_counts().index[0]; kq["symbol_chinh"] = sym
    if sym in GIA and Path(GIA[sym]).exists():
        p = PT.pip(sym); g = DT.doc_gia(GIA[sym]); f = DT.chi_bao(g, p)
        dau = PT.ro(df).sort_values("mo_luc").groupby("ro").head(1)
        dau = dau[(dau.symbol == sym) & (dau.mo_luc >= g.index[60]) & (dau.mo_luc <= g.index[-1])]
        kq["gia_dung"] = f"{GIA[sym]} ({g.index[0]} -> {g.index[-1]})"
        if len(dau) >= 30:
            ff = f.loc[g.index[60]:]
            kq["phan_biet"] = DT.phan_biet(ff, dau["mo_luc"])
            kq["phan_biet_bo_gio"] = DT.phan_biet(ff, dau["mo_luc"], bo_qua_gio=True)
            # chiều: buy vs sell tại lệnh đầu rổ (logistic, không giờ)
            X = DT.tai_thoi_diem(f, dau["mo_luc"]); y = (dau["chieu"].values == "buy").astype(int)
            m = X.notna().all(axis=1).values
            if m.sum() > 40 and 0.1 < y[m].mean() < 0.9:
                from sklearn.linear_model import LogisticRegression; from sklearn.model_selection import cross_val_score
                Xs = X[m][[c for c in DT.TEN if c not in ("gio", "thu")]]; Xs = (Xs - Xs.mean()) / Xs.std()
                lg = LogisticRegression(max_iter=2000, class_weight="balanced")
                kq["auc_chieu_cv5"] = round(float(np.mean(cross_val_score(lg, Xs, y[m], cv=5, scoring="roc_auc"))), 3)
                lg.fit(Xs, y[m]); kq["he_so_chieu"] = {c: round(float(v), 3) for c, v in zip(Xs.columns, lg.coef_[0])}
            kq["buoc_luoi_atr"] = DT.buoc_luoi_atr(df[df.symbol == sym], f, p)
        else:
            kq["phan_biet"] = None; kq["ly_do"] = f"chỉ {len(dau)} lệnh đầu rổ trong vùng giá"
    else:
        kq["phan_biet"] = None; kq["ly_do"] = f"không có giá H1 cho {sym} trên box"
    return kq


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--thu-muc", default="data/cong_khai/csv"); ap.add_argument("--ra", default="data/dich_nguoc/top10.json")
    a = ap.parse_args(); ra = []
    for f in sorted(glob.glob(f"{a.thu_muc}/*.history.csv")):
        k = mot(f); ra.append(k)
        pb = k.get("phan_biet") or {}; pg = k.get("phan_biet_bo_gio") or {}
        print(k["id"], k["symbol_chinh"], k["phong_cach"], "AUC", pb.get("auc_cay_cv5"), pb.get("auc_logistic_cv5"), "bỏ giờ", pg.get("auc_cay_cv5"), pg.get("auc_logistic_cv5"), flush=True)
    Path(a.ra).parent.mkdir(parents=True, exist_ok=True)
    Path(a.ra).write_text(json.dumps(ra, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
