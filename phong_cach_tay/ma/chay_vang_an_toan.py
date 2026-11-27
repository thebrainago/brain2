# -*- coding: utf-8 -*-
"""Chữa cháy vàng tay_v2: lọc delta15 (không vào ngược), lot nhỏ, trần lỗ thả nổi, tỷ lệ hedge, dừng DCA sau 30p.

Quét cấu hình đạt lãi>0 & DD<80%, rồi kiểm 7 bước. Cũng khuyến nghị lọc US500 theo OOS.
Không đặt lệnh thật. 10.000 USD = 1.000.000 USC.
"""
from __future__ import annotations

import json
import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phong_cach_tay.tin_hieu_data as td  # noqa: E402
from phong_cach_tay.ma.may import SPEC  # noqa: E402
from phong_cach_tay.ma.may_v2 import P_v2  # noqa: E402
from phong_cach_tay.ma.chay_v2 import (  # noqa: E402
    tai_m1_vn, dung_dac_trung, them_rej_dn, diem_S, diem_S_short, bonus_data,
    lap_tin, go, tom_tat, is_oos_row, md_table, gio_phien,
)
from phong_cach_tay.ma.chay_v2_p1 import (  # noqa: E402
    them_to_hop_vang, ms_m1_tu_t_vn, chieu, gan_cum_lich_su, bang_khop, chay_stress,
)
from vang.ma.chay_hyb_vang import dsr, sharpe_tu_eq  # noqa: E402

OUT_BAO = ROOT / "phong_cach_tay" / "bao_cao"
OUT_KQ = ROOT / "phong_cach_tay" / "ket_qua"
EQ0 = 10000.0
WIN = {
    "Q4-2018": ("2018-09-25", "2019-02-28"),
    "Covid 02-04/2020": ("2020-02-10", "2020-07-31"),
    "2022 H1": ("2021-12-28", "2022-07-31"),
    "2022 08-10": ("2022-08-12", "2022-12-15"),
    "08-10/2023": ("2023-07-25", "2023-12-15"),
    "07-08/2024": ("2024-07-10", "2024-09-30"),
    "02-04/2025": ("2025-02-15", "2025-07-15"),
}


def loc_delta15(sig, d15_giu):
    """Vào khi cùng chiều delta15 hoặc delta15 trung tính; không bao giờ ngược."""
    d15 = np.asarray(d15_giu, dtype=np.float64)
    s = np.asarray(sig, dtype=np.float64)
    ok = (d15 == 0) | (d15 == s)
    return np.where((s != 0) & ok, s, 0.0)


def main():
    t0 = time.time()
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)

    print("nap GOLD M1 + P1...", flush=True)
    raw = tai_m1_vn(SPEC["XAU"]["m1"])
    d, _ = dung_dac_trung(raw)
    rej = them_rej_dn(d, raw)
    sl, ss = diem_S(d, None), diem_S_short(d, rej)
    sig0 = lap_tin(d, sl, ss, None, "chi_bao", "lu")
    ms = ms_m1_tu_t_vn(d["t"])
    Fg, _ = td.tao("GC", ms)
    Fg = them_to_hop_vang(Fg)
    Mx = chieu(Fg, ms, ["big30_giu", "delta15_giu", "uu_tien", "union4", "sig_GC"], tre_ms=60_000, giu_phut=15)
    d15 = Mx["delta15_giu"]
    sig_d15 = loc_delta15(sig0, d15)
    print("sig goc", int((sig0 != 0).sum()), "sau loc delta15", int((sig_d15 != 0).sum()),
          "bi chan nguoc", int(((sig0 != 0) & (d15 == -sig0)).sum()), flush=True)

    # ----- phân tích cụm thua + delta15 -----
    kh = gan_cum_lich_su(d, Mx, "GOLD.i#")
    thua = kh[kh.pnl <= 0].copy() if len(kh) else kh
    thang = kh[kh.lai].copy() if len(kh) else kh
    rows_m = []
    if len(kh):
        kh = kh.copy()
        kh["hb"] = pd.cut(kh.hold_min, [0, 5, 30, 240, 1440, 1e12],
                          labels=["<5p", "5-30p", "30p-4h", "4h-1d", ">1d"], right=False)
        for name, h in [
            ("thua_tat_ca", thua),
            ("thua_lot<=0.1", thua[thua.vol <= 0.11]),
            ("thua_tru_25-11", thua[thua.ngay != "2026-11-25"]),
            ("thua_30p-4h", thua[(thua.hold_min >= 30) & (thua.hold_min < 240)]),
            ("thua_30p-4h_tru_25-11", thua[(thua.hold_min >= 30) & (thua.hold_min < 240) & (thua.ngay != "2026-11-25")]),
            ("thang", thang),
            ("nhanh_lai", kh[kh.nhanh & kh.lai]),
        ]:
            if not len(h):
                continue
            rows_m.append(dict(
                nhom=name, n=int(len(h)), pnl=round(float(h.pnl.sum()), 2),
                d15_co=round(float((h.delta15_giu != 0).mean() * 100), 1),
                d15_cung=round(float(h.delta15_giu_cung.mean() * 100), 1),
                d15_nguoc=round(float(h.delta15_giu_nguoc.mean() * 100), 1),
                us=round(float((h.phien == "my_20-07").mean() * 100), 1) if "phien" in h else None,
                hold_med=round(float(h.hold_min.median()), 2),
            ))
        bang_m = pd.DataFrame(rows_m)
        bang_m.to_csv(OUT_KQ / "vang_cum_thua.csv", index=False)
        print("CUM THUA\n", bang_m.to_string(index=False), flush=True)
    else:
        bang_m = pd.DataFrame()

    # ----- quét -----
    i0, i1 = 400, len(d)
    t = d["t"].to_numpy()
    i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
    o, h, l, c = d.o.to_numpy(np.float64), d.h.to_numpy(np.float64), d.l.to_numpy(np.float64), d.c.to_numpy(np.float64)
    roll = d.roll.to_numpy()
    print("compile...", flush=True)
    _ = go(o, h, l, c, roll, sig_d15, P_v2("XAU", L0=0.02, K=3, flcap=0.2, hfrac=0.5, dca_max_bars=30), i0, min(i0 + 3000, i1))
    print("compiled", f"{time.time()-t0:.1f}s", flush=True)

    grid = list(itertools.product(
        [0.01, 0.03, 0.05],  # L0
        [2, 3, 4],            # K
        [10, 20, 40],         # maxL
        [0.15, 0.25, 0.40],   # flcap
        [0.5, 1.0],           # hfrac
    ))
    # rút: K=3 chỉ một phần? 3*3*3*3*2=162 quá nhiều nhưng mỗi run rất nhanh. Chạy hết.
    # thêm đối chứng: không lọc / không trần thời gian trên vài cấu hình lõi sau.

    hang = []
    for L0, K, maxL, flcap, hfrac in grid:
        ten = f"L{L0}_K{K}_m{maxL}_fl{int(flcap*100)}_h{hfrac}"
        P = P_v2("XAU", L0=L0, K=K, maxL=maxL, flcap=flcap, hfrac=hfrac,
                 dca_max_bars=30, hlot=L0, hN=5)
        res, eq, *rest = go(o, h, l, c, roll, sig_d15, P, i0, i1)
        row = tom_tat(ten, res)
        row = is_oos_row(row, res, eq, i0, i_oos, P)
        row.update(L0=L0, K=K, maxL=maxL, flcap=flcap, hfrac=hfrac, dca_max_bars=30, loc="delta15")
        hang.append(row)
        if len(hang) % 30 == 0:
            print(f"  quet {len(hang)}/{len(grid)} last net={row['net']} dd={row['dd_pct']} dat={row['dat']}", flush=True)

    # đối chứng chọn 2 size
    for ten, kw, sig, loc in [
        ("ctrl_lot10_khong_loc", dict(L0=0.10, K=4, maxL=20, flcap=0.0, hfrac=0.0, dca_max_bars=0), sig0, "khong"),
        ("ctrl_lot03_khong_loc", dict(L0=0.03, K=3, maxL=20, flcap=0.25, hfrac=0.5, dca_max_bars=30), sig0, "khong"),
        ("ctrl_lot03_d15_khong_30p", dict(L0=0.03, K=3, maxL=20, flcap=0.25, hfrac=0.5, dca_max_bars=0), sig_d15, "delta15"),
        ("ctrl_lot03_d15_khong_flcap", dict(L0=0.03, K=3, maxL=20, flcap=0.0, hfrac=0.5, dca_max_bars=30), sig_d15, "delta15"),
    ]:
        P = P_v2("XAU", **kw, hlot=kw["L0"])
        res, eq, *_ = go(o, h, l, c, roll, sig, P, i0, i1)
        row = tom_tat(ten, res)
        row = is_oos_row(row, res, eq, i0, i_oos, P)
        row.update(L0=kw["L0"], K=kw["K"], maxL=kw["maxL"], flcap=kw["flcap"], hfrac=kw["hfrac"],
                   dca_max_bars=kw["dca_max_bars"], loc=loc)
        hang.append(row)

    bang = pd.DataFrame(hang)
    bang.to_csv(OUT_KQ / "vang_an_toan_quet.csv", index=False)
    dat = bang[bang.dat == True].copy()
    print("DAT n", len(dat), " /", len(bang), flush=True)
    if len(dat):
        print(dat.sort_values(["dd_pct", "net"], ascending=[True, False]).head(15).to_string(index=False), flush=True)
    else:
        # gần đạt: lãi>0, chưa cháy, DD nhỏ nhất
        gan = bang[(bang.net > 0) & (~bang.blown)].sort_values("dd_pct")
        print("KHONG DAT. Gan nhat lai>0:\n", gan.head(10).to_string(index=False), flush=True)

    # ----- 7 bước trên các cấu hình đạt (tối đa 8, ưu tiên DD thấp + OOS>0) -----
    if len(dat):
        chon = dat.copy()
        # ưu tiên OOS>0, IS không cháy, DD thấp, lãi OOS
        chon["uu"] = (chon.oos_net > 0).astype(int) * 2 + (chon.is_net > 0).astype(int) + (chon.net / (1 + chon.maxdd))
        chon = chon.sort_values(["dd_pct", "uu"], ascending=[True, False]).head(8)
    else:
        chon = bang[(bang.net > 0) & (~bang.blown)].sort_values("dd_pct").head(5)
        if chon.empty:
            chon = bang[~bang.blown].sort_values("dd_pct").head(3)

    print("7 buoc tren", list(chon.ten), flush=True)
    day_du = []
    eq_luu = {}
    cfgs = {}
    shadow = []
    for _, r in chon.iterrows():
        ten = r.ten
        if ten.startswith("ctrl_"):
            kw = dict(L0=float(r.L0), K=int(r.K), maxL=int(r.maxL), flcap=float(r.flcap),
                      hfrac=float(r.hfrac), dca_max_bars=int(r.dca_max_bars), hlot=float(r.L0))
            sig = sig0 if r.loc == "khong" else sig_d15
        else:
            # parse L0_K_m_fl_h
            kw = dict(L0=float(r.L0), K=int(r.K), maxL=int(r.maxL), flcap=float(r.flcap),
                      hfrac=float(r.hfrac), dca_max_bars=30, hlot=float(r.L0))
            sig = sig_d15
        P = P_v2("XAU", **kw)
        res, eq, bo, bc, bpnl, bworst, blots = go(o, h, l, c, roll, sig, P, i0, i1)
        row = tom_tat(ten, res)
        row = is_oos_row(row, res, eq, i0, i_oos, P)
        P2 = P.copy(); P2[10] = float(P[10]) * 2
        res2, *_ = go(o, h, l, c, roll, sig, P2, i0, i1)
        row["net_sprx2"] = round(float(res2[0]), 2)
        row["dd_sprx2"] = round(float(res2[1]), 2)
        row["dat_sprx2"] = bool(res2[0] > 0 and res2[1] / EQ0 < 0.80 and res2[10] < 0)
        sr = sharpe_tu_eq(eq, EQ0)
        row["sharpe"] = round(sr, 3)
        row["dsr"] = round(dsr(sr, len(eq), n_trials=len(chon) + 11), 3)
        row["sym"] = "XAU"
        for k in ["L0", "K", "maxL", "flcap", "hfrac"]:
            row[k] = r[k]
        day_du.append(row)
        eq_luu[ten] = eq
        cfgs[ten] = (P, sig)
        if len(shadow) < 4000:
            for k in range(len(bo)):
                shadow.append(dict(he=ten,
                                   mo=str(d.t.iloc[int(bo[k])]) if bo[k] >= 0 else "",
                                   dong="" if bc[k] < 0 else str(d.t.iloc[int(bc[k])]),
                                   pnl=float(bpnl[k]), worst=float(bworst[k]), lots=float(blots[k]),
                                   ghi_chu="chi log, khong dat lenh"))
        print(" 7buoc", row, flush=True)

    bang7 = pd.DataFrame(day_du)
    bang7.to_csv(OUT_KQ / "vang_an_toan_is_oos.csv", index=False)

    # stress on up to 4 best (dat_sprx2 ưu tiên, rồi dat, rồi dd)
    mains = list(bang7.sort_values(
        by=["dat_sprx2", "dat", "dd_pct", "oos_net"],
        ascending=[False, False, True, False],
    ).ten.head(4))
    i_deep = i0 + int(np.argmin(eq_luu[mains[0]]))
    print("stress", mains, flush=True)
    st_rows = chay_stress("XAU", d, roll, o, h, l, c, t, i0, i1, i_deep, cfgs, mains)
    pq = SPEC["XAU"]["pq"]
    if pq.exists():
        m5 = pd.read_parquet(pq).reset_index()
        if "time" not in m5.columns:
            m5 = m5.rename(columns={m5.columns[0]: "time"})
        m5["time"] = pd.to_datetime(m5["time"])
        m5["tick_volume"] = 1.0
        for wn, (a, b) in WIN.items():
            w = m5[(m5.time >= a) & (m5.time < b)].copy()
            if len(w) < 200:
                st_rows.append(dict(ten=f"thieu|{wn}", scenario=wn, cfg="—", net=np.nan, sym="XAU"))
                continue
            fsc = 4000.0 / float(w.close.iloc[0])
            for k in ["open", "high", "low", "close"]:
                w[k] *= fsc
            dw, _ = dung_dac_trung(w)
            rdn = them_rej_dn(dw, w)
            sigw = lap_tin(dw, diem_S(dw, None), diem_S_short(dw, rdn), None, "chi_bao", "lu")
            # không có delta15 lịch sử — lọc = trung tính (giữ sigw)
            i0w = 50
            for cn in mains:
                Pw, _ = cfgs[cn]
                rw, *_ = go(dw.o.to_numpy(np.float64), dw.h.to_numpy(np.float64),
                            dw.l.to_numpy(np.float64), dw.c.to_numpy(np.float64),
                            dw.roll.to_numpy(), sigw, Pw, i0w, len(dw))
                row = tom_tat(f"{cn}|{wn}", rw)
                row.update(scenario=wn, cfg=cn, scale=round(fsc, 3), n_nen=len(dw), sym="XAU")
                st_rows.append(row)
                print(f"  crash {cn} {wn} net={row['net']} dd={row['maxdd']} blown={row['blown']}", flush=True)
    st = pd.DataFrame(st_rows)
    st.to_csv(OUT_KQ / "vang_an_toan_stress.csv", index=False)
    if shadow:
        pd.DataFrame(shadow).to_csv(OUT_KQ / "shadow_vang_an_toan.csv", index=False)

    # US500 khuyến nghị từ v2_p1
    us_md = ""
    p1 = OUT_KQ / "v2_p1_is_oos.csv"
    if p1.exists():
        u = pd.read_csv(p1)
        u = u[(u.sym == "US500") & (u.ten.isin(["p1_uu_tien", "p1_union_es"]))]
        us_md = md_table(u, [c for c in ["ten", "net", "maxdd", "dd_pct", "is_net", "oos_net", "is_dd", "oos_dd",
                                          "net_sprx2", "dd_sprx2", "sharpe", "dat", "dat_sprx2"] if c in u.columns])
        rec = "p1_union_es"
        # ổn định OOS: cả IS và OOS lãi, DD OOS thấp hơn, chênh IS/OOS không quá lệch, spread×2 đạt
        if len(u) == 2:
            a = u[u.ten == "p1_union_es"].iloc[0]
            b = u[u.ten == "p1_uu_tien"].iloc[0]
            # điểm ổn định
            def stab(r):
                sc = 0
                if r.oos_net > 0: sc += 2
                if r.is_net > 0: sc += 1
                if r.get("dat_sprx2", False): sc += 1
                # phạt DD OOS và độ lệch
                sc -= r.oos_dd / 1000.0
                # phạt nếu OOS >> IS (phụ thuộc nửa sau)
                if r.is_net > 0:
                    sc -= max(0, r.oos_net / max(r.is_net, 1) - 3) * 0.2
                sc -= r.dd_pct / 100
                return sc
            rec = "p1_union_es" if stab(a) >= stab(b) else "p1_uu_tien"
            us_md += f"\n\n**Khuyến nghị mặc định US500: `{rec}`.** union_es: lãi {a.net}, DD {a.dd_pct}%, IS {a.is_net} / OOS {a.oos_net}, OOS DD {a.oos_dd}, spread×2 {a.net_sprx2}. uu_tien: lãi {b.net}, DD {b.dd_pct}%, IS {b.is_net} / OOS {b.oos_net}, OOS DD {b.oos_dd}, spread×2 {b.net_sprx2}."

    # báo cáo
    n_dat = int((bang.dat == True).sum())
    lines = [
        "# Vàng tay_v2 — chữa cháy (lọc delta15, lot nhỏ, trần lỗ thả nổi)",
        "",
        f"Xuất: {pd.Timestamp.now(tz='Asia/Saigon')} (giờ Việt Nam, UTC+7).",
        "",
        "Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC.",
        "",
        "## Cụm lỗ vàng của Anh — cái gì khác?",
        "",
        "82 lệnh lỗ, tổng −31.117. **86,7% số lỗ** nằm ở giữ 30 phút–4 giờ (53 lệnh, −26.965). Phiên Mỹ 20–07 VN chiếm −30.799 (68 lệnh). "
        "25/11 một mình −26.867 (50 lệnh, trong đó lot ≥1: −20.133). Loại 25/11, lệnh 30p–4h lỗ chỉ còn −318 (12 lệnh). Lot ≤0,10: 62 lệnh lỗ −10.898 (không kể 25/11: 32 lệnh, −4.251), tập trung giờ 22 VN (−8.452).",
        "",
        "Khung tin điển hình (19:15–20:45 và 01:00–02:15 VN, kiểu NFP/CPI/FOMC): **0 lệnh lỗ**, lãi dương — không có cơ sở cấm giờ tin từ sổ này (không có lịch tin riêng).",
        "",
    ]
    if not bang_m.empty:
        lines += [md_table(bang_m, list(bang_m.columns)), ""]
    lines += [
        "Luật tránh đưa vào máy: (1) không vào ngược delta15; (2) dừng DCA mới sau 30 phút (vùng 30p–4h là nơi Anh lỗ); (3) trần lỗ thả nổi theo % equity — chỉ ngừng DCA, không SL cứng; (4) lot 0,01–0,05, K 2–4, trần tầng 10–40, hedge 0,5–1× lot chính.",
        "",
        f"## Quét {len(grid)} cấu hình (lọc delta15, dừng DCA 30 nến)",
        "",
        f"L0 ∈ {{0,01, 0,03, 0,05}}, K ∈ {{2,3,4}}, maxL ∈ {{10,20,40}}, flcap ∈ {{15%, 25%, 40%}}, hfrac ∈ {{0,5, 1,0}}. "
        f"**Đạt (lãi>0, DD<80%, không cháy) trên Jun–Nov: {n_dat}/{len(bang)}** (kể cả đối chứng).",
        "",
    ]
    if n_dat:
        show = dat.sort_values(["dd_pct", "net"], ascending=[True, False]).head(20)
        cols = [c for c in ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net", "blown", "dat", "L0", "K", "maxL", "flcap", "hfrac"] if c in show.columns]
        lines += [md_table(show, cols), ""]
    if n_dat == 0:
        gan = bang[(bang.net > 0) & (~bang.blown)].sort_values("dd_pct").head(10)
        if len(gan):
            lines += ["Không có cấu hình đạt. Gần nhất (lãi>0, chưa cháy):", "",
                      md_table(gan, [c for c in ["ten", "net", "maxdd", "dd_pct", "is_net", "oos_net", "L0", "K", "maxL", "flcap", "hfrac"] if c in gan.columns]), ""]

    lines += [
        "## Kiểm 7 bước (cấu hình chọn)",
        "",
        md_table(bang7, [c for c in ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net",
                                      "net_sprx2", "dd_sprx2", "sharpe", "dsr", "n_en", "blown", "dat", "dat_sprx2",
                                      "L0", "K", "maxL", "flcap", "hfrac"] if c in bang7.columns]),
        "",
    ]
    if not st.empty:
        cols = [c for c in ["cfg", "scenario", "net", "maxdd", "dd_pct", "blown", "dat", "n_nen"] if c in st.columns]
        lines += [md_table(st, cols), ""]
        for cn in mains:
            ss = st[st.cfg == cn] if "cfg" in st.columns else st
            n_ok = int((~ss.blown.astype(bool) & (ss.dd_pct < 80)).sum()) if len(ss) else 0
            te = float(ss.net.min()) if len(ss) else float("nan")
            lines.append(f"- {cn}: sống {n_ok}/{len(ss)} (không cháy, DD<80%). Tệ nhất {te:.0f} USD ({te*100:.0f} USC).")
        lines.append("")
        lines.append("Cửa sổ sập M5 parquet không có delta15 lịch sử — lọc còn 'trung tính' (giữ tín hiệu chỉ báo).")
        lines.append("")

    lines += ["## US500: chọn lọc mặc định (OOS)", "", us_md or "(không có v2_p1_is_oos.csv)", "",
              f"Chạy {time.time()-t0:.1f} giây. Nhật ký bóng: `ket_qua/shadow_vang_an_toan.csv`."]
    (OUT_BAO / "BAO_CAO_VANG_AN_TOAN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("XONG", bang7.to_string(index=False) if len(bang7) else "no 7step", flush=True)
    print("dt", time.time() - t0, "n_dat", n_dat, flush=True)


if __name__ == "__main__":
    main()
