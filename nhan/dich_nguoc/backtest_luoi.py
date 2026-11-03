# -*- coding: utf-8 -*-
"""MÔ PHỎNG Python cho 2 ứng viên dịch ngược (lưới hedge). Không phải Strategy Tester MT5.
Đường đi trong nến: O->L->H->C nếu nến tăng, O->H->L->C nếu nến giảm; giữa hai đỉnh chèn mọi mức lưới bị cắt.
Phí: spread cố định (pip) trừ mỗi lệnh. SWAP (từ 03/11): điểm/lot/ngày theo bảng đo trong repo (config/phi_xm_micro.json — XM;
thiếu cặp thì config/chi_phi_do.json — FXCE), cộng lúc qua ngày (nến 00h), x3 đêm thứ Tư; lịch sử swap 2008–2026 CHƯA ĐO ĐƯỢC
(dùng giá trị hiện tại cho cả quá khứ) + kịch bản BẢO THỦ: cả hai chiều = −max(|mua|,|bán|).
MARGIN: đòn bẩy cố định (mặc định 1:500), margin = lô của chân lớn hơn (kiểu hedged MT5) × contract × giá base/USD (hằng số xấp xỉ) / đòn bẩy;
STOP-OUT khi equity/margin < 20% (mức XM) -> đóng TẤT CẢ lệnh tại giá xấu nhất của nến (đơn giản hơn MT5 đóng từng lệnh lỗ nhất).
    python -m nhan.dich_nguoc.backtest_luoi
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

FX = "/workspace/du_lieu_fx/"


def doc(p):
    g = pd.read_csv(p, usecols=["time", "open", "high", "low", "close"], parse_dates=["time"]).set_index("time").sort_index()
    return g


def chay(g, kieu, pip, buoc, tp, spread, gia_tri_pip_lot, von=1000.0, lot_moi_1000=0.01, max_lenh=60, dong_ro_khi=6,
         swap_mua=0.0, swap_ban=0.0, diem=1e-5, base_usd=None, don_bay=500.0, stop_out=0.2, ghi_vao=None):
    """kieu='luoi_tp' (2330430): mỗi lệnh TP = tp pip; mở BUY/SELL mới khi không có lệnh cùng chiều trong ±buoc quanh giá;
                                  đóng tất cả khi tổng lãi nổi >= 0 và số lệnh mở >= dong_ro_khi.
       kieu='ro_dca' (2262642): hai rổ BUY/SELL độc lập; thêm lệnh khi giá đi ngược buoc pip từ lệnh cuối;
                                  đóng cả rổ khi giá về giá-trung-bình ± tp pip."""
    bal = von; mo = []   # (chieu +1/-1, gia, lot)
    eq_min_ratio = 1.0; dinh = von; dd = 0.0; duong = []; chet = False
    t_hien = [0]
    def lot_moi(c=0):
        if ghi_vao is not None:
            ghi_vao.append((t_hien[0], c))   # 03/11: (chỉ số nến, chiều) mỗi lệnh vào — đo khớp với lệnh thật
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
                    mo.append((c, p, lot_moi(c)))
        else:
            for c in (1, -1):
                ro = [(cc, x, l) for cc, x, l in mo if cc == c]
                if not ro:
                    mo.append((c, p, lot_moi(c))); continue
                tb = sum(x * l for _, x, l in ro) / sum(l for *_, l in ro)
                if c * (p - tb) >= tp * pip:
                    for cc, x, l in ro: bal += (c * (p - x) / pip - spread) * l * gia_tri_pip_lot
                    mo = [m for m in mo if m[0] != c]; mo.append((c, p, lot_moi(c)))
                elif len(ro) < max_lenh and c * (ro[-1][1] - p) >= buoc * pip:
                    mo.append((c, p, lot_moi(c)))
    O, H, L, C = (g[k].values for k in ("open", "high", "low", "close"))
    ngay = g.index.normalize(); thu = g.index.dayofweek; so_stop_out = 0; tong_swap = 0.0
    sw_usd = {1: swap_mua * diem / pip * gia_tri_pip_lot, -1: swap_ban * diem / pip * gia_tri_pip_lot}
    def margin():
        if base_usd is None: return 0.0
        b = sum(l for c, x, l in mo if c == 1); s_ = sum(l for c, x, l in mo if c == -1)
        return max(b, s_) * 100000 * base_usd / don_bay
    for t in range(len(g)):
        t_hien[0] = t
        if t > 0 and ngay[t] != ngay[t - 1] and mo:
            k3 = 3 if thu[t - 1] == 2 else 1
            sw = sum(sw_usd[c] * l for c, x, l in mo) * k3; bal += sw; tong_swap += sw
        diem = [O[t], L[t], H[t], C[t]] if C[t] >= O[t] else [O[t], H[t], L[t], C[t]]
        for a, b in zip(diem[:-1], diem[1:]):
            n = max(1, int(abs(b - a) / (min(buoc, tp) * pip)) + 1)
            for k in range(1, n + 1):
                buoc_gia(a + (b - a) * k / n)
        # equity xấu nhất trong nến ~ min tại H/L
        e = bal + min(noi(H[t]), noi(L[t]))
        m = margin()
        if m > 0 and e < stop_out * m:
            p_xau = L[t] if noi(L[t]) < noi(H[t]) else H[t]
            for i in range(len(mo)): dong(i, p_xau)
            mo = []; so_stop_out += 1; e = bal
        dinh = max(dinh, bal + noi(C[t])); dd = max(dd, 1 - e / dinh) if dinh > 0 else 1.0
        if e <= 0 or bal < 0.01 * von:
            chet = True; duong.append((g.index[t], 0.0)); break
        if t % 24 == 0: duong.append((g.index[t], bal + noi(C[t])))
    eq = 0.0 if chet else bal + noi(C[-1])
    nam = (g.index[-1] - g.index[0]).days / 365.25
    cagr = (eq / von) ** (1 / nam) - 1 if eq > 0 else -1.0
    return {"tu": str(g.index[0]), "den": str(g.index[-1]), "so_nam": round(nam, 2), "von": von, "equity_cuoi": round(float(eq), 2),
            "cagr": round(float(cagr), 4), "so_stop_out": so_stop_out, "tong_swap": round(tong_swap, 2), "dd_max_equity": round(float(min(dd, 1.0)), 4), "chay_tai_khoan": bool(chet), "ngay_chay": str(duong[-1][0]) if chet else None,
            "dat": bool((not chet) and dd < 0.8 and cagr > 0.10)}


HD = FX + "hd_dai/"


def doc_dai(ten):
    """Nối H1 dài: histdata M1 2008–2023 (gộp H1, giờ NY+7) + chuỗi 2024–2026 sẵn có (M5/H1, NY+7)."""
    t = ten.lower(); phan = []
    for f in (HD + f"{t}_h1_2008_2023_ny7.csv",):
        try: phan.append(doc(f))
        except FileNotFoundError: pass
    sau = {"audcad": FX + "audcad_h1_tu_histdata_m5_ny7.csv", "eurchf": FX + "hd28/eurchf_m5.csv",
           "audnzd": FX + "hd28/audnzd_m5.csv", "eurgbp": FX + "eurgbp_h1_tu_histdata_m5_ny7.csv",
           "xauusd": FX + "xauusd_h1_tu_histdata_m5_ny7.csv"}.get(t)
    if sau:
        g = doc(sau)
        if (g.index[1] - g.index[0]) < pd.Timedelta("1h"):
            g = g.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        if phan: g = g[g.index > phan[-1].index[-1]]
        phan.append(g)
    if not phan: return None
    g = pd.concat(phan).sort_index(); return g[~g.index.duplicated()]


def _swap(sym):
    m = json.load(open(Path(__file__).resolve().parents[2] / "config/phi_xm_micro.json"))
    if sym in m: return m[sym]["swap_mua_diem"], m[sym]["swap_ban_diem"], "XM đo 06/10/2026"
    d = json.load(open(Path(__file__).resolve().parents[2] / "config/chi_phi_do.json"))
    if sym in d: return d[sym]["swap_long"], d[sym]["swap_short"], "FXCE đo 22/08/2026 (không phải XM)"
    return None


# (symbol, pip, spread pip, giá trị pip/lot USD xấp xỉ, giá base/USD xấp xỉ) — hằng số, ghi rõ là xấp xỉ
CAP = [("AUDCAD", 1e-4, 2.5, 7.3, 0.70), ("EURCHF", 1e-4, 3.2, 11.2, 1.10), ("AUDNZD", 1e-4, 4.0, 6.0, 0.70),
       ("NZDCAD", 1e-4, 3.0, 7.3, 0.60), ("EURGBP", 1e-4, 1.5, 13.0, 1.10)]
UNG_VIEN = {
    "UV1_luoi_hedge_tp35_(2330430)": dict(kieu="luoi_tp", buoc=35, tp=35),
    "UV2_ro_dca_hedge_15pip_(2262642)": dict(kieu="ro_dca", buoc=15, tp=11, max_lenh=140),
}
LOT = (0.002, 0.001, 0.0005, 0.00025)

if __name__ == "__main__":
    import sys
    ra = []; chon = sys.argv[1:]
    for sym, pip, sp, gtp, busd in [x for x in CAP if not chon or x[0] in chon]:
        g = doc_dai(sym); sw = _swap(sym)
        if g is None or sw is None or (g.index[-1] - g.index[0]).days < 365 * 8:
            print(sym, "bỏ: thiếu dữ liệu dài hoặc swap", flush=True); continue
        bt = max(abs(sw[0]), abs(sw[1]))
        for kb, (sm, sb) in {"swap_do": sw[:2], "swap_bao_thu": (-bt, -bt), "swap_0_lac_quan": (0.0, 0.0)}.items():
            for uv, ts in UNG_VIEN.items():
                for lot in LOT:
                    k = chay(g, pip=pip, spread=sp, gia_tri_pip_lot=gtp, lot_moi_1000=lot, swap_mua=sm, swap_ban=sb,
                             base_usd=busd, **ts)
                    k.update(ung_vien=uv, du_lieu=f"{sym}_H1_{g.index[0].year}_{g.index[-1].year}", lot_moi_1000=lot,
                             kich_ban_swap=kb, swap_diem=[sm, sb], nguon_swap=sw[2], tham_so=ts); ra.append(k)
                    print(json.dumps(k, ensure_ascii=False), flush=True)
    json.dump(ra, open(f"data/dich_nguoc/backtest_luoi_{'_'.join(chon) or 'tat_ca'}.json", "w"), ensure_ascii=False, indent=1)
