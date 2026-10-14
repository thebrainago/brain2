# -*- coding: utf-8 -*-
"""Vòng 32 — lưới entry quanh 79 mốc nam châm: offset ±0,1…±2 ATR × 3 kiểu × buy/sell. MÔ PHỎNG.
Phí: XM STANDARD (phi_xm_that.spread_gio_bps_tk, tài khoản 'Standard'): spread theo giờ vào + trượt 0,5×spread mỗi chiều
(phi_xm_that.TRUOT_X_SPREAD) + swap mỗi đêm (kịch bản đầy đủ, ngày swap3 ×3). FX = Standard đo thật; chỉ số/vàng/dầu = ƯỚC
(Ultra Low × tỉ lệ Standard/UltraLow trung vị 7 cặp FX theo giờ).
python v32_luoi_moc.py tiendk | kiem"""
import json, sys
import numpy as np, pandas as pd
from scipy import stats
import phi_xm_that as PX
from nhan.song_zigzag_atr import atr
from nhan.moc_nam_cham import moc
from v30 import nap, TEP_M5
from v31_moc import mo_phong, _g, N

MA_XM = {"US500": "US500Cash#", "US100": "US100Cash#", "GER40": "GER40Cash#", "XAUUSD": "GOLD.i#", "DAU": "OILCash#",
         **{p: p + "#" for p in ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"]}}
OFF = [-2, -1.5, -1, -0.75, -0.5, -0.25, -0.1, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2]
SL, TP = 1.0, 1.5
CAT = pd.Timestamp("2025-06-01")
HO_TRUOC = 14453
WD = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}


def phi(ts, df):
    m = MA_XM[ts]
    sp = np.array([PX.spread_gio_bps_tk(m, g, "Standard")[0] for g in range(24)])
    uoc = PX.spread_gio_bps_tk(m, 12, "Standard")[1]
    s = PX.spec_xm()[PX.ho_so_xm(m, "Standard")[0]]
    sw = {d: PX.swap_dem_tk(m, d, s["gia"], "day_du", "Standard") * 1e4 for d in (1, -1)}
    day = df.index.normalize().values
    chg = np.r_[0, (day[1:] != day[:-1]).astype(int)]
    w3 = WD.get(s["swap3"], 2)
    prevwd = pd.DatetimeIndex(np.r_[day[0], day[:-1]]).dayofweek.values
    trip = chg * (prevwd == w3) * 2
    return sp, sw, np.cumsum(chg) + np.cumsum(trip), uoc


def lenh(ts, chi_gd1):
    df = nap(ts, "H1")
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    a = atr(h, l, c); hr = df.index.hour.values
    sp, sw, dem, uoc = phi(ts, df)
    M = moc(df); M = M[(M.kb >= 1) & (M.kb < len(c) - 2)].reset_index(drop=True)
    gd = np.where(df.index[M.kb.values] < CAT, 1, 2)
    if chi_gd1:
        M = M[gd == 1].reset_index(drop=True); gd = gd[gd == 1]
    kb = M.kb.values; V = M.gia.values; A = a[kb - 1]; ten = M.ten.values
    out = []
    def ghi(kieu, off, idx, st, e, sd, fav_from):
        if len(idx) == 0: return
        r, ra, mf = mo_phong(h, l, c, st, e, sd, SL * A[idx], TP * A[idx], fav_from)
        ra = np.minimum(ra, len(c) - 1)
        cost = 2 * sp[hr[np.minimum(st, len(c) - 1)]] - np.where(sd > 0, sw[1], sw[-1]) * (dem[ra] - dem[np.minimum(st, len(c) - 1)])
        out.append(pd.DataFrame(dict(ts=ts, ten=ten[idx], off=off, kieu=kieu, chieu=np.where(sd > 0, "buy", "sell"), ret=r - cost, mfe=mf,
                                     tg=df.index[kb[idx]], gd=gd[idx])))
    for off in OFF:
        E = V + off * A; s = np.sign(c[kb - 1] - E)
        I = kb[:, None] + np.arange(N)[None, :]; ok = I < len(c) - 2
        tch = (_g(l, I) <= E[:, None]) & (_g(h, I) >= E[:, None]) & ok
        k = np.where(tch.any(1) & (s != 0) & (A > 0))[0]
        t = kb[k] + tch[k].argmax(1)
        ghi("FADE", off, k, t, E[k].copy(), s[k], 1)
        ghi("BREAKOUT", off, k, t, E[k].copy(), -s[k], 1)
        Jc = t[:, None] + np.arange(N)[None, :]
        thru = (s[k][:, None] * (_g(c, Jc) - E[k][:, None]) <= -0.1 * A[k][:, None]) & (Jc < len(c) - 2)
        hb = thru.any(1); cb = t + thru.argmax(1); k2 = np.where(hb)[0]
        Jr = cb[k2][:, None] + 1 + np.arange(12)[None, :]
        back = np.where(s[k][k2][:, None] > 0, _g(h, Jr) >= E[k][k2][:, None], _g(l, Jr) <= E[k][k2][:, None]) & (Jr < len(c) - 2)
        k3 = np.where(back.any(1))[0]
        ki = k[k2][k3]; jr = cb[k2][k3] + 1 + back[k3].argmax(1)
        ghi("RETEST", off, ki, jr, E[ki].copy(), -s[ki], 1)
    return pd.concat(out, ignore_index=True), uoc


def tk(r):
    r = r.sort_values("tg"); x = r.ret.values
    if len(x) < 3: return dict(n=int(len(x)))
    w, l = x[x > 0].sum(), -x[x < 0].sum(); eq = np.cumsum(x) / 100
    sd = x.std(ddof=1)
    return dict(n=int(len(x)), win=round(100 * (x > 0).mean(), 1), pf=round(w / l, 3) if l > 0 else None, tb_bps=round(x.mean(), 2),
                maxdd_pct=round(float(np.max(np.maximum.accumulate(np.r_[0, eq])[1:] - eq)), 2), mfe_bps=round(r.mfe.mean(), 1),
                t=round(float(x.mean() / (sd / np.sqrt(len(x)))), 2) if sd > 0 else 0.0,
                p=float(stats.ttest_1samp(x, 0, alternative="greater").pvalue))


KEY = ["ten", "kieu", "chieu", "off"]


def tiendk():
    T = []; uocs = {}
    for ts in TEP_M5:
        t, u = lenh(ts, True); T.append(t); uocs[ts] = bool(u); print(ts, len(t), flush=True)
    T = pd.concat(T, ignore_index=True)
    T["thang"] = T.ret > 0; T["gw"] = T.ret.clip(lower=0); T["gl"] = (-T.ret).clip(lower=0); T["r2"] = T.ret ** 2
    g = T.groupby(KEY).agg(n=("ret", "size"), s=("ret", "sum"), s2=("r2", "sum"), w=("thang", "sum"), gw=("gw", "sum"), gl=("gl", "sum")).reset_index()
    g["tb"] = g.s / g.n; g["sd"] = np.sqrt(np.maximum(g.s2 / g.n - g.tb ** 2, 1e-12) * g.n / (g.n - 1).clip(lower=1))
    g["t"] = g.tb / (g.sd / np.sqrt(g.n)); g["pf"] = g.gw / g.gl.replace(0, np.nan); g["win"] = 100 * g.w / g.n
    so_o = len(g)
    g = g.sort_values(KEY).reset_index(drop=True)
    g["oi"] = g.off.map({v: i for i, v in enumerate(OFF)})
    look = {(r.ten, r.kieu, r.chieu, r.oi): r for r in g.itertuples()}
    ung = []
    for r in g.itertuples():
        nb = [look.get((r.ten, r.kieu, r.chieu, r.oi + d)) for d in (-1, 1)]
        if any(x is None for x in nb): continue
        grp = [r] + nb
        if all(x.n >= 150 and (x.pf or 0) > 1 for x in grp):
            ung.append(dict(ten=r.ten, kieu=r.kieu, chieu=r.chieu, off=r.off, diem=min(x.t for x in grp),
                            gd1=dict(n=int(r.n), win=round(r.win, 1), pf=round(r.pf, 3), tb_bps=round(r.tb, 2), t=round(r.t, 2)),
                            lan_can=[dict(off=x.off, n=int(x.n), pf=round(x.pf, 3), t=round(x.t, 2)) for x in nb]))
    chon = sorted(ung, key=lambda x: -x["diem"])[:20]
    HO = HO_TRUOC + so_o
    tong = dict(so_o=so_o, o_pf_gt1=int((g.pf > 1).sum()), o_n150_pf_gt1=int(((g.n >= 150) & (g.pf > 1)).sum()), ung_vien_on_dinh=len(ung))
    json.dump(dict(nhan="MO PHONG", phi="XM Standard", uoc_phi=uocs, tong=tong, ho_holm=HO, chon=chon,
                   o=g.drop(columns=["s", "s2", "gw", "gl", "w", "sd"]).to_dict("records")),
              open("reports/vong32_gd1.json", "w"), ensure_ascii=False, default=float)
    L = ["# Vòng 32 — TIỀN ĐĂNG KÝ lưới entry quanh mốc nam châm (sinh từ GĐ1 H1 2024-01 → 2025-05, TRƯỚC khi xem GĐ2). MÔ PHỎNG", "",
         f"79 mốc × offset {OFF} ATR × 3 kiểu (FADE = lệnh giới hạn tại mốc+offset, ngược chiều giá tới; BREAKOUT = lệnh dừng tại đó, cùng chiều giá tới;"
         " RETEST = sau khi đóng xuyên ≥ 0,1 ATR, lệnh giới hạn quay lại mức đó trong 12 nến, cùng chiều phá) × buy/sell.",
         f"Dừng {SL} ATR, chốt {TP} ATR (ATR14 H1), giữ ≤ 24 nến H1; nến khớp chạm dừng → lỗ. Lệnh chờ hiệu lực 24 nến từ khi mốc biết. Gộp 12 tài sản.",
         "Phí **XM Standard**: spread trung vị theo giờ vào + trượt 0,5×spread mỗi chiều + swap qua đêm (đầy đủ, ngày swap3 ×3).",
         f"Standard đo thật: 7 cặp FX. ƯỚC (Ultra Low × tỉ lệ Standard/UL theo giờ): {[k for k, v in uocs.items() if v]}.",
         f"**Số ô đã sàng: {so_o}** (tính HẾT vào Holm) → họ Holm {HO_TRUOC} + {so_o} = **{HO}**.",
         f"GĐ1: ô PF>1: {tong['o_pf_gt1']}; n≥150 & PF>1: {tong['o_n150_pf_gt1']}; ổn định (ô và CẢ HAI offset kề đều n≥150, PF>1): {tong['ung_vien_on_dinh']}.",
         "Chọn: xếp theo t NHỎ NHẤT trong bộ 3 offset kề (bề mặt ổn định), tối đa 20.", "",
         "| # | Mốc | Kiểu | Chiều | Offset ATR | GĐ1 n | win % | PF | bps/lệnh | t | t min 3 offset |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(chon, 1):
        q = x["gd1"]; L.append(f"| {i} | {x['ten']} | {x['kieu']} | {x['chieu']} | {x['off']} | {q['n']} | {q['win']} | {q['pf']} | {q['tb_bps']} | {q['t']} | {round(x['diem'], 2)} |")
    if not chon: L.append("| — | không có ô ổn định nào | | | | | | | | | |")
    open("reports/vong32_tien_dang_ky.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def kiem():
    g = json.load(open("reports/vong32_gd1.json"))
    T = pd.concat([lenh(ts, False)[0] for ts in TEP_M5], ignore_index=True)
    o = []
    for x in g["chon"]:
        q = T[(T.ten == x["ten"]) & (T.kieu == x["kieu"]) & (T.chieu == x["chieu"]) & np.isclose(T.off, x["off"])]
        o.append(dict(ten=f"{x['ten']} {x['kieu']} {x['chieu']} off {x['off']}", gd1=tk(q[q.gd == 1]), gd2=tk(q[q.gd == 2]),
                      gd2_theo_tai_san={ts: tk(qq[qq.gd == 2]).get("tb_bps") for ts, qq in q.groupby("ts")}))
    HO = g["ho_holm"]; ps = sorted(range(len(o)), key=lambda i: o[i]["gd2"].get("p", 1.0)); run = 0
    for r, i in enumerate(ps):
        run = max(run, min(1.0, o[i]["gd2"].get("p", 1.0) * (HO - r))); o[i]["p_holm"] = run; o[i]["qua_holm"] = run < 0.05
    json.dump(dict(nhan="MO PHONG", phi="XM Standard", ho_holm=HO, o=o), open("reports/vong32.json", "w"), ensure_ascii=False, indent=1, default=float)
    f = lambda s: f"{s.get('n')} / {s.get('win')} / {s.get('pf')} / {s.get('tb_bps')} / {s.get('maxdd_pct')} / {s.get('mfe_bps')}"
    L = ["# Vòng 32 — KẾT QUẢ lưới entry quanh mốc (MÔ PHỎNG, phí XM Standard)", "", f"Họ Holm cộng dồn **{HO}**. Mỗi giai đoạn: lệnh / win % / PF / bps/lệnh / maxDD % / MFE TB bps.", "",
         "| Hệ | GĐ1 | GĐ2 | p GĐ2 | p Holm | Qua? |", "|---|---|---|---|---|---|"]
    for x in o:
        L.append(f"| {x['ten']} | {f(x['gd1'])} | {f(x['gd2'])} | {x['gd2'].get('p', 1):.3g} | {x['p_holm']:.3g} | {'CÓ' if x['qua_holm'] else 'không'} |")
    open("reports/vong32.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"tiendk": tiendk, "kiem": kiem}[sys.argv[1]]()
