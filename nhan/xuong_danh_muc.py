# -*- coding: utf-8 -*-
"""xuong_danh_muc.py - TOAN TU DANH MUC cua XUONG (22/10/2026, Claude): ghep CHEO cac he dat thanh bo chay CUNG LUC.

Khac `xuong_toan_tu` (moi toan tu cho RA MOT the = mot chuoi lenh vao + mot bo quan li): danh muc la NHIEU EA, moi EA mot chart, chung mot tai khoan.
Ket qua khong phai the moi ma la MOT BANG LOT (lot nhan cho tung the) - EA nao chay lot nao tren cung tai khoan.

Cach tinh (MÔ PHỎNG, xap xi cong duong von):
  - moi the chay MOT lan tren toan ky o lot khuyen nghi, giu duong von (dong + tinh ca lenh dang ket) -> chuan ve ti le X_i(t) = von_i(t)/von_i(0) - 1;
  - danh muc von(t) = 1 + s * sum_i X_i(t) (s = he so lot chung); s duoc keo bang chia doi de sut giam danh muc = muc tieu;
  - tham lam: bat dau tu the co lai@DD cao nhat, them the nao lam lai@DD cua DANH MUC tang them it nhat `tang_toi_thieu` (mac dinh 3 %);
  - tuong quan ngay giua cac duong von la thong tin canh bao, khong phai cong.
GIOI HAN (nho ro): cong duong von la xap xi - ky quy CHUNG, stop-out chung, va lenh DCA tang lot theo von khong duoc mo phong o day. Muon chinh xac:
chay hai EA tren cung tai khoan tren MT5 (hoac `TK.chay_tk` nhieu ma). Nen co bo so nho (<= 5 the) va s <= 1 de co khoang ky quy an toan.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nhan import xuong_may as XM


def duong_von(may: XM.May, t: dict, thu: dict, lot: float) -> dict | None:
    """-> {"dong": Series ti le von (theo ngay, lenh dong), "xau": Series (tinh gia bat loi), "r": ket qua} hoac None neu khong do duoc.
    `may` PHAI mo bang giu_duong_von=True."""
    r = may.chay(t, thu, (0.0, 1.0), lot)
    if r.get("loi") or r.get("chay") or "duong_von" not in r:
        return None
    idx = pd.DatetimeIndex(r["chi_muc"])
    dong = pd.Series(np.asarray(r["duong_von"], float), index=idx)
    xau = pd.Series(np.asarray(r["von_xau"], float), index=idx)
    if len(dong) < 50 or float(dong.iloc[0]) <= 0:
        return None
    v0 = float(dong.iloc[0])
    return {"dong": (dong / v0).groupby(dong.index.normalize()).last(),
            "xau": (xau / v0).groupby(xau.index.normalize()).min(), "r": r}


def _dd(e: np.ndarray) -> float:
    dinh = np.maximum.accumulate(np.maximum(e, 1e-9))
    return float(np.max((dinh - e) / dinh)) * 100.0


def do_danh_muc(X_dong: np.ndarray, X_xau: np.ndarray, nam: float, dd_muc: float) -> dict:
    """X_* = tong (von_i - 1) theo ngay. Keo he so lot chung s toi sut giam muc tieu -> {s, lai_pct_nam, sut_giam_pct}."""
    def tai(s):
        e_xau, e_dong = 1.0 + s * X_xau, 1.0 + s * X_dong
        if e_xau.min() <= 0.02:
            return None
        return _dd(e_xau), e_dong[-1]
    lo, hi = 0.0, 1.0
    r = tai(hi)
    while r is not None and r[0] <= dd_muc and hi < 64:
        lo, hi = hi, hi * 2
        r = tai(hi)
    for _ in range(30):
        mid = (lo + hi) / 2
        rr = tai(mid)
        if rr is not None and rr[0] <= dd_muc:
            lo = mid
        else:
            hi = mid
    s = lo
    rr = tai(s) if s > 0 else (0.0, 1.0)
    if rr is None or rr[1] <= 0:
        return {"s": 0.0, "lai_pct_nam": -100.0, "sut_giam_pct": 100.0}
    return {"s": s, "lai_pct_nam": ((rr[1]) ** (1.0 / max(nam, 1e-6)) - 1.0) * 100.0, "sut_giam_pct": rr[0]}


def danh_muc(may_dv: XM.May, ung: list[tuple[dict, dict, float]], dd_muc: float = 60.0, toi_da: int = 5, tang_toi_thieu: float = 0.03,
             tq_max: float = 0.85) -> dict:
    """ung = [(the, thu, lot_khuyen_nghi)]. -> {"thanh_vien": [{"id", "lot", "lai_rieng"}], "lai_pct_nam", "sut_giam_pct", "tuong_quan_max",
    "so_nam", "luat_tang": ...} hoac {"loi": ...}. Chi tinh tren cac the do duoc, chung nhau it nhat 1,5 nam."""
    dv = {}
    for t, thu, lot in ung:
        d = duong_von(may_dv, t, thu, lot)
        if d is not None and d["r"].get("so_nam", 0) >= 1.0:
            dv[t["id"]] = (t, thu, lot, d)
    if not dv:
        return {"loi": "CHUA_DO_DUOC: khong the nao co duong von"}
    ngay = pd.DatetimeIndex(sorted(set().union(*[set(v[3]["dong"].index) for v in dv.values()])))
    X = {k: (v[3]["dong"].reindex(ngay).ffill().fillna(1.0).to_numpy() - 1.0) for k, v in dv.items()}
    Xx = {k: (v[3]["xau"].reindex(ngay).ffill().fillna(1.0).to_numpy() - 1.0) for k, v in dv.items()}
    # chi phan chung tu khi MOT he bat dau co du lieu den het: ngoai khoang cua he do, he khac dung 0 (chua chay) - dung ffill sau, nen ok
    nam = max((ngay[-1] - ngay[0]).days / 365.25, 1e-6)
    if nam < 1.5:
        return {"loi": "CHUA_DO_DUOC: chung nhau chi %.2f nam" % nam}
    bd = {k: do_danh_muc(X[k], Xx[k], nam, dd_muc) for k in dv}
    thu_tu = sorted(dv, key=lambda k: -bd[k]["lai_pct_nam"])
    ret = pd.DataFrame({k: np.diff(1.0 + X[k], prepend=1.0) for k in dv}, index=ngay)
    tq = ret.corr().fillna(0.0)
    tot = None
    for goc in thu_tu[:6]:
        nhom = [goc]
        cur = bd[goc]
        while len(nhom) < toi_da:
            tot_them = None
            for k in thu_tu:
                if k in nhom or max(abs(float(tq.at[k, x])) for x in nhom) > tq_max:
                    continue
                n2 = nhom + [k]
                d2 = do_danh_muc(sum(X[x] for x in n2), sum(Xx[x] for x in n2), nam, dd_muc)
                if d2["lai_pct_nam"] > cur["lai_pct_nam"] * (1 + tang_toi_thieu) and (tot_them is None or d2["lai_pct_nam"] > tot_them[1]["lai_pct_nam"]):
                    tot_them = (k, d2)
            if tot_them is None:
                break
            nhom.append(tot_them[0])
            cur = tot_them[1]
        if tot is None or cur["lai_pct_nam"] > tot[1]["lai_pct_nam"]:
            tot = (list(nhom), cur)
    nhom, cur = tot
    m = tq.loc[nhom, nhom].to_numpy()
    return {"thanh_vien": [{"id": k, "lot": round(dv[k][2] * cur["s"], 2), "lot_khuyen_nghi_rieng": dv[k][2], "lai_rieng_o_dd": round(bd[k]["lai_pct_nam"], 1)}
                           for k in nhom],
            "he_so_lot_chung": round(cur["s"], 3), "lai_pct_nam": round(cur["lai_pct_nam"], 2), "sut_giam_pct": round(cur["sut_giam_pct"], 2),
            "lai_tot_nhat_rieng": round(max(b["lai_pct_nam"] for b in bd.values()), 2),
            "tuong_quan_max": round(float(np.max(np.abs(m[np.triu_indices_from(m, 1)]))), 3) if len(nhom) > 1 else 0.0,
            "so_nam": round(nam, 2), "dd_muc_tieu": dd_muc, "so_ung_vien_do_duoc": len(dv),
            "nhan": "MÔ PHỎNG, xấp xỉ cộng đường vốn (chưa mô phỏng ký quỹ/stop-out chung); xác nhận bằng MT5 hai EA cùng tài khoản"}
