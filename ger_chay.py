#!/usr/bin/env python3
"""ger_chay.py - MO PHONG ho EA geraked/metatrader5 (thu vien GerEA, `nhan/ger_ea.py`) voi .set TAC GIA.

    python ger_chay.py [--ra reports/GER_EA.json]

Moi EA: (a) dung ma + khung tac gia ghi trong ten .set (vd `3MAF-USDCAD-15M-Inputs.set`), (b) EURUSD cung
khung, (c) EURUSD M5 va H1. Du lieu: HistData M1 -> M5 (`gop_histdata_m5.py`), khung lon = gop tu M5
(nhan trai, gio Helsinki). Phi XM (`vong_thu_nghiem.mo_hinh_chi_phi`). Tai khoan = TAI_KHOAN_MAC_DINH.
TAT CA LA MO PHONG - khong phai tien that. Cong giu KHONG doi: lai sau phi + maxDD < 80% + khong chay.
"""
from __future__ import annotations

import glob
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
from nhan import ger_ea as G                       # noqa: E402
from nhan import ger_ea_tin_hieu as T              # noqa: E402
import vong_thu_nghiem as V                        # noqa: E402

DL = Path("/workspace/du_lieu_fx")
KHO = GOC / "data" / "cau_kho" / "goi_github"
KHUNG_PHUT = {"5M": 5, "15M": 15, "30M": 30, "1H": 60, "3H": 180, "M5": 5, "H1": 60}


def du_lieu(ma: str, phut: int, tep: str | None = None) -> pd.DataFrame:
    df = V.doc_csv(DL / (tep or f"{ma.lower()}_m5_histdata_server.csv"))
    if phut == 5:
        return df
    g = df.resample(f"{phut}min", label="left", closed="left")
    r = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                      "close": g["close"].last()})
    return r.dropna()


def diem_cua(ma: str) -> float:
    m = ma.upper()
    return 0.01 if m.startswith("XAU") else 1e-3 if m.endswith("JPY") else 1e-5


def mot_lan(ten: str, vb: str, th: dict, ma: str, phut: int, tk: G.TaiKhoan,
            duong_m5: bool = True) -> dict:
    df = du_lieu(ma, phut)
    cp = V.mo_hinh_chi_phi(df, ma)
    diem = diem_cua(ma)
    s = cp.spread_mang(df.index) * df["open"].to_numpy(float)
    th_ = dict(th)
    tin, cb = T.TIN_HIEU[ten](df, th_, s, diem)
    ts, cb2 = G.tham_so_tu_ma(vb, th_)
    t0 = time.time()
    if phut > 5 and duong_m5:
        # Tin hieu tren khung EA, KHOP LENH + luoi + keo SL tren duong gia M5 (bar lon giau duong di
        # trong bar - luoi nhay cam nhat voi cho nay). Tin hieu bar lon j -> bar M5 dau tien >= open j.
        d5 = du_lieu(ma, 5)
        cp5 = V.mo_hinh_chi_phi(d5, ma)
        vt = d5.index.searchsorted(df.index)
        tin5 = {k: __import__("numpy").zeros(len(d5), dtype=v.dtype) for k, v in tin.items()}
        ok = vt < len(d5)
        for k in tin:
            tin5[k][vt[ok]] = tin[k][ok]
        # gia vao tinh lai theo open M5 cua bar khop (= open bar lon khi bar M5 do ton tai)
        kq = G.chay(d5, tin5, ts, cp5, ma, diem, tk)
        cb2 = cb2 + ["khop lenh/luoi/keo SL tren duong gia M5 (tin hieu khung %d phut)" % phut]
    else:
        kq = G.chay(df, tin, ts, cp, ma, diem, tk)
    cs = G.chi_so(kq, tk.von)
    # nua sau (30% cuoi) rieng: von dau = von rong tai moc cat
    e = kq.duong_von
    cat = int(len(e) * 0.7)
    v0 = float(e.iloc[cat - 1]) if cat > 0 else tk.von
    cs["lai_30pct_cuoi_pct"] = round((kq.von_cuoi / v0 - 1) * 100, 2) if v0 > 0 else None
    cs["giu"] = bool(cs["lai_sau_phi_pct"] > 0 and cs["maxdd_pct"] < 80 and not cs["chay"])
    cs.update({"ma": ma, "khung_phut": phut, "bar": len(df), "tu": str(df.index[0]),
               "den": str(df.index[-1]), "tin_hieu_mua": int((tin["huong"] > 0).sum()),
               "tin_hieu_ban": int((tin["huong"] < 0).sum()), "giay": round(time.time() - t0, 1),
               "phi": cp.phien_ban(), "canh_bao": cb + cb2 + kq.canh_bao,
               "spread_bps_tb": round(float(cp.spread_frac_chung) * 1e4, 2)})
    return cs


def main(argv=None) -> int:
    a = list(argv if argv is not None else sys.argv[1:])
    ra = Path(a[a.index("--ra") + 1]) if "--ra" in a else GOC / "reports" / "GER_EA.json"
    tk = G.TaiKhoan(**{k: v for k, v in V.TAI_KHOAN_MAC_DINH.items()
                       if k in ("von", "don_bay", "stop_out", "lot_max")})
    # do nhay tai khoan (KHONG doi cong): XM quoc te don bay toi 1:1000, stop-out 20%
    tk_xm = G.TaiKhoan(von=tk.von, don_bay=500.0, stop_out=0.2, lot_max=tk.lot_max)
    bang = {"luc": time.strftime("%Y-%m-%d %H:%M:%S"), "nhan": "MO PHONG (Python, HistData BID, phi XM)",
            "tai_khoan": vars(tk), "ea": {}, "chua_dich": T.CHUA_DICH}
    for ten in T.TIN_HIEU:
        d = KHO / f"geraked__metatrader5__Experts_{ten}"
        vb = (d / f"{ten}.mq5").read_text(encoding="utf-8", errors="ignore")
        sets = sorted(glob.glob(str(d / "*.set")))
        st = Path(sets[0]).read_text(encoding="utf-8", errors="ignore") if sets else None
        th, bo = G.gop_tham_so(vb, st)
        m = re.match(r"[^-]+-([A-Z]{6})-(\w+)-Inputs", Path(sets[0]).name) if sets else None
        lan = []
        if m and (DL / f"{m.group(1).lower()}_m5_histdata_server.csv").exists():
            lan.append((m.group(1), KHUNG_PHUT[m.group(2)]))
        if m:
            lan.append(("EURUSD", KHUNG_PHUT[m.group(2)]))
        lan += [("EURUSD", 5), ("EURUSD", 60)]
        lan = list(dict.fromkeys(lan))
        kq = {"set": Path(sets[0]).name if sets else None, "set_bo_qua": bo, "lan": []}
        for ma, ph in lan:
            for nhan_tk, tk_ in (("mac_dinh_1:100_so50", tk), ("XM_1:500_so20", tk_xm)):
                try:
                    r = mot_lan(ten, vb, th, ma, ph, tk_)
                except NotImplementedError as e:
                    r = {"ma": ma, "khung_phut": ph, "loi": str(e)}
                r["tai_khoan"] = nhan_tk
                kq["lan"].append(r)
                print(ten, ma, ph, nhan_tk, {k: r.get(k) for k in (
                    "lai_sau_phi_pct", "lai_30pct_cuoi_pct", "maxdd_pct", "sharpe", "so_ro",
                    "so_lenh", "tang_max", "so_stop_out", "chay", "giu", "loi")}, flush=True)
        bang["ea"][ten] = kq
    ra.write_text(json.dumps(bang, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("ghi", ra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
