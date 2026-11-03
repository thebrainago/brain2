# -*- coding: utf-8 -*-
"""MÔ PHỎNG Python cho 2 ứng viên dịch ngược (lưới hedge). Không phải Strategy Tester MT5.
Đường đi trong nến: O->L->H->C nếu nến tăng, O->H->L->C nếu nến giảm; giữa hai đỉnh chèn mọi mức lưới bị cắt.
Phí: spread cố định (pip) trừ mỗi lệnh; SWAP KHÔNG TÍNH (CHƯA ĐO ĐƯỢC) ; không mô phỏng margin/stop-out ngoài equity<=0.
    python -m nhan.dich_nguoc.backtest_luoi
"""
from __future__ import annotations
import json, math
import numpy as np
import pandas as pd

FX = "/workspace/du_lieu_fx/"


def doc(p):
    g = pd.read_csv(p, usecols=["time", "open", "high", "low", "close"], parse_dates=["time"]).set_index("time").sort_index()
    return g


def chay(g, kieu, pip, buoc, tp, spread, gia_tri_pip_lot, von=1000.0, lot_moi_1000=0.01, max_lenh=60, dong_ro_khi=6):
    """kieu='luoi_tp' (2330430): mỗi lệnh TP = tp pip; mở BUY/SELL mới khi không có lệnh cùng chiều trong ±buoc quanh giá;
                                  đóng tất cả khi tổng lãi nổi >= 0 và số lệnh mở >= dong_ro_khi.
       kieu='ro_dca' (2262642): hai rổ BUY/SELL độc lập; thêm lệnh khi giá đi ngược buoc pip từ lệnh cuối;
                                  đóng cả rổ khi giá về giá-trung-bình ± tp pip."""
    bal = von; mo = []   # (chieu +1/-1, gia, lot)
    eq_min_ratio = 1.0; dinh = von; dd = 0.0; duong = []; chet = False
    def lot_moi():
        return max(0.0001, round(lot_moi_1000 * bal / 1000, 4))   # XM Micro: 0.01 lot micro = 0.0001 lot chuẩn
    def noi(p):
        return sum(c * (p - x) / pip * l * gia_tri_pip_lot for c, x, l in mo)
    def dong(i, p):
        nonlocal bal
        c, x, l = mo[i]; bal += (c * (p - x) / pip - spread) * l * gia_tri_pip_lot
    def buoc_gia(p):
        nonlocal mo, bal
        if kieu == "luoi_tp":
            giu = []
            for c, x, l in mo:
                if c * (p - x) >= tp * pip - 1e-12: bal += (tp - spread) * l * gia_tri_pip_lot
                else: giu.append((c, x, l))
            mo = giu
            if len(mo) >= dong_ro_khi and noi(p) >= 0:
                for i in range(len(mo)): dong(i, p)
                mo = []
            for c in (1, -1):
                if len([1 for cc, x, l in mo if cc == c]) < max_lenh and not any(cc == c and abs(x - p) < buoc * pip * 0.999 for cc, x, l in mo):
                    mo.append((c, p, lot_moi()))
        else:
            for c in (1, -1):
                ro = [(cc, x, l) for cc, x, l in mo if cc == c]
                if not ro:
                    mo.append((c, p, lot_moi())); continue
                tb = sum(x * l for _, x, l in ro) / sum(l for *_, l in ro)
                if c * (p - tb) >= tp * pip:
                    for cc, x, l in ro: bal += (c * (p - x) / pip - spread) * l * gia_tri_pip_lot
                    mo = [m for m in mo if m[0] != c]; mo.append((c, p, lot_moi()))
                elif len(ro) < max_lenh and c * (ro[-1][1] - p) >= buoc * pip:
                    mo.append((c, p, lot_moi()))
    O, H, L, C = (g[k].values for k in ("open", "high", "low", "close"))
    for t in range(len(g)):
        diem = [O[t], L[t], H[t], C[t]] if C[t] >= O[t] else [O[t], H[t], L[t], C[t]]
        for a, b in zip(diem[:-1], diem[1:]):
            n = max(1, int(abs(b - a) / (min(buoc, tp) * pip)) + 1)
            for k in range(1, n + 1):
                buoc_gia(a + (b - a) * k / n)
        # equity xấu nhất trong nến ~ min tại H/L
        e = bal + min(noi(H[t]), noi(L[t]))
        dinh = max(dinh, bal + noi(C[t])); dd = max(dd, 1 - e / dinh) if dinh > 0 else 1.0
        if e <= 0:
            chet = True; duong.append((g.index[t], 0.0)); break
        if t % 24 == 0: duong.append((g.index[t], bal + noi(C[t])))
    eq = 0.0 if chet else bal + noi(C[-1])
    nam = (g.index[-1] - g.index[0]).days / 365.25
    cagr = (eq / von) ** (1 / nam) - 1 if eq > 0 else -1.0
    return {"tu": str(g.index[0]), "den": str(g.index[-1]), "so_nam": round(nam, 2), "von": von, "equity_cuoi": round(float(eq), 2),
            "cagr": round(float(cagr), 4), "dd_max_equity": round(float(min(dd, 1.0)), 4), "chay_tai_khoan": bool(chet), "ngay_chay": str(duong[-1][0]) if chet else None,
            "dat": bool((not chet) and dd < 0.8 and cagr > 0.10)}


CAU_HINH = [
    # (tên, file, pip, spread pip, giá trị pip/lot USD xấp xỉ)
    ("AUDCAD_H1_2008_2026", FX + "audcad_h1_tu_histdata_m5_ny7.csv", 1e-4, 2.5, 7.3),
    ("GBPUSD_H1_2024_2026", FX + "gbpusd_h1_duka_ba_2024_2026.csv", 1e-4, 1.5, 10.0),
]
UNG_VIEN = {
    "UV1_luoi_hedge_tp35_(2330430)": dict(kieu="luoi_tp", buoc=35, tp=35),
    "UV2_ro_dca_hedge_15pip_(2262642)": dict(kieu="ro_dca", buoc=15, tp=11, max_lenh=140),
}

if __name__ == "__main__":
    ra = []
    for ten_dl, f, pip, sp, gtp in CAU_HINH:
        g = doc(f)
        for uv, ts in UNG_VIEN.items():
            for lot in (0.01, 0.004, 0.002, 0.001, 0.0005):
                k = chay(g, pip=pip, spread=sp, gia_tri_pip_lot=gtp, lot_moi_1000=lot, **ts)
                k.update(ung_vien=uv, du_lieu=ten_dl, lot_moi_1000=lot, tham_so=ts); ra.append(k)
                print(json.dumps(k, ensure_ascii=False), flush=True)
    json.dump(ra, open("data/dich_nguoc/backtest_luoi.json", "w"), ensure_ascii=False, indent=1)
