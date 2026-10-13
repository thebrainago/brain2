# -*- coding: utf-8 -*-
"""phan_tich_luoi_box.py - PHAN TICH PYTHON tren BOX chay song song voi MT5 may nha (vong 27). MO PHONG, khong phai tien that.

Cung luoi tham so voi mt5tools/sinh_viec.py (MRZ/RSI, D1) tren gia D1 XM (xuat tu MT5 may nha), chia IS 2016-2022 / OOS 2023-2026-10.
Phi: spread trung vi theo gio XM do that (reports/mt5_v27/spread_gio) luc vao (gio InpGioVao) + luc ra (trung vi ca ngay); CHUA tinh swap.
Moi bien the deu ghi -> Holm tren tong so lan thu IS. Ket qua: reports/mt5_lien_tuc/box_luoi_python.json
"""
from __future__ import annotations

import functools
import itertools
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "mt5tools"))
import sinh_viec as SV  # noqa: E402

GOC = Path(__file__).resolve().parent


def _atr_rsi(h, l, c):
    """ATR14 + (eu, ed) Wilder - khong phu thuoc tham so luoi -> tinh 1 lan / chuoi (toi uu vong lap chu ky 5)."""
    n = len(c); A = [0.0] * n; atr = h[0] - l[0]; A[0] = atr; eu = ed = None; EU = [None] * n; ED = [None] * n
    for i in range(1, n):
        pc = c[i - 1]; tr = max(h[i] - l[i], abs(h[i] - pc), abs(l[i] - pc)); atr += (tr - atr) / 14; A[i] = atr
        d = c[i] - pc; u, v = max(d, 0.0), max(-d, 0.0)
        if eu is None: eu, ed = u, v
        else: eu += (u - eu) / 14; ed += (v - ed) / 14
        EU[i], ED[i] = eu, ed
    return A, EU, ED


def _z_mrz(c, mrz_n):
    """z-score cua so (cung cong thuc goc, ket qua trung tung bit) - tinh 1 lan / (chuoi, mrz_n), dung lai cho moi nguong z."""
    n = len(c); Z = [None] * n
    for i in range(mrz_n - 1, n):
        w = c[i - mrz_n + 1:i + 1]; m = sum(w) / mrz_n; sd = math.sqrt(sum((x - m) ** 2 for x in w) / (mrz_n - 1))
        if sd > 0:
            Z[i] = (c[i] - m) / sd
    return Z


def chi_bao(h, l, c, che, z_ng, mrz_n, r_thap, r_cao, _dem=None):
    """Giu giao dien cu. _dem (dict) = dem chi bao dung chung trong 1 chuoi."""
    dem = _dem if _dem is not None else {}
    if "atr" not in dem:
        dem["atr"] = _atr_rsi(h, l, c)
    A, EU, ED = dem["atr"]; n = len(c); T = [0] * n
    if che == "RSI":
        for i in range(1, n):
            eu, ed = EU[i], ED[i]
            if eu == 0 and ed == 0: continue
            r = 100.0 if ed == 0 else 100 - 100 / (1 + eu / ed); T[i] = 1 if r < r_thap else (-1 if r > r_cao else 0)
    else:
        k = ("z", mrz_n)
        if k not in dem:
            dem[k] = _z_mrz(c, mrz_n)
        for i, z in enumerate(dem[k]):
            if z is not None and i >= 1:
                T[i] = 1 if z < -z_ng else (-1 if z > z_ng else 0)
    return A, T


def mo_phong(o, h, l, c, A, T, sl_atr, tr_atr, giu, chi_phi, bat_dau=60):
    n = len(c); out = []; pos = None
    for k in range(bat_dau + 1, n):
        if pos is not None:
            s, j, E, st, best = pos
            if k - j >= giu:
                out.append((j, s * (o[k] - E) - chi_phi)); pos = None; continue
            best = c[k - 1] if best is None else (max(best, c[k - 1]) if s > 0 else min(best, c[k - 1]))
            st = max(st, best - tr_atr * A[k - 1]) if s > 0 else min(st, best + tr_atr * A[k - 1]); pos = (s, j, E, st, best)
        elif T[k - 1] != 0:
            s = T[k - 1]; E = o[k]; pos = (s, k, E, E - s * sl_atr * A[k - 1], None)
        if pos is not None:
            s, j, E, st, best = pos
            if (s > 0 and l[k] <= st) or (s < 0 and h[k] >= st):
                out.append((j, s * (st - E) - chi_phi)); pos = None
    return out


@functools.lru_cache(maxsize=None)
def chi_phi_ma(ma: str, gio: int) -> float:
    f = GOC / "reports/mt5_v27/spread_gio" / (ma.replace("#", "").replace(".", "_") + ".csv")
    pt = 0.001 if "JPY" in ma else (0.01 if ma.startswith(("GOLD", "US", "GER")) else (0.001 if ma.startswith("SILVER") else 0.00001))
    if not f.exists():
        return None
    g = pd.read_csv(f, index_col=0)
    vao = g["trung_vi_point"].get(gio, g["trung_vi_point"].median()); ra = g["trung_vi_point"].median()
    return (vao + ra) * pt


def _mot_ma(f: Path) -> list[dict]:
    """Toan bo luoi cho 1 ma (chay trong tien trinh con). Ket qua trung tung dong voi ban tuan tu cu."""
    out = []
    ma = f.stem.replace("_D1", "")
    ma_xm = next((m for m in SV.MA if m.replace("#", "").replace(".", "_") == ma), None)
    if not ma_xm:
        return out
    d = pd.read_csv(f, parse_dates=["time"])
    o, h, l, c = (d[k].tolist() for k in ("open", "high", "low", "close")); t = d["time"]
    is_ = ((t >= "2016-01-01") & (t <= "2022-12-31")).to_numpy(); oos = ((t >= "2023-01-01") & (t <= "2026-10-01")).to_numpy()
    dem = {}
    for che in ("MRZ", "RSI"):
        luoi_rieng = [(z, n, 30, 70) for z in (1.5, 2.0, 2.5) for n in (20, 50, 100)] if che == "MRZ" else [(2, 50, a, b) for a in (20, 25, 30) for b in (70, 75, 80)]
        for (z, mn, ra_, rc) in luoi_rieng:
            A, T = chi_bao(h, l, c, che, z, mn, ra_, rc, dem)
            L0 = {}
            for tr, giu, gv, sl in itertools.product((1.5, 2.0, 2.5, 3.0), (5, 20, 72), (0, 2), (1.0, 1.5, 2.0)):
                cp = chi_phi_ma(ma_xm, gv)
                if cp is None:
                    continue
                # mo_phong khong phu thuoc gio vao ngoai phi co dinh -> chay 1 lan phi 0 roi tru phi (cung phep tru -> trung bit)
                if (tr, giu, sl) not in L0:
                    L0[(tr, giu, sl)] = mo_phong(o, h, l, c, A, T, sl, tr, giu, 0.0)
                L = [(j, x - cp) for j, x in L0[(tr, giu, sl)]]
                for pha, mask in (("IS", is_), ("OOS", oos)):
                    r = [x for j, x in L if mask[j]]
                    if not r:
                        continue
                    lai = sum(x for x in r if x > 0); lo = -sum(x for x in r if x < 0)
                    ts = {"InpGioVao": gv, "InpGiuToiDa": giu, "InpSlATR": sl, "InpTrATR": tr}
                    ts.update({"InpNguongZ": z, "InpMrzN": mn} if che == "MRZ" else {"InpRsiThap": ra_, "InpRsiCao": rc})
                    out.append({"ea": che, "ma": ma_xm, "tf": "D1", "ts": ts, "pha": pha, "lenh": len(r),
                                "net": round(sum(r) / c[-1] * 1e4, 1), "pf": round(lai / lo, 3) if lo > 0 else 99.0, "p": round(SV.p_gia_tri(r), 6)})
    return out


def chay(thu_muc_d1: str, ra: str, tien_trinh: int | None = None):
    import os
    from concurrent.futures import ProcessPoolExecutor
    tep = sorted(Path(thu_muc_d1).glob("*_D1.csv"))
    tien_trinh = tien_trinh or min(len(tep) or 1, os.cpu_count() or 1)
    out = []
    if tien_trinh <= 1:
        phan = map(_mot_ma, tep)
    else:
        ex = ProcessPoolExecutor(tien_trinh); phan = ex.map(_mot_ma, tep)  # map giu thu tu -> dau ra trung ban tuan tu
    for f, p in zip(tep, phan):
        out.extend(p)
        if p:
            print(p[0]["ma"], len(out), flush=True)
    if tien_trinh > 1:
        ex.shutdown()
    sc = out
    tk = SV.tong_ket(sc)
    import gzip
    with gzip.open(ra.replace(".json", "_chi_tiet.jsonl.gz"), "wt", encoding="utf-8") as g:
        for r in sc:
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
    tk["ung_vien_ca_hai"].sort(key=lambda u: -min(u["IS"]["pf"], u["OOS"]["pf"]))
    json.dump({"ghi_chu": "MO PHONG Python tren gia D1 XM; net = tong bps (so voi gia cuoi); phi = spread XM theo gio, CHUA swap. "
               "Holm tren moi lan thu IS; chi tiet: *_chi_tiet.jsonl.gz", "tong_ket": tk}, open(ra, "w"), ensure_ascii=False, indent=0)
    print(json.dumps({k: v for k, v in tk.items() if k != "ung_vien_ca_hai"}), "ung_vien:", len(tk["ung_vien_ca_hai"]),
          "holm:", sum(u["holm"] for u in tk["ung_vien_ca_hai"]))


if __name__ == "__main__":
    chay(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else str(GOC / "reports/mt5_lien_tuc/box_luoi_python.json"))
