# -*- coding: utf-8 -*-
"""Vòng 31 (B) — 79 mốc nam châm × 12 tài sản H1 (2024-01 → 2026-10). MÔ PHỎNG.
python v31_moc.py tiendk  -> đo chạm/phản ứng (toàn kỳ), sàng 1.422 ô giao dịch trên GĐ1, ghi tiền đăng ký
python v31_moc.py kiem    -> kiểm GĐ2 các ô đã đăng ký + Holm cộng dồn (tính HẾT ô đã sàng vào họ)"""
import json, sys, itertools
import numpy as np, pandas as pd
from scipy import stats
from nhan.song_zigzag_atr import atr, PHI_UL, TRUOT_BPS
from nhan.moc_nam_cham import moc
from v30 import nap, TEP_M5, thong_ke, chon_lenh, DET

CAT = pd.Timestamp("2025-06-01")
N = 24
BUF = (0.1, 0.25, 0.5)
TPS = (1.0, 2.0)
HO_TRUOC = 13029  # sau vòng 30


def _g(arr, I):
    return arr[np.clip(I, 0, len(arr) - 1)]


def mo_phong(H, L, C, st, e, sd, sl_d, tp_d, fav_from=0):
    """st: chỉ số nến bắt đầu (cột 0); lỗ kiểm từ cột 0, lời từ cột fav_from. Trùng nến → tính lỗ."""
    I = st[:, None] + np.arange(N + 1)[None, :]
    ok = I < len(H)
    hh, ll, cc = _g(H, I), _g(L, I), _g(C, I)
    fav = np.where(sd[:, None] > 0, hh - e[:, None], e[:, None] - ll)
    adv = np.where(sd[:, None] > 0, e[:, None] - ll, hh - e[:, None])
    a_hit = (adv >= sl_d[:, None]) & ok
    f_hit = (fav >= tp_d[:, None]) & ok
    f_hit[:, :fav_from] = False
    ia = np.where(a_hit.any(1), a_hit.argmax(1), 10 ** 6)
    iff = np.where(f_hit.any(1), f_hit.argmax(1), 10 ** 6)
    last = np.minimum(ok.sum(1) - 1, N)
    cl = cc[np.arange(len(st)), last]
    g = np.where(ia <= iff, np.where(ia < 10 ** 6, -sl_d, sd * (cl - e)), tp_d)
    g = np.where((ia == 10 ** 6) & (iff == 10 ** 6), sd * (cl - e), g)
    ra = np.where(ia <= iff, ia, iff); ra = np.where(ra >= 10 ** 6, last, ra)
    mfe = np.where(ok, fav, -np.inf).max(1)
    return g / e * 1e4, st + ra, mfe / e * 1e4


def su_kien(ts):
    df = nap(ts, "H1")
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    a = atr(h, l, c)
    M = moc(df)
    M = M[(M.kb >= 1) & (M.kb < len(c) - 2)].reset_index(drop=True)
    kb = M.kb.values; V = M.gia.values; A = a[kb - 1]
    s = np.sign(c[kb - 1] - V)
    M = M[(s != 0) & (A > 0)].reset_index(drop=True); kb, V, A, s = kb[(s != 0) & (A > 0)], V[(s != 0) & (A > 0)], A[(s != 0) & (A > 0)], s[(s != 0) & (A > 0)]
    I = kb[:, None] + np.arange(N)[None, :]; ok = I < len(c)
    tch = (_g(l, I) <= V[:, None]) & (_g(h, I) >= V[:, None]) & ok
    M["cham"] = tch.any(1); M["s"] = s; M["A"] = A; M["kc_atr"] = np.abs(c[kb - 1] - V) / A
    M["tg"] = df.index[kb]; M["gd"] = np.where(M.tg < CAT, 1, 2); M["ts"] = ts
    t = kb + np.where(tch.any(1), tch.argmax(1), 0)
    M["t"] = t
    T = M[M.cham].index.values
    tt, VV, AA, ss = t[T], V[T], A[T], s[T]
    R = tt[:, None] + np.arange(N + 1)[None, :]; okr = R < len(c)
    hh, ll = _g(h, R), _g(l, R)
    fav = np.where(ss[:, None] > 0, hh - VV[:, None], VV[:, None] - ll) / AA[:, None]
    adv = np.where(ss[:, None] > 0, VV[:, None] - ll, hh - VV[:, None]) / AA[:, None]
    fav[:, 0] = -np.inf; fav[~okr] = -np.inf; adv[~okr] = -np.inf
    ib = np.where((fav >= 1).any(1), (fav >= 1).argmax(1), 999); ix = np.where((adv >= 1).any(1), (adv >= 1).argmax(1), 999)
    M.loc[T, "phan_ung"] = np.where(ib < ix, "bat", np.where(ix < ib, "xuyen", "khong_ro"))
    M.loc[T, "so_nen"] = np.minimum(ib, ix)
    M.loc[T, "bat_max_atr"] = fav.max(1); M.loc[T, "xuyen_max_atr"] = adv.max(1)
    fee = PHI_UL[ts] + TRUOT_BPS
    out = []
    cc = c
    for b in BUF:
        for tp in TPS:
            # FADE
            r, ra, mf = mo_phong(h, l, c, tt, VV.copy(), ss, (b + 0.5) * AA, tp * AA, 1)
            out.append(pd.DataFrame(dict(ts=ts, ten=M.ten.values[T], kieu="FADE", b=b, tp=tp, ret=r - fee, mfe=mf, tg=M.tg.values[T], gd=M.gd.values[T], t=tt, ra_i=ra)))
            # BREAKOUT / RETEST
            Jc = tt[:, None] + np.arange(N)[None, :]
            thru = (ss[:, None] * (_g(cc, Jc) - VV[:, None]) <= -b * AA[:, None]) & (Jc < len(c) - 2)
            has = thru.any(1); cb = tt + thru.argmax(1)
            k = np.where(has)[0]
            if len(k):
                st = cb[k] + 1; e = o[np.clip(st, 0, len(o) - 1)]
                r, ra, mf = mo_phong(h, l, c, st, e, -ss[k], AA[k] * 1.0, tp * AA[k], 0)
                out.append(pd.DataFrame(dict(ts=ts, ten=M.ten.values[T][k], kieu="BREAKOUT", b=b, tp=tp, ret=r - fee, mfe=mf, tg=M.tg.values[T][k], gd=M.gd.values[T][k], t=cb[k], ra_i=ra)))
                Jr = cb[k][:, None] + 1 + np.arange(12)[None, :]
                back = np.where(ss[k][:, None] > 0, _g(h, Jr) >= VV[k][:, None], _g(l, Jr) <= VV[k][:, None]) & (Jr < len(c) - 2)
                hb = back.any(1); jr = cb[k] + 1 + back.argmax(1); kk = np.where(hb)[0]
                if len(kk):
                    ki = k[kk]
                    r, ra, mf = mo_phong(h, l, c, jr[kk], VV[ki].copy(), -ss[ki], (b + 0.5) * AA[ki], tp * AA[ki], 1)
                    out.append(pd.DataFrame(dict(ts=ts, ten=M.ten.values[T][ki], kieu="RETEST", b=b, tp=tp, ret=r - fee, mfe=mf, tg=M.tg.values[T][ki], gd=M.gd.values[T][ki], t=jr[kk], ra_i=ra)))
    return M, pd.concat(out, ignore_index=True)


def tk(r):
    r = r.sort_values("tg"); x = r.ret.values
    if len(x) < 3: return dict(n=int(len(x)))
    w, l = x[x > 0].sum(), -x[x < 0].sum(); eq = np.cumsum(x) / 100
    return dict(n=int(len(x)), win=round(100 * (x > 0).mean(), 1), pf=round(w / l, 3) if l > 0 else None, tb_bps=round(x.mean(), 2),
                maxdd_pct=round(float(np.max(np.maximum.accumulate(np.r_[0, eq])[1:] - eq)), 2), mfe_bps=round(r.mfe.mean(), 1),
                t=round(float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), 2) if x.std() > 0 else 0,
                p=float(stats.ttest_1samp(x, 0, alternative="greater").pvalue))


def tiendk():
    Ms, Ts = [], []
    for ts in TEP_M5:
        M, T = su_kien(ts); Ms.append(M); Ts.append(T); print(ts, len(M), len(T), flush=True)
    M = pd.concat(Ms, ignore_index=True); T = pd.concat(Ts, ignore_index=True)
    M.to_pickle("/workspace/scratch/v31_moc.pkl"); T.to_pickle("/workspace/scratch/v31_lenh.pkl")
    # đặc tính mốc (toàn kỳ, mô tả)
    dt = {}
    for ten, g in M.groupby("ten"):
        c = g[g.cham]
        dt[ten] = dict(so_lan=int(len(g)), p_cham=round(g.cham.mean(), 3), kc_atr_p50=round(g.kc_atr.median(), 2),
                       p_bat=round((c.phan_ung == "bat").mean(), 3), p_xuyen=round((c.phan_ung == "xuyen").mean(), 3),
                       nen_p50=float(c.so_nen[c.so_nen < 999].median()) if len(c) else None,
                       bat_max_atr_p50=round(c.bat_max_atr.median(), 2), xuyen_max_atr_p50=round(c.xuyen_max_atr.median(), 2),
                       theo_tai_san={ts: dict(p_cham=round(gg.cham.mean(), 3), p_bat=round((gg[gg.cham].phan_ung == "bat").mean(), 3))
                                     for ts, gg in g.groupby("ts")})
    # sàng GĐ1
    o = []
    for (ten, kieu, b, tp), g in T.groupby(["ten", "kieu", "b", "tp"]):
        s1 = tk(g[g.gd == 1]); o.append(dict(ten=ten, kieu=kieu, b=b, tp=tp, gd1=s1))
    so_o = len(o)
    ung = [x for x in o if x["gd1"].get("n", 0) >= 100 and (x["gd1"].get("pf") or 0) > 1]
    chon = sorted(ung, key=lambda x: -x["gd1"]["t"])[:20]
    # mốc làm bộ phát hiện cho confluence v30 (H1): mốc của 5 ô chọn đầu
    moc_chon = list(dict.fromkeys([x["ten"] for x in chon]))[:5]
    json.dump(dict(nhan="MO PHONG", dac_tinh_moc=dt, so_o_sang=so_o, o_gd1=o, chon=chon, moc_cho_confluence=moc_chon),
              open("reports/vong31_moc_gd1.json", "w"), ensure_ascii=False, indent=1, default=float)
    L = ["# Vòng 31-B — TIỀN ĐĂNG KÝ mốc nam châm (sinh từ GĐ1 H1 trước 2025-06-01, TRƯỚC khi xem GĐ2). MÔ PHỎNG", "",
         f"79 mốc × 3 kiểu (FADE đánh cản / BREAKOUT / RETEST) × đệm {BUF} ATR × chốt {TPS} ATR = **{so_o} ô đã sàng** — TẤT CẢ tính vào Holm.",
         "Dừng: FADE/RETEST = mốc ∓ (đệm + 0,5) ATR; BREAKOUT = 1 ATR từ giá vào (open nến sau nến đóng xuyên mốc ≥ đệm). Giữ tối đa 24 nến H1. Lệnh giới hạn khớp đúng mốc; nến khớp chạm dừng → lỗ.",
         "ATR = ATR14 H1. Phí XM Ultra Low (spread trung vị + 1 bps). Gộp 12 tài sản.",
         f"Chọn: GĐ1 n ≥ 100, PF > 1, xếp theo t, tối đa 20. Họ Holm cuối = {HO_TRUOC} + {so_o} + 20 ô confluence tối đa = sẽ ghi ở kết quả.",
         f"Mốc dùng cho bộ phát hiện confluence (giá cách mốc ≤ 0,25 ATR): {moc_chon}", "",
         "| # | Mốc | Kiểu | Đệm ATR | Chốt ATR | GĐ1 n | win % | PF | bps/lệnh | t |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(chon, 1):
        g = x["gd1"]; L.append(f"| {i} | {x['ten']} | {x['kieu']} | {x['b']} | {x['tp']} | {g['n']} | {g['win']} | {g['pf']} | {g['tb_bps']} | {g['t']} |")
    # confluence: thêm bộ phát hiện "moc" vào ứng viên H1 của v30
    U = pd.read_pickle("/workspace/scratch/v30_ung_vien.pkl"); U = U[U.kh == "H1"].copy()
    mk = M[M.ten.isin(moc_chon)][["ts", "ngay", "gia", "kb"]]
    gan = np.zeros(len(U), bool)
    for ts, gu in U.groupby("ts"):
        df = nap(ts, "H1"); a = atr(df.high.values, df.low.values, df.close.values); c = df.close.values
        mm = mk[mk.ts == ts]; byday = {k: v for k, v in mm.groupby("ngay")}
        for ii, r in zip(gu.index, gu.itertuples()):
            v = byday.get(df.index[r.t].normalize())
            if v is None: continue
            v = v[v.kb <= r.t]
            if len(v) and np.min(np.abs(c[r.t] - v.gia.values)) <= 0.25 * a[r.t]: gan[U.index.get_loc(ii)] = True
    U["moc"] = gan
    U.to_pickle("/workspace/scratch/v31_ung_vien_h1.pkl")
    cf = []
    for hg in ("nguoc", "thuan"):
        u1 = U[(U.huong == hg) & (U.gd == 1)]
        for combo in [("moc",)] + [("moc", x) for x in DET[hg]]:
            s = thong_ke(chon_lenh(u1, combo))
            if s.get("n", 0) >= 30 and (s.get("pf") or 0) > 1: cf.append(dict(huong=hg, combo=list(combo), gd1=s))
    cf = sorted(cf, key=lambda x: -x["gd1"]["tb_bps"] * np.sqrt(x["gd1"]["n"]))[:6]
    L += ["", "## Confluence (H1, ứng viên v30 + bộ phát hiện `moc`), tối đa 6, cùng tiêu chí n ≥ 30, PF > 1", "",
          "| # | Chiều | Tổ hợp | GĐ1 n | win % | PF | bps/lệnh |", "|---|---|---|---|---|---|---|"]
    for i, x in enumerate(cf, 1):
        g = x["gd1"]; L.append(f"| {i} | {x['huong']} | {'+'.join(x['combo'])} | {g['n']} | {g['win']} | {g['pf']} | {g['tb_bps']} |")
    if not cf: L.append("| — | — | không có ô nào đạt GĐ1 | | | | |")
    so_cf_sang = 2 * (1 + 0) + len(DET["nguoc"]) + len(DET["thuan"])
    L += ["", f"Số ô confluence đã sàng: {so_cf_sang} (tính hết vào Holm). Họ Holm cuối = {HO_TRUOC} + {so_o} + {so_cf_sang} = **{HO_TRUOC + so_o + so_cf_sang}**."]
    g = json.load(open("reports/vong31_moc_gd1.json")); g["confluence_chon"] = cf; g["so_cf_sang"] = so_cf_sang
    json.dump(g, open("reports/vong31_moc_gd1.json", "w"), ensure_ascii=False, indent=1, default=float)
    open("reports/vong31_tien_dang_ky.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def kiem():
    g = json.load(open("reports/vong31_moc_gd1.json"))
    T = pd.read_pickle("/workspace/scratch/v31_lenh.pkl")
    U = pd.read_pickle("/workspace/scratch/v31_ung_vien_h1.pkl")
    HO = HO_TRUOC + g["so_o_sang"] + g["so_cf_sang"]
    o = []
    for x in g["chon"]:
        q = T[(T.ten == x["ten"]) & (T.kieu == x["kieu"]) & (T.b == x["b"]) & (T.tp == x["tp"])]
        o.append(dict(loai="moc", ten=f"{x['ten']} {x['kieu']} đệm {x['b']} chốt {x['tp']}", gd1=tk(q[q.gd == 1]), gd2=tk(q[q.gd == 2]),
                      gd2_theo_tai_san={ts: tk(qq[qq.gd == 2]).get("tb_bps") for ts, qq in q.groupby("ts")}))
    for x in g["confluence_chon"]:
        u = U[U.huong == x["huong"]]
        o.append(dict(loai="confluence", ten=f"{x['huong']} H1 {'+'.join(x['combo'])}", gd1=thong_ke(chon_lenh(u[u.gd == 1], x["combo"])),
                      gd2=thong_ke(chon_lenh(u[u.gd == 2], x["combo"]))))
    ps = sorted(range(len(o)), key=lambda i: o[i]["gd2"].get("p", 1.0)); run = 0
    for r, i in enumerate(ps):
        run = max(run, min(1.0, o[i]["gd2"].get("p", 1.0) * (HO - r))); o[i]["p_holm"] = run; o[i]["qua_holm"] = run < 0.05
    json.dump(dict(nhan="MO PHONG", ho_holm_truoc=HO_TRUOC, ho_holm=HO, o=o), open("reports/vong31_moc.json", "w"), ensure_ascii=False, indent=1, default=float)
    f = lambda s: f"{s.get('n')} / {s.get('win')} / {s.get('pf')} / {s.get('tb_bps')} / {s.get('maxdd_pct')} / {s.get('mfe_bps')}"
    L = ["# Vòng 31-B — KẾT QUẢ mốc nam châm (MÔ PHỎNG)", "", f"Holm cộng dồn {HO_TRUOC} → **{HO}** (gồm toàn bộ {g['so_o_sang']} ô đã sàng + {g['so_cf_sang']} ô confluence).",
         "Mỗi giai đoạn: lệnh / win % / PF / bps/lệnh / maxDD % / MFE TB bps. GĐ1 H1 2024-01 → 2025-05, GĐ2 2025-06 → 2026-10.", "",
         "| Loại | Hệ | GĐ1 | GĐ2 | p GĐ2 | p Holm | Qua? |", "|---|---|---|---|---|---|---|"]
    for x in o:
        L.append(f"| {x['loai']} | {x['ten']} | {f(x['gd1'])} | {f(x['gd2'])} | {x['gd2'].get('p', 1):.3g} | {x['p_holm']:.3g} | {'CÓ' if x['qua_holm'] else 'không'} |")
    dt = g["dac_tinh_moc"]
    L += ["", "## Đặc tính 79 mốc (toàn kỳ, gộp 12 tài sản; chạm trong 24 nến H1 kể từ khi mốc biết; bật/xuyên = đi 1 ATR H1 về phía nào trước)", "",
          "| Mốc | Số lần | P chạm | Khoảng cách p50 (ATR) | P bật | P xuyên | Nến tới khi rõ p50 | Bật max p50 (ATR) | Xuyên max p50 (ATR) |", "|---|---|---|---|---|---|---|---|---|"]
    for k, v in sorted(dt.items(), key=lambda kv: -kv[1]["p_bat"]):
        L.append(f"| {k} | {v['so_lan']} | {v['p_cham']} | {v['kc_atr_p50']} | {v['p_bat']} | {v['p_xuyen']} | {v['nen_p50']} | {v['bat_max_atr_p50']} | {v['xuyen_max_atr_p50']} |")
    open("reports/vong31_moc.md", "w").write("\n".join(L) + "\n")
    for x in o: print(x["loai"], x["ten"], "GD1", f(x["gd1"]), "GD2", f(x["gd2"]), "p", round(x["gd2"].get("p", 1), 4), "holm", round(x["p_holm"], 4))


if __name__ == "__main__":
    {"tiendk": tiendk, "kiem": kiem}[sys.argv[1]]()
