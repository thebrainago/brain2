# -*- coding: utf-8 -*-
"""Kiểm 7 bước phong cách tay trên XAU và US500. Không đặt lệnh thật."""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from vang.ma.chay_hyb_vang import (  # noqa: E402
    dung_dac_trung, diem_S, bonus_data, go, tom_tat, dsr, sharpe_tu_eq,
)
from phong_cach_tay.ma.may import SPEC, P_tay, S_xac_nhan  # noqa: E402

OUT_BAO = ROOT / "phong_cach_tay" / "bao_cao"
OUT_KQ = ROOT / "phong_cach_tay" / "ket_qua"
SHADOW = OUT_KQ / "shadow_phong_cach_tay.csv"

WIN = {
    "Q4-2018": ("2018-09-25", "2019-02-28"),
    "Covid 02-04/2020": ("2020-02-10", "2020-07-31"),
    "2022 H1": ("2021-12-28", "2022-07-31"),
    "2022 08-10": ("2022-08-12", "2022-12-15"),
    "08-10/2023": ("2023-07-25", "2023-12-15"),
    "07-08/2024": ("2024-07-10", "2024-09-30"),
    "02-04/2025": ("2025-02-15", "2025-07-15"),
}

EQ0 = 10000.0


def tai_m1_vn(path: Path) -> pd.DataFrame:
    m = pd.read_csv(path, parse_dates=["time"])
    t = m["time"].dt.tz_localize("Europe/Athens", ambiguous="infer", nonexistent="shift_forward")
    m = m.copy()
    m["time"] = t.dt.tz_convert("Asia/Saigon").dt.tz_localize(None)
    return m


def md_table(df, cols):
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)


def chay_mot(sym: str, raw: pd.DataFrame, d, vp, S0, S1, opt_data, t0_wall):
    sp = SPEC[sym]
    i0 = 400
    i1 = len(d)
    t = d["t"].to_numpy()
    i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
    print(f"[{sym}] IS {i_oos-i0} OOS {i1-i_oos}", flush=True)

    opt0 = np.full((len(d), 6), np.nan)
    P0 = P_tay(sym)
    cfgs = {
        "tay_HYB_AG": (P0, S0, opt0),
        "tay_xac_nhan": (P_tay(sym), S1, opt_data if sym == "XAU" else opt0),
    }
    for ten, kwargs in [
        ("lan_coef10", dict(coef=1.0)),
        ("lan_coef13", dict(coef=1.3)),
        ("lan_G2", dict(G=2.0)),
        ("lan_maxL10", dict(maxL=10)),
    ]:
        cfgs[ten] = (P_tay(sym, **kwargs), S1 if sym == "XAU" else S0, opt_data if sym == "XAU" else opt0)

    hang = []
    eq_luu = {}
    shadow_rows = []

    print(f"[{sym}] compile numba...", flush=True)
    _ = go(d, vp, opt0, S0, P0, i0, min(i0 + 2000, i1))
    print(f"[{sym}] compiled {time.time()-t0_wall:.1f}s", flush=True)

    for ten, (P, S, opt) in cfgs.items():
        print(f"[{sym}] chay {ten}", flush=True)
        r, x = go(d, vp, opt, S, P, i0, i1)
        row = tom_tat(ten, r, eq0=EQ0)
        eq = x["eq"]
        j_oos = i_oos - i0
        if 0 < j_oos < len(eq):
            is_net = float(eq[j_oos - 1] - EQ0)
            oos_net = float(eq[-1] - eq[j_oos - 1])
            peak = EQ0
            is_dd = 0.0
            for v in eq[:j_oos]:
                if v > peak:
                    peak = v
                is_dd = max(is_dd, peak - v)
            peak = eq[j_oos - 1]
            oos_dd = 0.0
            for v in eq[j_oos:]:
                if v > peak:
                    peak = v
                oos_dd = max(oos_dd, peak - v)
        else:
            is_net = row["net"]
            oos_net = 0
            is_dd = row["maxdd"]
            oos_dd = 0
        row["is_net"] = round(is_net, 2)
        row["oos_net"] = round(oos_net, 2)
        row["is_dd"] = round(is_dd, 2)
        row["oos_dd"] = round(oos_dd, 2)
        P2 = P.copy()
        P2[16] = float(P[16]) * 2
        r2, _ = go(d, vp, opt, S, P2, i0, i1)
        row["net_sprx2"] = round(r2["net"], 2)
        row["dd_sprx2"] = round(r2["maxdd"], 2)
        row["dat_sprx2"] = bool(r2["net"] > 0 and r2["maxdd"] / EQ0 < 0.80 and r2["blown"] < 0)
        sr = sharpe_tu_eq(eq, EQ0)
        row["sharpe"] = round(sr, 3)
        row["dsr"] = round(dsr(sr, len(eq), n_trials=len(cfgs) + 11), 3)
        row["sym"] = sym
        hang.append(row)
        eq_luu[ten] = eq
        if ten in ("tay_HYB_AG", "tay_xac_nhan"):
            for k in range(len(x["bo"])):
                t_mo = str(d["t"].iloc[int(x["bo"][k])]) if x["bo"][k] >= 0 else ""
                t_dong = "" if x["bc"][k] < 0 else str(d["t"].iloc[int(x["bc"][k])])
                shadow_rows.append(dict(
                    sym=sym, he=ten, mo=t_mo, dong=t_dong or "con_mo",
                    tang=int(x["blay"][k]), pnl=float(x["bpnl"][k]),
                    worst=float(x["bworst"][k]), lots=float(x["blots"][k]),
                    ghi_chu="chi log, khong dat lenh",
                ))
        print(" ", row, flush=True)

    bang = pd.DataFrame(hang)

    # 11 stress: 2 gap + 2 grind on M1, 7 crash on parquet M15
    print(f"[{sym}] stress...", flush=True)
    stress_rows = []
    t_idx = d["t"].to_numpy()
    eq_b = eq_luu["tay_HYB_AG"]
    i_deep = i0 + int(np.argmin(eq_b))

    def gap(g, i):
        def f(dx):
            for k in ["o", "h", "l", "c", "c5p", "zz_lo"]:
                dx.loc[i:, k] = dx.loc[i:, k] * (1 - g)
        return f

    def grind(tot, days, start="2026-06-01"):
        def f(dx):
            i_s = int(np.searchsorted(t_idx, np.datetime64(start)))
            n = len(dx)
            k = np.zeros(n)
            span = days * 1380
            k[i_s:] = np.minimum(np.arange(n - i_s) / max(span, 1), 1.0)
            fac = np.exp(np.log(1 - tot) * k)
            for kk in ["o", "h", "l", "c", "c5p", "zz_lo"]:
                dx[kk] = dx[kk] * fac
            for kk in ["a5", "a15", "ah1"]:
                dx[kk] = dx[kk] * fac
        return f

    synth = [
        ("gap-10% tai day von", gap(0.10, i_deep)),
        ("gap-20% tai day von", gap(0.20, i_deep)),
        ("grind-20%/60ngay", grind(0.20, 60)),
        ("grind-35%/120ngay", grind(0.35, 120)),
    ]
    mains = [
        ("tay_HYB_AG", cfgs["tay_HYB_AG"]),
        ("tay_xac_nhan", cfgs["tay_xac_nhan"]),
    ]
    for sn, fn in synth:
        d2 = d.copy()
        fn(d2)
        for cn, (P, S, opt) in mains:
            r, _ = go(d2, vp, opt, S, P, i0, i1)
            row = tom_tat(f"{cn}|{sn}", r, eq0=EQ0)
            row["scenario"] = sn
            row["cfg"] = cn
            row["sym"] = sym
            stress_rows.append(row)
            print(f"  stress {cn} {sn} net={row['net']} dd={row['maxdd']} blown={row['blown']}", flush=True)

    pq = sp["pq"]
    if pq.exists():
        m5 = pd.read_parquet(pq).reset_index()
        if "time" not in m5.columns:
            m5 = m5.rename(columns={m5.columns[0]: "time"})
        m5["time"] = pd.to_datetime(m5["time"])
        m15 = (m5.set_index("time").resample("15min")
               .agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna())
        m15["tick_volume"] = 1.0
        m15 = m15.reset_index()
        for wn, (a, b) in WIN.items():
            w = m15[(m15.time >= a) & (m15.time < b)].copy()
            if len(w) < 200:
                stress_rows.append(dict(ten=f"thieu|{wn}", scenario=wn, cfg="—", net=np.nan, ghi="nến không đủ", sym=sym))
                continue
            fsc = float(sp["scale_crash"]) / float(w.close.iloc[0])
            for k in ["open", "high", "low", "close"]:
                w[k] = w[k] * fsc
            dw, vpw = dung_dac_trung(w)
            Sw = diem_S(dw, None)
            optw = np.full((len(dw), 6), np.nan)
            i0w = 50
            for cn in ["tay_HYB_AG", "tay_xac_nhan"]:
                P = P_tay(sym).copy()
                P[14] = 64
                P[44] = 64
                P[49] = 5 * 92
                P[52] = 92
                r, _ = go(dw, vpw, optw, Sw, P, i0w, len(dw))
                row = tom_tat(f"{cn}|{wn}", r, eq0=EQ0)
                row["scenario"] = wn
                row["cfg"] = cn
                row["scale"] = round(fsc, 3)
                row["n_nen"] = len(dw)
                row["sym"] = sym
                stress_rows.append(row)
                print(f"  crash {cn} {wn} net={row['net']} dd={row['maxdd']} blown={row['blown']}", flush=True)

    st = pd.DataFrame(stress_rows)
    return bang, st, shadow_rows, dict(
        n=len(raw), t0=str(raw.time.iloc[0]), t1=str(raw.time.iloc[-1]),
        is_bars=int(i_oos - i0), oos_bars=int(i1 - i_oos),
        spr=sp["spr"], pv=sp["pv"], step=sp["step"],
        scale_crash=sp["scale_crash"],
    )


def main():
    t0 = time.time()
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)
    all_bang = []
    all_st = []
    all_shadow = []
    meta = {}

    # --- XAU ---
    print("nap GOLD M1...", flush=True)
    raw_x = tai_m1_vn(SPEC["XAU"]["m1"])
    print("XAU n", len(raw_x), raw_x.time.iloc[0], raw_x.time.iloc[-1], flush=True)
    dx, vpx = dung_dac_trung(raw_x)
    print("XAU dac trung", len(dx), "a15 med", float(np.nanmedian(dx.a15)), flush=True)
    bonus, opt_data = bonus_data(dx)
    print("XAU bonus!=0", int((bonus != 0).sum()), flush=True)
    S0x = diem_S(dx, None)
    S1x = S_xac_nhan(S0x, bonus)
    bx, stx, shx, meta["XAU"] = chay_mot("XAU", raw_x, dx, vpx, S0x, S1x, opt_data, t0)
    all_bang.append(bx)
    all_st.append(stx)
    all_shadow.extend(shx)

    # --- US500 ---
    print("nap US500 M1...", flush=True)
    raw_s = tai_m1_vn(SPEC["US500"]["m1"])
    print("US500 n", len(raw_s), raw_s.time.iloc[0], raw_s.time.iloc[-1], flush=True)
    ds, vps = dung_dac_trung(raw_s)
    print("US500 dac trung", len(ds), "a15 med", float(np.nanmedian(ds.a15)), flush=True)
    S0s = diem_S(ds, None)
    S1s = S0s  # chưa gắn Fxaurum ES (Part 1 làm scoring data)
    opt0s = np.full((len(ds), 6), np.nan)
    bs, sts, shs, meta["US500"] = chay_mot("US500", raw_s, ds, vps, S0s, S1s, opt0s, t0)
    all_bang.append(bs)
    all_st.append(sts)
    all_shadow.extend(shs)

    bang = pd.concat(all_bang, ignore_index=True)
    st = pd.concat(all_st, ignore_index=True)
    bang.to_csv(OUT_KQ / "is_oos.csv", index=False)
    st.to_csv(OUT_KQ / "stress.csv", index=False)
    if all_shadow:
        pd.DataFrame(all_shadow).to_csv(SHADOW, index=False)
    (OUT_KQ / "meta_chay.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # báo cáo tiếng Việt
    lines = [
        "# Máy phong cách tay — kiểm 7 bước (XAU và US500)",
        "",
        f"Xuất báo cáo: {pd.Timestamp.now(tz='Asia/Saigon')} (giờ Việt Nam, UTC+7).",
        "",
        "Máy: quy tắc tay đo từ lịch sử XM demo (không SL, vào cụm lot nhỏ, DCA khoảng+vùng, hedge cụm đóng nhanh, đóng theo lãi/lỗ tổng) "
        "cộng khối HYB+AG. Vào từ điểm chỉ báo truyền thống (BB M15, râu M5, 2 giờ đầu phiên Mỹ, ATR thấp); "
        "với vàng, tín hiệu Fxaurum chỉ được dùng khi chỉ báo cũng đồng thuận (S≥1). "
        "**Không đặt lệnh thật** (chỉ nhật ký bóng).",
        "",
        "## Quy cách tài khoản cent",
        "",
        "- Không tìm thấy terminal Exness cent (`E:\\exness_cent` không tồn tại, không có process). "
        "Quy cách dùng giả định Exness Standard Cent phổ biến: tiền tệ USC, 100 USC = 1 USD; lot và giá như tài khoản standard; P/L và số dư ×100.",
        "- Vàng: pv=100, bước 0,01, spread 0,20 giá, swap −83,83 / +20,64 USD/lot/đêm (tức ×100 USC).",
        "- US500: pv=1, bước 0,10, spread 0,65 giá, swap −1,24 / +0,17 USD/lot/đêm.",
        "- Vốn khởi điểm 10.000 USD = 1.000.000 USC — đủ vận hành so với kiểu nạp 10k→30k. Đòn bẩy 1:1000 như demo đo được; sàn cent có thể khác.",
        "- Tiêu chí đạt: lãi ròng > 0, max DD < 80% vốn, không cháy (equity ≤ 0).",
        "",
        "- IS: trước 2026-10-01; OOS: từ 2026-10-01 (UTC+7).",
        "- 7 bước: (1) IS/OOS, (2) spread ×2, (3) 11 stress (7 cửa sổ sập lịch sử + 2 gap + 2 grind), (4) lân cận tham số, (5) cháy / lỗ thả nổi vs 80%, (6) Deflated Sharpe, (7) nhật ký bóng.",
        "",
    ]
    for sym in ["XAU", "US500"]:
        m = meta[sym]
        sub = bang[bang["sym"] == sym]
        sts = st[st["sym"] == sym] if "sym" in st.columns else st
        lines += [
            f"## {sym}",
            "",
            f"- Dữ liệu M1 XM {m['t0']} → {m['t1']} (Europe/Athens → UTC+7), {m['n']} nến. IS {m['is_bars']} nến, OOS {m['oos_bars']} nến.",
            f"- Spread {m['spr']}, pv={m['pv']}, bước lot {m['step']}. Cửa sổ sập scale về {m['scale_crash']} (parquet M5, mốc giờ parquet, **không phải** máy chủ XM).",
            "",
            md_table(sub, ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net", "net_sprx2", "dd_sprx2", "sharpe", "dsr", "n_ro", "blown", "dat", "dat_sprx2"]),
            "",
        ]
        song = []
        for cn in ["tay_HYB_AG", "tay_xac_nhan"]:
            ss = sts[sts["cfg"] == cn] if "cfg" in sts.columns else sts
            nsc = len(ss)
            n_ok = int((~ss["blown"].astype(bool) & (ss["dd_pct"] < 80)).sum()) if nsc else 0
            te = float(ss["net"].min()) if nsc else float("nan")
            song.append(f"- {cn}: sống {n_ok}/{nsc} kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất {te:.0f} USD ({te*100:.0f} USC).")
        if not sts.empty:
            cols = [c for c in ["cfg", "scenario", "net", "maxdd", "dd_pct", "maxfl", "blown", "dat", "n_nen"] if c in sts.columns]
            lines.append("### Stress")
            lines.append("")
            lines.append(md_table(sts, cols))
            lines.append("")
            lines.extend(song)
            lines.append("")

    lines += [
        f"Nhật ký bóng: `{SHADOW}` (chỉ ghi, không đặt lệnh).",
        f"Chạy trong {time.time()-t0:.1f} giây.",
        "",
        "US500: chưa gắn tín hiệu data ES/Fxaurum (Part 1); `tay_xac_nhan` trùng `tay_HYB_AG` trên cửa sổ này.",
        "Vàng: OptionsDb chưa cho GEX/max pain, trọng số quyền chọn gần như không có mức thật.",
    ]
    text = "\n".join(lines) + "\n"
    (OUT_BAO / "BAO_CAO_7_BUOC.md").write_text(text, encoding="utf-8")
    # con trỏ sang vang/ và sp500/
    (ROOT / "vang" / "bao_cao").mkdir(parents=True, exist_ok=True)
    (ROOT / "sp500" / "bao_cao").mkdir(parents=True, exist_ok=True)
    (ROOT / "vang" / "bao_cao" / "PHONG_CACH_TAY.md").write_text(
        "Xem báo cáo chung (cả XAU và US500) ở `phong_cach_tay/bao_cao/BAO_CAO_7_BUOC.md` và mã dùng chung `phong_cach_tay/`.\n\n" + text,
        encoding="utf-8",
    )
    (ROOT / "sp500" / "bao_cao" / "PHONG_CACH_TAY.md").write_text(
        "Xem báo cáo chung (cả XAU và US500) ở `phong_cach_tay/bao_cao/BAO_CAO_7_BUOC.md` và mã dùng chung `phong_cach_tay/`.\n\n" + text,
        encoding="utf-8",
    )
    print("XONG", bang.to_string(index=False), flush=True)
    print("dt", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
