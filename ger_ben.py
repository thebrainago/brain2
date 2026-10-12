#!/usr/bin/env python3
"""ger_ben.py - KIEM DO BEN (MO PHONG) cho cac o GerEA dat nhan cong (12/10/2026, vong 5).

    python ger_ben.py [--ra reports/GER_BEN.json]

Moi o (EA, .set tac gia KHONG DOI, EURUSD H1, khop/luoi tren duong M5):
  1. cua so roi nhau 6 doan (moi doan von moi 10.000) + theo nam  (khong chinh tham so -> moi doan la ngoai mau)
  2. 8 diem bat dau lech nhau (luoi phu thuoc duong di)
  3. thu tu trong bar: gan_open / thap_truoc / cao_truoc -> lay XAU NHAT
  4. spread XM x1.5 (va truot gia x1.5 theo, vi truot = 1/4 spread)
  5. cap khac (cung khung H1): GBPUSD USDJPY USDCHF AUDUSD NZDUSD USDCAD XAUUSD
  6. EURUSD 2018-2023 (truoc chuoi da thu; giai doan tac gia toi uu .set CHUA BIET - .set cho XAUUSD/AUDUSD M5)
  7. Kiem dinh boi: 16 o vong 4 -> p mot phia tu lai ngay (t = SR_ngay*sqrt(N)), Holm-Bonferroni + Bonferroni.
Cong KHONG doi. Song = tung kiem 1..6 deu lai sau phi + DD < 80% + khong chay, VA p Holm < 0.05.
"""
from __future__ import annotations

import glob
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
import ger_chay as C                               # noqa: E402
from nhan import ger_ea as G                       # noqa: E402
from nhan import ger_ea_tin_hieu as T              # noqa: E402
import vong_thu_nghiem as V                        # noqa: E402

O_DAT = [("BBRSI", "EURUSD", 60), ("3MACD", "EURUSD", 60)]


def nap(ten):
    d = C.KHO / f"geraked__metatrader5__Experts_{ten}"
    vb = (d / f"{ten}.mq5").read_text(encoding="utf-8", errors="ignore")
    st = Path(sorted(glob.glob(str(d / "*.set")))[0]).read_text(encoding="utf-8", errors="ignore")
    th, _ = G.gop_tham_so(vb, st)
    return vb, th


def chay_o(ten, ma, phut, tk, tep=None, he_spread=1.0, thu_tu="gan_open", cat=None):
    """Tin hieu khung EA, khop tren M5. `cat` = (i0, i1) chi so bar M5 (von moi o dau cat)."""
    vb, th = nap(ten)
    d5 = C.du_lieu(ma, 5, tep)
    if cat:
        d5 = d5.iloc[cat[0]:cat[1]]
    g = d5.resample(f"{phut}min", label="left", closed="left")
    import pandas as pd
    df = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                       "close": g["close"].last()}).dropna() if phut > 5 else d5
    cp = V.mo_hinh_chi_phi(df, ma)
    cp5 = V.mo_hinh_chi_phi(d5, ma)
    if he_spread != 1.0:
        cp5 = cp5.bien_the(spread=cp5.spread_frac_chung * he_spread,
                           truot_gia=cp5.truot_gia_frac * he_spread)
        cp = cp.bien_the(spread=cp.spread_frac_chung * he_spread)
    diem = C.diem_cua(ma)
    s = cp.spread_mang(df.index) * df["open"].to_numpy(float)
    tin, _ = T.TIN_HIEU[ten](df, dict(th), s, diem)
    ts, _ = G.tham_so_tu_ma(vb, dict(th))
    if phut > 5:
        vt = d5.index.searchsorted(df.index)
        tin5 = {k: np.zeros(len(d5), dtype=v.dtype) for k, v in tin.items()}
        ok = vt < len(d5)
        for k in tin:
            tin5[k][vt[ok]] = tin[k][ok]
    else:
        tin5 = tin
    kq = G.chay(d5, tin5, ts, cp5, ma, diem, tk, thu_tu=thu_tu)
    cs = G.chi_so(kq, tk.von)
    cs["giu"] = bool(cs["lai_sau_phi_pct"] > 0 and cs["maxdd_pct"] < 80 and not cs["chay"])
    cs["tu"], cs["den"] = str(d5.index[0])[:10], str(d5.index[-1])[:10]
    return cs, kq


def p_mot_phia(kq) -> tuple[float, float, int]:
    r = kq.duong_von.resample("1D").last().dropna().pct_change().dropna()
    r = r[np.isfinite(r)]
    if len(r) < 10 or r.std() == 0:
        return 1.0, 0.0, len(r)
    t = r.mean() / r.std() * math.sqrt(len(r))
    return 0.5 * math.erfc(t / math.sqrt(2)), float(t), len(r)


def gon(cs):
    return {k: cs.get(k) for k in ("lai_sau_phi_pct", "maxdd_pct", "sharpe", "so_lenh", "so_ro",
                                   "tang_max", "chay", "giu", "tu", "den")}


def main(argv=None) -> int:
    a = list(argv if argv is not None else sys.argv[1:])
    ra = Path(a[a.index("--ra") + 1]) if "--ra" in a else GOC / "reports" / "GER_BEN.json"
    tk = G.TaiKhoan(**{k: v for k, v in V.TAI_KHOAN_MAC_DINH.items()
                       if k in ("von", "don_bay", "stop_out", "lot_max")})
    bang = {"luc": time.strftime("%Y-%m-%d %H:%M:%S"), "nhan": "MO PHONG - kiem do ben GerEA",
            "o": {}}
    # 7. kiem dinh boi tren 16 o vong 4 (o goc, tai khoan mac dinh)
    vong4 = json.loads((GOC / "reports" / "GER_EA.json").read_text(encoding="utf-8"))
    ps = []
    for ten, v in vong4["ea"].items():
        for r in v["lan"]:
            if r.get("tai_khoan") not in (None, "mac_dinh_1:100_so50") or r.get("loi"):
                continue
            _, kq = chay_o(ten, r["ma"], r["khung_phut"], tk)
            p, t, nn = p_mot_phia(kq)
            ps.append({"o": f"{ten} {r['ma']} {r['khung_phut']}p", "p": p, "t": round(t, 2), "ngay": nn})
            print("p", ps[-1], flush=True)
    m = len(ps)
    thu = sorted(range(m), key=lambda i: ps[i]["p"])
    chay_max = 0.0
    for k, i in enumerate(thu):
        chay_max = max(chay_max, min(1.0, (m - k) * ps[i]["p"]))
        ps[i]["p_holm"] = round(chay_max, 4)
        ps[i]["p_bonf"] = round(min(1.0, m * ps[i]["p"]), 4)
        ps[i]["p"] = round(ps[i]["p"], 4)
    bang["kiem_dinh_boi"] = {"so_o": m, "ds": ps}
    for ten, ma, ph in O_DAT:
        o = {}
        goc, kq = chay_o(ten, ma, ph, tk)
        o["goc"] = gon(goc)
        n5 = len(C.du_lieu(ma, 5))
        o["cua_so_6"] = [gon(chay_o(ten, ma, ph, tk, cat=(i * n5 // 6, (i + 1) * n5 // 6))[0])
                         for i in range(6)]
        o["bat_dau_lech_8"] = [gon(chay_o(ten, ma, ph, tk, cat=(i * n5 // 16, n5))[0])
                               for i in range(1, 9)]
        o["thu_tu"] = {tt: gon(chay_o(ten, ma, ph, tk, thu_tu=tt)[0])
                       for tt in ("gan_open", "thap_truoc", "cao_truoc")}
        o["spread_x1.5"] = gon(chay_o(ten, ma, ph, tk, he_spread=1.5)[0])
        o["spread_x1.5_xau_nhat"] = min((gon(chay_o(ten, ma, ph, tk, he_spread=1.5, thu_tu=tt)[0])
                                         for tt in ("thap_truoc", "cao_truoc")),
                                        key=lambda x: x["lai_sau_phi_pct"])
        o["cap_khac"] = {}
        for mk in ("GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD", "XAUUSD"):
            o["cap_khac"][mk] = gon(chay_o(ten, mk, ph, tk)[0])
        o["eurusd_2018_2023"] = gon(chay_o(ten, ma, ph, tk, tep="eurusd_cu_m5_histdata_server.csv")[0])
        ph_ = next(x for x in ps if x["o"] == f"{ten} {ma} {ph}p")
        o["p"] = ph_
        nhom = [o["goc"]] + o["cua_so_6"] + o["bat_dau_lech_8"] + list(o["thu_tu"].values()) + \
            [o["spread_x1.5"], o["spread_x1.5_xau_nhat"], o["eurusd_2018_2023"]] + list(o["cap_khac"].values())
        o["dem_giu"] = f"{sum(x['giu'] for x in nhom)}/{len(nhom)}"
        o["song"] = bool(all(x["giu"] for x in nhom) and ph_["p_holm"] < 0.05)
        bang["o"][f"{ten} {ma} {ph}p"] = o
        print(ten, json.dumps({k: o[k] for k in ("goc", "dem_giu", "song", "p")}, ensure_ascii=False))
        for k in ("cua_so_6", "bat_dau_lech_8"):
            print(" ", k, [(x["lai_sau_phi_pct"], x["maxdd_pct"]) for x in o[k]])
        print("  thu_tu", {k: (v["lai_sau_phi_pct"], v["maxdd_pct"]) for k, v in o["thu_tu"].items()})
        print("  spread1.5", o["spread_x1.5"]["lai_sau_phi_pct"], o["spread_x1.5"]["maxdd_pct"],
              "xau nhat", o["spread_x1.5_xau_nhat"]["lai_sau_phi_pct"], o["spread_x1.5_xau_nhat"]["maxdd_pct"])
        print("  cap", {k: (v["lai_sau_phi_pct"], v["maxdd_pct"]) for k, v in o["cap_khac"].items()})
        print("  2018-2023", o["eurusd_2018_2023"])
    ra.write_text(json.dumps(bang, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("ghi", ra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
