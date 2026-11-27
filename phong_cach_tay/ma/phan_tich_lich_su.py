# -*- coding: utf-8 -*-
"""Phân tích lịch sử deal XM (chỉ đọc) — trích phong cách tay của Anh."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DU = ROOT / "du_lieu"
KQ = ROOT / "ket_qua"
BAO = ROOT / "bao_cao"

# MT5
ENTRY_IN, ENTRY_OUT, ENTRY_INOUT, ENTRY_OUT_BY = 0, 1, 2, 3
TYPE_BUY, TYPE_SELL, TYPE_BALANCE = 0, 1, 2
REASON = {0: "client", 1: "mobile", 2: "web", 3: "expert", 4: "SL", 5: "TP", 6: "SO"}
BURST_MS = 2000  # cùng cụm vào/ra


def vn(ts):
    s = pd.to_datetime(ts, unit="s", utc=True)
    return s.dt.tz_convert("Asia/Saigon") if hasattr(s, "dt") else s.tz_convert("Asia/Saigon")


def vn_msc(ms):
    s = pd.to_datetime(ms, unit="ms", utc=True)
    return s.dt.tz_convert("Asia/Saigon") if hasattr(s, "dt") else s.tz_convert("Asia/Saigon")


def q(s):
    s = pd.Series(s).dropna()
    if s.empty:
        return {}
    return dict(n=int(len(s)), med=round(float(s.median()), 4),
                p25=round(float(s.quantile(0.25)), 4), p75=round(float(s.quantile(0.75)), 4),
                mean=round(float(s.mean()), 4), min=round(float(s.min()), 4),
                max=round(float(s.max()), 4))


def main():
    KQ.mkdir(parents=True, exist_ok=True)
    BAO.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(DU / "deals_raw.csv")
    o = pd.read_csv(DU / "orders_raw.csv")
    p = pd.read_csv(DU / "positions_now.csv")

    d["t_vn"] = vn(d["time"])
    d["t_msc"] = vn_msc(d["time_msc"])
    o["t_vn"] = vn(o["time_setup"])
    p["t_vn"] = vn(p["time"])

    bal = d[d["type"] == TYPE_BALANCE].copy()
    tr = d[d["type"].isin([TYPE_BUY, TYPE_SELL])].copy()
    tr["side"] = np.where(tr["type"] == TYPE_BUY, "buy", "sell")
    tr["ly_do"] = tr["reason"].map(REASON).fillna("khac")

    # lệnh có SL/TP
    sl_n = int((o["sl"] > 0).sum())
    tp_n = int((o["tp"] > 0).sum())
    sl_by = o[o["sl"] > 0]["comment"].value_counts().to_dict() if sl_n else {}

    # vị thế đóng: ghép IN/OUT theo position_id
    inn = tr[tr["entry"] == ENTRY_IN]
    out = tr[tr["entry"].isin([ENTRY_OUT, ENTRY_OUT_BY, ENTRY_INOUT])]
    rows = []
    for pid, g in tr.groupby("position_id"):
        g = g.sort_values("time_msc")
        gi = g[g["entry"] == ENTRY_IN]
        go = g[g["entry"].isin([ENTRY_OUT, ENTRY_OUT_BY, ENTRY_INOUT])]
        if gi.empty:
            continue
        sym = gi["symbol"].iloc[0]
        side = gi["side"].iloc[0]
        vol = float(gi["volume"].sum())
        t0 = gi["t_msc"].iloc[0]
        px0 = float((gi["price"] * gi["volume"]).sum() / max(vol, 1e-12))
        if go.empty:
            hold_min = np.nan
            t1 = pd.NaT
            pnl = 0.0
            swap = 0.0
            closed = False
            px1 = np.nan
        else:
            t1 = go["t_msc"].iloc[-1]
            hold_min = (t1 - t0).total_seconds() / 60.0
            pnl = float(g["profit"].sum() + g["swap"].sum() + g["commission"].sum())
            swap = float(g["swap"].sum())
            closed = True
            vout = float(go["volume"].sum())
            px1 = float((go["price"] * go["volume"]).sum() / max(vout, 1e-12))
        rows.append(dict(position_id=int(pid), symbol=sym, side=side, vol=vol,
                         t0=t0, t1=t1, hold_min=hold_min, pnl=pnl, swap=swap,
                         closed=closed, px0=px0, px1=px1, magic=int(gi["magic"].iloc[0]),
                         reason=gi["ly_do"].iloc[0], n_in=len(gi), n_out=len(go)))
    pos = pd.DataFrame(rows)

    # Burst vào (cùng symbol+side, cách nhau < 2s)
    bursts = []
    for (sym, side), g in inn.sort_values("time_msc").groupby(["symbol", "side"]):
        g = g.reset_index(drop=True)
        bid = 0
        last = None
        cur = []
        def flush():
            nonlocal bid, cur
            if not cur:
                return
            cg = pd.DataFrame(cur)
            bursts.append(dict(symbol=sym, side=side, n=len(cg),
                               vol=float(cg.volume.sum()),
                               dt_s=float((cg.time_msc.max() - cg.time_msc.min()) / 1000),
                               t0=str(cg.t_msc.iloc[0]), px=float(cg.price.median())))
            cur = []
            bid += 1
        for _, r in g.iterrows():
            if last is not None and (r.time_msc - last) > BURST_MS:
                flush()
            cur.append(r)
            last = r.time_msc
        flush()
    burst = pd.DataFrame(bursts) if bursts else pd.DataFrame(columns=["symbol","side","n","vol"])

    # Đi bộ tồn kho: DCA / hedge
    dca = []
    hedges = []
    # open inventory: list of (t_msc, px, vol, ticket, side)
    inv = {}  # (sym, side) -> list
    inn_s = inn.sort_values("time_msc")
    out_s = out.sort_values("time_msc")
    # event merge
    ev = pd.concat([
        inn.assign(_k="in"),
        out.assign(_k="out"),
    ]).sort_values("time_msc")

    open_pos = {}  # position_id -> rec

    for _, r in ev.iterrows():
        key = (r.symbol, r.side)
        if r._k == "in":
            # hedge? opposite side already open
            opp = "sell" if r.side == "buy" else "buy"
            opp_list = inv.get((r.symbol, opp), [])
            same = inv.get(key, [])
            if opp_list:
                # khoảng cách giá so với VWAP phía đối
                v = sum(x[2] for x in opp_list)
                mid = sum(x[1] * x[2] for x in opp_list) / max(v, 1e-12)
                age_min = (r.time_msc - min(x[0] for x in opp_list)) / 60000.0
                hedges.append(dict(symbol=r.symbol, side_hedge=r.side, vol=float(r.volume),
                                   px=float(r.price), mid_opp=float(mid),
                                   gap=float(abs(r.price - mid)),
                                   n_opp=len(opp_list), vol_opp=float(v),
                                   age_min=round(float(age_min), 3),
                                   t=str(r.t_msc)))
            if same:
                last_t, last_px = same[-1][0], same[-1][1]
                dt_s = (r.time_msc - last_t) / 1000.0
                if dt_s > BURST_MS / 1000.0:
                    lots_before = sum(x[2] for x in same)
                    dca.append(dict(symbol=r.symbol, side=r.side, vol=float(r.volume),
                                    px=float(r.price), px_truoc=float(last_px),
                                    gap=float(abs(r.price - last_px)),
                                    dt_min=round(float(dt_s / 60.0), 3),
                                    n_truoc=len(same), vol_truoc=float(lots_before),
                                    he_so=round(float(r.volume / max(same[-1][2], 1e-12)), 3),
                                    t=str(r.t_msc)))
            inv.setdefault(key, []).append((int(r.time_msc), float(r.price), float(r.volume), int(r.position_id)))
            open_pos[int(r.position_id)] = key
        else:
            # close / trim
            key2 = open_pos.get(int(r.position_id))
            if key2 is None:
                # OUT side is opposite of the position side
                # buy OUT closes a sell position
                pos_side = "sell" if r.side == "buy" else "buy"
                key2 = (r.symbol, pos_side)
            lst = inv.get(key2, [])
            need = float(r.volume)
            neu = []
            for item in lst:
                if need <= 0:
                    neu.append(item)
                    continue
                if item[2] <= need + 1e-12:
                    need -= item[2]
                else:
                    neu.append((item[0], item[1], item[2] - need, item[3]))
                    need = 0
            inv[key2] = neu

    dca_df = pd.DataFrame(dca) if dca else pd.DataFrame()
    hd_df = pd.DataFrame(hedges) if hedges else pd.DataFrame()

    # Cụm đóng (trim / đóng rổ)
    close_bursts = []
    for sym, g in out.sort_values("time_msc").groupby("symbol"):
        g = g.reset_index(drop=True)
        cur = []
        last = None
        def flushc():
            nonlocal cur
            if not cur:
                return
            cg = pd.DataFrame(cur)
            close_bursts.append(dict(symbol=sym, n=len(cg), vol=float(cg.volume.sum()),
                                     pnl=float(cg.profit.sum() + cg.swap.sum()),
                                     dt_s=float((cg.time_msc.max() - cg.time_msc.min()) / 1000),
                                     t=str(cg.t_msc.iloc[0])))
            cur = []
        for _, r in g.iterrows():
            if last is not None and (r.time_msc - last) > BURST_MS:
                flushc()
            cur.append(r)
            last = r.time_msc
        flushc()
    cb = pd.DataFrame(close_bursts) if close_bursts else pd.DataFrame()

    # Equity (gồm nạp/rút) và PnL giao dịch thuần
    d2 = d.sort_values("time_msc")
    eq = (d2["profit"] + d2["swap"] + d2["commission"] + d2["fee"]).cumsum()
    # demo XM bắt đầu 0 rồi deposit; eq cuối ≈ balance if no open? open floating not in deals
    # Trading pnl only: exclude type=2
    tr_pnl = tr.sort_values("time_msc")
    trade_cum = (tr_pnl["profit"] + tr_pnl["swap"] + tr_pnl["commission"]).cumsum()

    # Balance events
    bal2 = bal.copy()
    bal2["t_vn_str"] = bal2["t_vn"].astype(str)
    nap = bal2[~bal2["comment"].str.contains("DIV-", na=False)][["t_vn_str", "profit", "comment"]]

    # theo symbol
    by_sym = []
    for sym, g in pos.groupby("symbol"):
        gc = g[g.closed]
        by_sym.append(dict(
            symbol=sym, n_pos=int(len(g)), n_dong=int(gc.shape[0]), n_mo=int((~g.closed).sum()),
            vol_tong=round(float(g.vol.sum()), 2),
            pnl=round(float(gc.pnl.sum()), 2),
            wr=round(float((gc.pnl > 0).mean() * 100), 1) if len(gc) else None,
            pf=round(float(gc.loc[gc.pnl > 0, "pnl"].sum() / max(-gc.loc[gc.pnl <= 0, "pnl"].sum(), 1e-9)), 2) if len(gc) else None,
            hold_med=round(float(gc.hold_min.median()), 2) if len(gc) else None,
            lot_med=round(float(g.vol.median()), 3),
            magic0_pct=round(float((g.magic == 0).mean() * 100), 1),
        ))

    # hold buckets
    bins = [0, 5, 30, 240, 1440, 1e12]
    labs = ["<5p", "5-30p", "30p-4h", "4h-1d", ">1d"]
    hold_rows = []
    for sym, g in pos[pos.closed].groupby("symbol"):
        cat = pd.cut(g.hold_min, bins=bins, labels=labs, right=False)
        for lab, h in g.groupby(cat, observed=False):
            hold_rows.append(dict(symbol=sym, bucket=str(lab), n=int(len(h)),
                                  pnl=round(float(h.pnl.sum()), 2),
                                  wr=round(float((h.pnl > 0).mean() * 100), 1) if len(h) else None))

    # giờ vào (VN)
    inn2 = inn.copy()
    inn2["gio"] = inn2["t_vn"].dt.hour
    gio = inn2.groupby(["symbol", "gio"]).size().reset_index(name="n")

    # open now
    p["side"] = np.where(p["type"] == 0, "buy", "sell")
    open_now = (p.groupby(["symbol", "side"])
                .agg(n=("ticket", "count"), vol=("volume", "sum"), pnl=("profit", "sum"),
                     sl=("sl", "max"), tp=("tp", "max"), px=("price_open", "median"))
                .reset_index())

    # max layers same side (from inv walk we can recompute max concurrent)
    # use pos open times
    max_layer = {}
    for sym, g in pos.groupby("symbol"):
        ev2 = []
        for _, r in g.iterrows():
            ev2.append((r.t0, 1, r.side, r.vol))
            if r.closed and pd.notna(r.t1):
                ev2.append((r.t1, -1, r.side, r.vol))
        ev2.sort(key=lambda x: (x[0], -x[1]))
        c = {"buy": 0, "sell": 0}
        mx = {"buy": 0, "sell": 0, "ca_hai": 0}
        for _, sgn, side, _v in ev2:
            c[side] += sgn
            mx[side] = max(mx[side], c[side])
            mx["ca_hai"] = max(mx["ca_hai"], c["buy"] + c["sell"])
        max_layer[sym] = mx

    # equity path for DD including deposits
    # Reconstruct balance curve at deal times (no floating)
    eq_arr = eq.to_numpy()
    # max dd on this realized-equity (underestimates floating DD)
    peak = np.maximum.accumulate(eq_arr)
    dd = peak - eq_arr
    # trading-only
    tc = trade_cum.to_numpy()
    peak_t = np.maximum.accumulate(np.r_[0, tc])
    # align
    dd_tr = (np.maximum.accumulate(tc) - tc)

    outj = dict(
        nguon="XM Global MT5 (C:\\Program Files\\XM Global MT5), tài khoản demo 345930355, trade_mode=0, chỉ đọc history_deals_get/history_orders_get.",
        exness_cent="Không tìm thấy E:\\exness_cent, không có process terminal Exness, không có origin Exness trong MetaQuotes. Không khởi động terminal.",
        thoi_gian=dict(
            deal_dau=str(d["t_vn"].min()),
            deal_cuoi=str(d["t_vn"].max()),
            n_deal=int(len(d)),
            n_deal_giao_dich=int(len(tr)),
            n_order=int(len(o)),
            n_pos_mo=int(len(p)),
        ),
        sl_tp=dict(
            order_sl_gt0=sl_n, order_tp_gt0=tp_n, order_tong=int(len(o)),
            ty_le_sl=round(sl_n / max(len(o), 1) * 100, 3),
            sl_comment=sl_by,
            deal_reason=tr["ly_do"].value_counts().to_dict(),
            ket_luan="Gần như không đặt SL trên lệnh tay (magic=0). 8 lệnh có SL đều comment grokmgr (bot).",
        ),
        magic=tr["magic"].value_counts().to_dict(),
        nap_rut=nap.to_dict(orient="records"),
        nap_rut_tong=round(float(nap["profit"].sum()), 2),
        theo_symbol=by_sym,
        hold=hold_rows,
        lot= {sym: q(g.vol) for sym, g in pos.groupby("symbol")},
        hold_phut={sym: q(g.hold_min) for sym, g in pos[pos.closed].groupby("symbol")},
        pnl_lenh={sym: q(g.pnl) for sym, g in pos[pos.closed].groupby("symbol")},
        burst_vao=dict(
            n_cum=int(len(burst)),
            n_trung_vi={sym: q(g.n) for sym, g in burst.groupby("symbol")} if len(burst) else {},
            ty_le_cum_ge3=round(float((burst.n >= 3).mean() * 100), 1) if len(burst) else None,
            mau=burst.sort_values("n", ascending=False).head(8).to_dict(orient="records") if len(burst) else [],
        ),
        dca=dict(
            n=int(len(dca_df)),
            gap={sym: q(g.gap) for sym, g in dca_df.groupby("symbol")} if len(dca_df) else {},
            dt_min={sym: q(g.dt_min) for sym, g in dca_df.groupby("symbol")} if len(dca_df) else {},
            he_so={sym: q(g.he_so) for sym, g in dca_df.groupby("symbol")} if len(dca_df) else {},
            vol={sym: q(g.vol) for sym, g in dca_df.groupby("symbol")} if len(dca_df) else {},
            n_truoc_max={sym: int(g.n_truoc.max()) for sym, g in dca_df.groupby("symbol")} if len(dca_df) else {},
        ),
        hedge=dict(
            n=int(len(hd_df)),
            gap={sym: q(g.gap) for sym, g in hd_df.groupby("symbol")} if len(hd_df) else {},
            age_min={sym: q(g.age_min) for sym, g in hd_df.groupby("symbol")} if len(hd_df) else {},
            vol={sym: q(g.vol) for sym, g in hd_df.groupby("symbol")} if len(hd_df) else {},
            n_opp={sym: q(g.n_opp) for sym, g in hd_df.groupby("symbol")} if len(hd_df) else {},
        ),
        dong_ro=dict(
            n_cum=int(len(cb)),
            pnl={sym: q(g.pnl) for sym, g in cb.groupby("symbol")} if len(cb) else {},
            n_lenh={sym: q(g.n) for sym, g in cb.groupby("symbol")} if len(cb) else {},
            ty_le_cum_lai=round(float((cb.pnl > 0).mean() * 100), 1) if len(cb) else None,
            # đóng cụm nhiều lệnh cùng lãi → đóng theo tổng P/L
            cum_ge5_lai=int(((cb.n >= 5) & (cb.pnl > 0)).sum()) if len(cb) else 0,
            cum_ge5_lo=int(((cb.n >= 5) & (cb.pnl <= 0)).sum()) if len(cb) else 0,
        ),
        tang_toi_da=max_layer,
        von=dict(
            eq_cuoi_realized=round(float(eq_arr[-1]), 2),
            eq_dinh_realized=round(float(peak.max()), 2),
            maxdd_realized_gom_nap=round(float(dd.max()), 2),
            pnl_giao_dich_thuan=round(float(tc[-1]), 2),
            maxdd_chi_giao_dich=round(float(dd_tr.max()), 2),
            ghi="DD realized trên deal không gồm lỗ thả nổi (lịch sử từng ghi worst open vàng khoảng −52,4k). Tài khoản bị SetCustomBalance nhiều lần (nạp/reset demo).",
        ),
        mo_hien_tai=open_now.to_dict(orient="records"),
        mo_sl_tp=dict(sl_gt0=int((p.sl > 0).sum()), tp_gt0=int((p.tp > 0).sum()), pnl=round(float(p.profit.sum()), 2)),
        gio_vao=gio.to_dict(orient="records"),
    )

    (KQ / "thong_ke_phong_cach.json").write_text(json.dumps(outj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    pos.to_csv(KQ / "vi_the_dong.csv", index=False)
    if len(dca_df):
        dca_df.to_csv(KQ / "dca_lop.csv", index=False)
    if len(hd_df):
        hd_df.to_csv(KQ / "hedge_kich.csv", index=False)
    if len(cb):
        cb.to_csv(KQ / "cum_dong.csv", index=False)
    burst.to_csv(KQ / "cum_vao.csv", index=False)
    print(json.dumps({k: outj[k] for k in ["thoi_gian", "sl_tp", "theo_symbol", "dca", "hedge", "dong_ro", "tang_toi_da", "von", "mo_hien_tai", "mo_sl_tp"]}, ensure_ascii=False, indent=2, default=str))
    print("XONG phan tich", KQ)


if __name__ == "__main__":
    main()
