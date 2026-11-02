# -*- coding: utf-8 -*-
"""Đặc trưng bối cảnh tại mỗi lệnh vào (chỉ dùng nến ĐÃ ĐÓNG trước thời điểm vào) so với thời điểm ngẫu nhiên
(cùng phân bố giờ không bị ép) -> mô hình đơn giản (cây quyết định nông + logistic) tìm đặc trưng phân biệt."""
from __future__ import annotations
import numpy as np
import pandas as pd

TEN = ["rsi14", "atr14_pip", "kc_ma50_atr", "bb_z20", "pha_phien_a", "gio", "thu", "loi_suat_5bar_atr"]


def doc_gia(p) -> pd.DataFrame:
    df = pd.read_csv(p) if isinstance(p, str) else p.copy()
    df.columns = [c.lower().strip("<>") for c in df.columns]
    if "time" not in df and "date" in df:
        df["time"] = df["date"] + (" " + df["time"] if "time" in df else "")
    df["time"] = pd.to_datetime(df["time"]); df = df.set_index("time").sort_index()
    return df[["open", "high", "low", "close"]].astype(float)


def chi_bao(g: pd.DataFrame, pip: float) -> pd.DataFrame:
    c = g["close"]; d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    tr = pd.concat([g.high - g.low, (g.high - c.shift()).abs(), (g.low - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    ma50 = c.rolling(50).mean(); m20 = c.rolling(20).mean(); s20 = c.rolling(20).std()
    ngay = g.index.normalize(); a = g[g.index.hour < 7]
    ah = a.groupby(a.index.normalize())["high"].max(); al = a.groupby(a.index.normalize())["low"].min()
    ah = pd.Series(ngay.map(ah), index=g.index); al = pd.Series(ngay.map(al), index=g.index)
    pha = np.where(g.index.hour < 7, 0, np.where(c > ah, 1, np.where(c < al, -1, 0)))
    f = pd.DataFrame({"rsi14": rsi, "atr14_pip": atr / pip, "kc_ma50_atr": (c - ma50) / atr, "bb_z20": (c - m20) / s20,
                      "pha_phien_a": pha, "gio": g.index.hour, "thu": g.index.dayofweek,
                      "loi_suat_5bar_atr": (c - c.shift(5)) / atr}, index=g.index)
    return f.shift(1)          # tại nến t chỉ biết giá trị của nến t-1 đã đóng -> không nhìn tương lai


def tai_thoi_diem(f: pd.DataFrame, luc: pd.Series) -> pd.DataFrame:
    i = f.index.searchsorted(pd.to_datetime(luc).values, side="right") - 1
    i = np.clip(i, 0, len(f) - 1)
    return f.iloc[i].reset_index(drop=True)


def phan_biet(f: pd.DataFrame, luc_vao: pd.Series, chieu: pd.Series | None = None, bo_qua_gio=False, hat=0, so_ngau_nhien=3) -> dict:
    """So đặc trưng lúc vào lệnh với mẫu ngẫu nhiên. Trả AUC kiểm chéo, xếp hạng đặc trưng và luật cây."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.tree import DecisionTreeClassifier, export_text
    rng = np.random.default_rng(hat)
    hop = f.dropna()
    X1 = tai_thoi_diem(f, luc_vao).dropna()
    chi_so = rng.choice(len(hop), size=min(len(hop), max(200, so_ngau_nhien * len(X1))), replace=False)
    X0 = hop.iloc[chi_so].reset_index(drop=True)
    X = pd.concat([X1, X0], ignore_index=True); y = np.r_[np.ones(len(X1)), np.zeros(len(X0))]
    cot = [c for c in TEN if not (bo_qua_gio and c in ("gio", "thu"))]
    X = X[cot]
    cay = DecisionTreeClassifier(max_depth=3, min_samples_leaf=max(5, len(X1) // 20), class_weight="balanced", random_state=hat)
    auc_cay = float(np.mean(cross_val_score(cay, X, y, cv=5, scoring="roc_auc")))
    cay.fit(X, y)
    Xs = (X - X.mean()) / X.std().replace(0, 1)
    lg = LogisticRegression(max_iter=2000, class_weight="balanced")
    auc_lg = float(np.mean(cross_val_score(lg, Xs, y, cv=5, scoring="roc_auc"))); lg.fit(Xs, y)
    # độ tách một biến: |AUC-0.5| khi dùng riêng từng đặc trưng (đo bằng xếp hạng)
    from sklearn.metrics import roc_auc_score
    don = {c: round(float(roc_auc_score(y, X[c])), 3) for c in cot}
    xep = sorted(cot, key=lambda c: -abs(don[c] - 0.5))
    tom = {c: {"vao_trung_vi": round(float(X1[c].median()), 3), "ngau_nhien_trung_vi": round(float(X0[c].median()), 3),
               "auc_don": don[c], "he_so_logistic": round(float(lg.coef_[0][cot.index(c)]), 3)} for c in xep}
    return {"so_lenh_vao": int(len(X1)), "so_mau_ngau_nhien": int(len(X0)), "auc_cay_cv5": round(auc_cay, 3),
            "auc_logistic_cv5": round(auc_lg, 3), "dac_trung_xep_hang": tom, "luat_cay": export_text(cay, feature_names=cot)}


def buoc_luoi_atr(df_lenh: pd.DataFrame, f: pd.DataFrame, pip: float) -> float | None:
    from .phan_tich import ro
    d = ro(df_lenh); r = []
    for _, g in d.groupby("ro"):
        if len(g) < 2: continue
        g = g.sort_values("mo_luc"); atr = tai_thoi_diem(f, g["mo_luc"].iloc[1:])["atr14_pip"].values
        r += list(np.abs(np.diff(g["gia_mo"].values)) / pip / atr)
    r = [x for x in r if np.isfinite(x)]
    return round(float(np.median(r)), 2) if r else None
