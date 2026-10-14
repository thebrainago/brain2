# -*- coding: utf-8 -*-
"""Vòng 30 — tính chất sóng ZigZag-ATR, luật p70/p90 của Anh, ghép điểm vào (confluence). MÔ PHỎNG.
python v30.py song | tiendk | kiem
"""
import json, sys, itertools
import numpy as np, pandas as pd
from scipy import stats
from nhan.song_zigzag_atr import atr, zigzag, song, tom_tat, PHI_UL, TRUOT_BPS

HD = "/workspace/du_lieu_fx/hd28/"
D1 = "/workspace/du_lieu_ngay/v24/"
TEP_M5 = {"US500": "spxusd_m5_den202610", "US100": "nsxusd_m5_den202610", "GER40": "grxeur_m5_den202610",
          "XAUUSD": "xauusd_m5_histdata_ny7_den202610", "DAU": "bcousd_m5",
          **{p: p.lower() + "_m5_histdata_ny7_den202610" for p in
             ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"]}}
TEP_D1 = {"US500": "iGSPC", "US100": "iNDX", "GER40": "iGDAXI", "XAUUSD": "GC_F", "DAU": "CL_F",
          "EURUSD": "EURUSD_X", "GBPUSD": "GBPUSD_X", "USDJPY": "JPY_X", "USDCHF": "USDCHF_X",
          "AUDUSD": "AUDUSD_X", "NZDUSD": "NZDUSD_X", "USDCAD": "USDCAD_X"}
CAT = {"H1": pd.Timestamp("2025-06-01"), "H4": pd.Timestamp("2025-06-01"), "D1": pd.Timestamp("2015-04-01")}
K_GD = 2.0  # ZigZag dùng để giao dịch (cố định trước)
HO_HOLM_TRUOC = 13000


def nap(ts, khung):
    if khung == "D1":
        d = pd.read_csv(D1 + TEP_D1[ts] + ".csv", parse_dates=["date"]).set_index("date")
        d = d[(d.index >= "2004-01-01") & (d.high >= d.low) & (d.close > 0)].dropna()
        return d[["open", "high", "low", "close"]]
    m = pd.read_csv(HD + TEP_M5[ts] + ".csv", parse_dates=["time"]).set_index("time")
    r = m.resample("1h" if khung == "H1" else "4h", label="left", closed="left").agg(
        dict(open="first", high="max", low="min", close="last")).dropna()
    return r


def lam_song():
    out, md = {}, ["# Tính chất sóng ZigZag-ATR (vòng 30, MÔ PHỎNG)", "",
                   "Dữ liệu: H1/H4 gộp từ HistData M5 BID (2024-01 → 2026-10, giờ server NY+7); D1 Yahoo 2004 → 2026-10.",
                   "Dầu: H1/H4 = Brent (BCOUSD), D1 = WTI hợp đồng liên tục CL_F (có bước nhảy đáo hạn). Vàng D1 = GC_F (cũng vậy).",
                   "Đẩy/hồi: theo MA200 cùng khung tại nến bắt đầu sóng (giá > MA200 → sóng lên là đẩy). Toàn bộ dữ liệu (cả 2 giai đoạn).",
                   "Cột: p50/p70/p90. Biên độ ATR = biên độ / ATR14 tại nến bắt đầu. Tỉ lệ hồi = sóng hồi / sóng đẩy ngay trước.", "",
                   "| Tài sản | Khung | k ATR | n đẩy | Đẩy điểm (p50/p70/p90) | Đẩy % | Đẩy ATR | Đẩy nến | n hồi | Hồi % | Hồi ATR | Hồi nến | Tỉ lệ hồi |",
                   "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda d: f"{d['p50']:.2f} / {d['p70']:.2f} / {d['p90']:.2f}" if d["p50"] is not None else "CHƯA ĐO ĐƯỢC"
    for ts in TEP_M5:
        for kh in ("H1", "H4", "D1"):
            df = nap(ts, kh)
            for k in (1.0, 2.0, 3.0):
                w, _, _ = song(df, k)
                t = tom_tat(w)
                g1 = tom_tat(w[w.t0 < CAT[kh]])
                out[f"{ts}|{kh}|{k}"] = {"toan": t, "gd1": g1, "so_nen": len(df), "tu": str(df.index[0]), "den": str(df.index[-1])}
                md.append(f"| {ts} | {kh} | {k:g} | {t['day']['pct']['n']} | {f(t['day']['diem'])} | {f(t['day']['pct'])} | {f(t['day']['atr'])} | {f(t['day']['nen'])} | "
                          f"{t['hoi']['pct']['n']} | {f(t['hoi']['pct'])} | {f(t['hoi']['atr'])} | {f(t['hoi']['nen'])} | {f(t['ti_le_hoi'])} |")
    json.dump(out, open("reports/tinh_chat_song.json", "w"), ensure_ascii=False, indent=1, default=str)
    open("reports/tinh_chat_song.md", "w").write("\n".join(md) + "\n")


# ---------------- chỉ báo ----------------
def rsi(c, n):
    d = np.diff(c, prepend=c[0]); u = np.clip(d, 0, None); v = np.clip(-d, 0, None)
    au = pd.Series(u).ewm(alpha=1 / n, adjust=False).mean().values
    av = pd.Series(v).ewm(alpha=1 / n, adjust=False).mean().values
    return 100 - 100 / (1 + au / np.where(av == 0, 1e-12, av))


def ung_vien(ts, kh):
    """Mỗi nến t: chân đang chạy so với pivot đã xác nhận gần nhất; tín hiệu ở close t, vào open t+1."""
    df = nap(ts, kh)
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    a = atr(h, l, c); m = pd.Series(c).rolling(200).mean().values
    piv = zigzag(h, l, a, K_GD)
    w, _, _ = song(df, K_GD)
    w1 = w[w.t0 < CAT[kh]]
    if len(w1) < 20:
        return None
    th = dict(d50=np.percentile(w1[w1.loai == "day"].atr, 50), d70=np.percentile(w1[w1.loai == "day"].atr, 70),
              d90=np.percentile(w1[w1.loai == "day"].atr, 90), r50=np.nanpercentile(w1.ti_le_hoi, 50),
              r70=np.nanpercentile(w1.ti_le_hoi, 70), nh90=int(np.percentile(w1[w1.loai == "hoi"].nen, 90)),
              nd90=int(np.percentile(w1[w1.loai == "day"].nen, 90)))
    fee = PHI_UL[ts] + TRUOT_BPS
    r14 = rsi(c, 14); r56 = rsi(c, 56)  # RSI "khung lớn" xấp xỉ = RSI chu kỳ ×4 trên cùng khung
    e12 = pd.Series(c).ewm(span=12, adjust=False).mean(); e26 = pd.Series(c).ewm(span=26, adjust=False).mean()
    mc = (e12 - e26); hist = (mc - mc.ewm(span=9, adjust=False).mean()).values
    a5 = atr(h, l, c, 5); a50 = atr(h, l, c, 50)
    rng = np.where(h - l > 0, h - l, np.nan); ibs = (c - l) / rng
    gio_vao = np.r_[df.index.hour[1:], -1]
    xn = np.array([p["xn"] for p in piv]); n = len(c)
    rows = []
    for t in range(201, n - 1):
        j = np.searchsorted(xn, t, side="right") - 1
        if j < 1 or not np.isfinite(m[t]):
            continue
        P, Q = piv[j], piv[j - 1]
        d = -P["loai"]; xu = 1 if c[P["idx"]] > m[P["idx"]] else -1
        mv = (c[t] - P["gia"]) * d
        if mv <= 0:
            continue
        aP = a[P["idx"]]; mvA = mv / aP
        if d == xu and mvA >= th["d50"]:
            huong, s = "nguoc", -d
            tp = th["r50"] * mv; sl = max(th["d90"] * aP - mv, 0) + 0.5 * a[t]; hold = max(th["nh90"], 2)
        elif d != xu and (Q["gia"] - P["gia"]) * xu < 0:  # Q→P là sóng đẩy theo xu
            imp = abs(P["gia"] - Q["gia"]); rt = mv / imp
            if not (th["r50"] <= rt <= th["r70"]):
                continue
            huong, s = "thuan", xu
            tp = mv; sl = max(imp - mv, 0) + 0.5 * a[t]; hold = max(th["nd90"], 2)
        else:
            continue
        e = o[t + 1]; tpp = e + s * tp; slp = e - s * sl; x = None; mfe = 0.0
        jj = t + 1
        for jj in range(t + 1, min(t + 1 + hold, n)):
            mfe = max(mfe, (h[jj] - e) if s == 1 else (e - l[jj]))
            if (s == 1 and l[jj] <= slp) or (s == -1 and h[jj] >= slp): x = slp; break
            if (s == 1 and h[jj] >= tpp) or (s == -1 and l[jj] <= tpp): x = tpp; break
        if x is None: x = c[jj]
        ra = s * (x - e) / e * 1e4 - fee
        det = dict(
            p70=mvA >= th["d70"], p90=mvA >= th["d90"],
            quet=(-s) * (c[t] - c[max(t - 3, 0)]) >= 3 * a[t],
            pin=(s == 1 and (min(o[t], c[t]) - l[t]) >= 2 / 3 * (h[t] - l[t]) > 0) or
                (s == -1 and (h[t] - max(o[t], c[t])) >= 2 / 3 * (h[t] - l[t]) > 0),
            rsi_dk=(r14[t] < 30 and r56[t] < 40) if s == 1 else (r14[t] > 70 and r56[t] > 60),
            ibs=(ibs[t] < 0.2) if s == 1 else (ibs[t] > 0.8),
            macd=s * (hist[t] - hist[t - 1]) > 0 and s * (hist[t - 1] - hist[t - 2]) < 0,
            nen=a5[t - 1] / a50[t - 1] < 0.75,
            volman=s * (c[t] - (h[t - 3:t].max() if s == 1 else l[t - 3:t].min())) > 0,
            gio=None if kh == "D1" else bool(gio_vao[t] != 0),
            ma200=s * (c[t] - m[t]) > 0)
        rows.append(dict(ts=ts, kh=kh, t=t, tg=df.index[t], ra_i=jj, chan=P["idx"], huong=huong, ret=ra,
                         thang=ra > 0, mfe=mfe / e * 1e4, gd=1 if df.index[t] < CAT[kh] else 2, **det))
    return pd.DataFrame(rows), th


DET = {"nguoc": ["p70", "p90", "quet", "pin", "rsi_dk", "ibs", "macd", "nen", "gio", "ma200"],
       "thuan": ["macd", "volman", "nen", "pin", "rsi_dk", "ibs", "gio", "ma200"]}


def chon_lenh(u, dk):
    """Một lệnh/chân sóng: nến đầu tiên thoả mọi điều kiện; không chồng lệnh cùng tài sản."""
    if len(u) == 0: return u
    mk = np.ones(len(u), bool)
    for x in dk:
        mk &= u[x].fillna(False).astype(bool).values
    v = u[mk].sort_values(["ts", "t"])
    keep, last, seen = [], {}, set()
    for r in v.itertuples():
        key = (r.ts, r.chan)
        if key in seen or r.t + 1 <= last.get(r.ts, -1): continue
        seen.add(key); last[r.ts] = r.ra_i; keep.append(r.Index)
    return v.loc[keep]


def thong_ke(v):
    if len(v) == 0: return dict(n=0)
    r = v.sort_values("tg").ret.values
    w, l = r[r > 0].sum(), -r[r < 0].sum()
    eq = np.cumsum(r) / 100; dd = float(np.max(np.maximum.accumulate(np.r_[0, eq])[1:] - eq)) if len(eq) else 0
    p = float(stats.ttest_1samp(r, 0, alternative="greater").pvalue) if len(r) > 2 else 1.0
    return dict(n=len(r), win=round(100 * (r > 0).mean(), 1), pf=round(w / l, 2) if l > 0 else None,
                tb_bps=round(r.mean(), 2), maxdd_pct=round(dd, 2), mfe_bps=round(v.mfe.mean(), 1), p=p)


def tat_ca_ung_vien():
    us, ths = [], {}
    for ts in TEP_M5:
        for kh in ("H1", "H4", "D1"):
            u, th = ung_vien(ts, kh)
            if u is not None and len(u): us.append(u); ths[f"{ts}|{kh}"] = th
    return pd.concat(us, ignore_index=True), ths


def tiendk():
    U, ths = tat_ca_ung_vien()
    U.to_pickle("/workspace/scratch/v30_ung_vien.pkl")
    bang, ung = {}, []
    for kh in ("H1", "H4", "D1"):
        for hg in ("nguoc", "thuan"):
            u1 = U[(U.kh == kh) & (U.huong == hg) & (U.gd == 1)]
            dets = [x for x in DET[hg] if not (kh == "D1" and x == "gio")]
            base = thong_ke(chon_lenh(u1, []))
            res = {"_goc": base}
            for combo in [(x,) for x in dets] + list(itertools.combinations(dets, 2)):
                s = thong_ke(chon_lenh(u1, combo))
                if s["n"]:
                    s["nang_win"] = round(s["win"] / base["win"], 3) if base.get("win") else None
                    s["nang_tb_bps"] = round(s["tb_bps"] - base["tb_bps"], 2)
                res["+".join(combo)] = s
                if s["n"] >= 30 and (s["pf"] or 0) > 1:
                    ung.append(dict(kh=kh, huong=hg, combo=combo, **s))
            bang[f"{kh}|{hg}"] = res
    chon = {}
    for hg in ("nguoc", "thuan"):
        c = sorted([x for x in ung if x["huong"] == hg], key=lambda x: -x["tb_bps"] * np.sqrt(x["n"]))[:10]
        chon[hg] = [dict(kh=x["kh"], combo=list(x["combo"]), gd1=dict((k, x[k]) for k in ("n", "win", "pf", "tb_bps", "maxdd_pct", "mfe_bps", "p"))) for x in c]
    json.dump(dict(nhan="MO PHONG", nguong_gd1=ths, nang_gd1=bang, chon=chon), open("reports/vong30_gd1.json", "w"),
              ensure_ascii=False, indent=1, default=float)
    md = ["# Vòng 30 — TIỀN ĐĂNG KÝ (sinh tự động từ giai đoạn 1, TRƯỚC khi xem giai đoạn 2). MÔ PHỎNG", "",
          "Giai đoạn 1: H1/H4 trước 2025-06-01, D1 trước 2015-04-01. Ngưỡng sóng (p50/p70/p90, tỉ lệ hồi) chỉ từ GĐ1, ZigZag k=2 ATR.",
          "Phí XM Ultra Low: spread trung vị H1 (bps) + 1 bps trượt khứ hồi; swap 0 (nhóm # DISABLED). Gộp 12 tài sản, một cấu hình chung mỗi khung.",
          "Volume: CHƯA ĐO ĐƯỢC — cột tick_volume HistData chỉ là số nến M1 trong nến M5 (≤5), Yahoo D1 không có; bộ phát hiện volume bị loại.",
          "Chọn: ô GĐ1 có n ≥ 30 và PF > 1, xếp theo tb_bps×√n, tối đa 10 mỗi chiều. Ô kiểm ở GĐ2 (một phía t, lợi nhuận/lệnh > 0).",
          f"Holm cộng dồn: họ trước {HO_HOLM_TRUOC} + 6 ô luật p70/p90 (3 khung × 2) + 3 ô luật thuận gốc + số tổ hợp dưới đây.", "",
          "| # | Chiều | Khung | Tổ hợp | GĐ1 n | win % | PF | bps/lệnh |", "|---|---|---|---|---|---|---|---|"]
    i = 0
    for hg in ("nguoc", "thuan"):
        for x in chon[hg]:
            i += 1; g = x["gd1"]
            md.append(f"| {i} | {hg} | {x['kh']} | {'+'.join(x['combo'])} | {g['n']} | {g['win']} | {g['pf']} | {g['tb_bps']} |")
    open("reports/vong30_tien_dang_ky.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


def kiem():
    U = pd.read_pickle("/workspace/scratch/v30_ung_vien.pkl")
    g = json.load(open("reports/vong30_gd1.json"))
    o = []
    for kh in ("H1", "H4", "D1"):
        for nm, dk in (("LUAT_P70", ["p70"]), ("LUAT_P90", ["p90"])):
            o.append(dict(loai="luat_anh", ten=nm, huong="nguoc", kh=kh, dk=dk))
        o.append(dict(loai="luat_anh", ten="THUAN_GOC_r50_r70", huong="thuan", kh=kh, dk=[]))
    for hg in ("nguoc", "thuan"):
        for x in g["chon"][hg]:
            o.append(dict(loai="to_hop", ten="+".join(x["combo"]), huong=hg, kh=x["kh"], dk=x["combo"]))
    for x in o:
        u = U[(U.kh == x["kh"]) & (U.huong == x["huong"])]
        x["gd1"] = thong_ke(chon_lenh(u[u.gd == 1], x["dk"]))
        x["gd2"] = thong_ke(chon_lenh(u[u.gd == 2], x["dk"]))
        x["theo_tai_san_gd2"] = {ts: thong_ke(chon_lenh(u[(u.gd == 2) & (u.ts == ts)], x["dk"])).get("tb_bps") for ts in TEP_M5}
    m = len(o); N = HO_HOLM_TRUOC + m
    ps = sorted(range(m), key=lambda i: o[i]["gd2"].get("p", 1.0))
    run = 0
    for r, i in enumerate(ps):
        run = max(run, min(1.0, o[i]["gd2"].get("p", 1.0) * (N - r)))
        o[i]["p_holm"] = run
        o[i]["qua_holm"] = run < 0.05
    json.dump(dict(nhan="MO PHONG", ho_holm_truoc=HO_HOLM_TRUOC, ho_holm=N, o=o), open("reports/vong30.json", "w"),
              ensure_ascii=False, indent=1, default=float)
    for x in o:
        print(x["loai"], x["huong"], x["kh"], x["ten"], "GD1", {k: x["gd1"].get(k) for k in ("n", "win", "pf", "tb_bps", "maxdd_pct", "mfe_bps")},
              "GD2", {k: x["gd2"].get(k) for k in ("n", "win", "pf", "tb_bps", "maxdd_pct", "mfe_bps", "p")}, "holm", round(x["p_holm"], 4))


if __name__ == "__main__":
    {"song": lam_song, "tiendk": tiendk, "kiem": kiem}[sys.argv[1]]()
