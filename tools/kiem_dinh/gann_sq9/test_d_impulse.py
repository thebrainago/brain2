# -*- coding: utf-8 -*-
"""
TEST D – Kịch bản scalp của Vanh: sau cú SẬP mạnh, lấy ĐÁY (đã xác nhận) làm neo Sq9.
  Mức trên đáy = mục tiêu HỒI (ngược trend), mức dưới đáy = mục tiêu ĐI TIẾP (thuận trend).
  Đối xứng: sau cú TĂNG mạnh, neo ĐỈNH (mức dưới = hồi, mức trên = đi tiếp).
Sự kiện (không nhìn trước):
  - Cú sập: max(high[p−L..p]) − low[p] ≥ D·ATR14[p], L = 24 nến, D ∈ {3, 5, 8}
  - Đáy xác nhận: pivot (trái 5, phải R ∈ {2,3,5}) -> vào tại close nến p+R;
    hoặc "b1": nến đầu tiên close ≥ đáy + 1 ATR (chưa thủng đáy), đáy = low thấp nhất 24 nến.
Mục tiêu: Sq9 45/90/135/180/270/360° trên & dưới neo; Fib hồi 23.6–78.6% của cú sập, Fib mở rộng 127.2/161.8/200%;
  đối chứng: góc Sq9 lệch ngẫu nhiên ±22.5° (3 lần rút), lưới ATR (neo ± m·ATR, m = 0.25..12) để dựng đường cong P(chạm | khoảng cách).
Đo trong H nến: chạm, chạm "sạch" (mục tiêu hồi: trước khi thủng neo; mục tiêu đi tiếp: trước khi hồi quá 50% cú sập),
  số nến tới chạm, MAE trước khi chạm (×ATR), mục tiêu nào chạm trước (hồi k vs đi tiếp k).
Scalp: vào tại close nến xác nhận; TP = mục tiêu; hồi: SL = neo − k·ATR (k = 0.25/0.5/1); đi tiếp: SL = vào + k·ATR (k = 0.5/1/2);
  hết H nến thì đóng theo close; cùng nến chạm cả TP và SL thì tính SL; trừ spread (vàng 0.3, ES 0.25, ^GSPC 0.5).
"""
import numpy as np, pandas as pd, pickle
from common2 import load as load_daily, atr_rma, sq9

ANG = np.array([45, 90, 135, 180, 270, 360], float)
FIB_R = np.array([0.236, 0.382, 0.5, 0.618, 0.786])
FIB_E = np.array([1.272, 1.618, 2.0])
GRID = np.arange(0.25, 12.01, 0.25)
SPREAD = {"GC=F": 0.3, "ES=F": 0.25, "^GSPC": 0.5}
SL_R = [0.25, 0.5, 1.0]; SL_C = [0.5, 1.0, 2.0]
TF = {"1h": dict(H=[12, 24, 48]), "15m": dict(H=[24, 48, 96]), "5m": dict(H=[72, 144, 288]), "1d": dict(H=[5, 10, 20])}
L, LEFT, R_SHIFT = 24, 5, 3


def load(tk, tf):
    if tf == "1d":
        d = load_daily(tk); per = np.where(d.index < pd.Timestamp("2016-01-01"), "IS", "OOS")
        clus = d.index.to_period("M").astype(str).values
    else:
        f = f"data_{tk.replace('=','').replace('^','')}_{tf}.pkl"
        d = pd.read_pickle(f).dropna(subset=["Open", "High", "Low", "Close"])
        ti = d.index.tz_convert("America/New_York").tz_localize(None)
        per = np.where(ti < ti[len(ti) // 2], "IS", "OOS")
        clus = ti.to_period("W").astype(str).values
    return d, per, clus


def find_events(hi, lo, cl, atr, D, conf):
    n = len(cl); ev = []
    for p in range(max(L, LEFT), n - 1):
        if not np.isfinite(atr[p]): continue
        drop_top = hi[p - L:p + 1].max()
        if drop_top - lo[p] < D * atr[p]: continue
        if conf.startswith("R"):
            R = int(conf[1:])
            if p + R >= n: continue
            w = lo[p - LEFT:p + R + 1]
            if lo[p] <= w.min() and lo[p] < lo[p - LEFT:p].min():
                ev.append((p, p + R, drop_top))
        else:  # b1: đáy = low thấp nhất 24 nến, chờ close ≥ đáy + 1 ATR mà chưa thủng đáy
            if lo[p] > lo[p - L:p].min(): continue
            for t in range(p + 1, min(p + L, n - 1) + 1):
                if lo[t] < lo[p]: break
                if cl[t] >= lo[p] + 1.0 * atr[p]:
                    ev.append((p, t, drop_top)); break
    # loại trùng nến xác nhận
    seen, out = set(), []
    for e in ev:
        if e[1] not in seen: seen.add(e[1]); out.append(e)
    return out


def first_idx(mask):
    return np.where(mask.any(-1), mask.argmax(-1), 10**6)


def run(tk, tf, rng):
    d, per, clus = load(tk, tf)
    H_list = TF[tf]["H"]; Hm = max(H_list); sp = SPREAD[tk]
    h0, l0, c0 = (d[x].values.astype(float) for x in ("High", "Low", "Close"))
    atr = atr_rma(h0, l0, c0); n = len(c0)
    rows, grid_rows = [], []
    for s, sname in ((1, "drop"), (-1, "rally")):
        hi, lo, cl = (h0, l0, c0) if s == 1 else (-l0, -h0, -c0)
        for D in (3, 5, 8):
            for conf in ("R2", "R3", "R5", "b1"):
                for (p, c, top) in find_events(hi, lo, cl, atr, D, conf):
                    if c + Hm >= n: continue
                    A = lo[p]; Areal = s * A; e = cl[c]; a_t = atr[c]; drop = top - A
                    # ---- tập mục tiêu (không gian biến đổi: hồi = phía trên neo) ----
                    T, meta = [], []
                    for side, sg in (("hoi", 1), ("tiep", -1)):
                        lv = s * sq9(Areal, ANG, s * sg)
                        for a, v in zip(ANG, lv): T.append(v); meta.append(("sq9", side, f"{int(a)}°"))
                        for r in range(R_SHIFT):
                            lv = s * sq9(Areal, ANG + rng.uniform(-22.5, 22.5, len(ANG)), s * sg)
                            for a, v in zip(ANG, lv): T.append(v); meta.append(("shift", side, f"{int(a)}°"))
                    for f in FIB_R: T.append(A + f * drop); meta.append(("fib", "hoi", f"{f*100:.1f}%"))
                    for f in FIB_E: T.append(A - (f - 1) * drop); meta.append(("fib", "tiep", f"{f*100:.1f}%"))
                    T = np.array(T, float)
                    G = np.r_[A + GRID * a_t, A - GRID * a_t]
                    # ---- cửa sổ ----
                    w = slice(c + 1, c + 1 + Hm)
                    HI, LO, CL = hi[w], lo[w], cl[w]
                    advD = np.maximum.accumulate(e - LO); advU = np.maximum.accumulate(HI - e)
                    fBrk = first_idx(LO < A); X = A + 0.5 * drop; fX = first_idx(HI >= X)
                    def touch_first(TT):
                        up = TT >= e
                        f_up = first_idx(HI[None, :] >= TT[:, None]); f_dn = first_idx(LO[None, :] <= TT[:, None])
                        return np.where(up, f_up, f_dn), up
                    fT, up = touch_first(T)
                    fG, _ = touch_first(G)
                    grid_rows.append(dict(ticker=tk, tf=tf, dir=sname, D=D, conf=conf, period=per[c], cluster=clus[c],
                                          **{f"g_{H}": (fG < H) for H in H_list}))
                    above = T >= A
                    rec_base = dict(ticker=tk, tf=tf, dir=sname, D=D, conf=conf, period=per[c], cluster=clus[c], c=c,
                                    drop_atr=drop / a_t, entry_atr=(e - A) / a_t)
                    # SL cho scalp
                    slR = {k: A - k * a_t for k in SL_R}; slC = {k: e + k * a_t for k in SL_C}
                    fSLR = {k: first_idx(LO <= v) for k, v in slR.items()}
                    fSLC = {k: first_idx(HI >= v) for k, v in slC.items()}
                    for j, (st, side, lab) in enumerate(meta):
                        f = fT[j]; tv = T[j]
                        rec = dict(rec_base, set=st, side=side, label=lab, dATR=(tv - A) / a_t, pctDrop=(tv - A) / drop,
                                   valid=bool(tv > e + sp) if side == "hoi" else bool(tv < e - sp),
                                   bars=f + 1 if f < 10**6 else np.nan,
                                   MAE=(advD[f] if up[j] else advU[f]) / a_t if f < Hm else np.nan)
                        clean_lim = fBrk if above[j] else fX
                        for H in H_list:
                            rec[f"t_{H}"] = f < H
                            rec[f"cl_{H}"] = (f < H) and (f < clean_lim)
                        # scalp chỉ cho sq9 & fib & shift hợp lệ
                        if rec["valid"]:
                            for H in H_list:
                                if side == "hoi":
                                    for k in SL_R:
                                        risk = e - slR[k]; fs = fSLR[k]
                                        if f < H and f < fs: Rv = (tv - e - sp) / risk
                                        elif fs < H and fs <= f: Rv = -(risk + sp) / risk
                                        else: Rv = (CL[H - 1] - e - sp) / risk
                                        rec[f"R_{H}_{k}"] = Rv
                                else:
                                    for k in SL_C:
                                        risk = k * a_t; fs = fSLC[k]
                                        if f < H and f < fs: Rv = (e - tv - sp) / risk
                                        elif fs < H and fs <= f: Rv = -(risk + sp) / risk
                                        else: Rv = (e - CL[H - 1] - sp) / risk
                                        rec[f"R_{H}_{k}"] = Rv
                        rows.append(rec)
                    # mục tiêu nào chạm trước (sq9 hồi k vs đi tiếp k) – lưu riêng
                    for a_i, a in enumerate(ANG):
                        fu, fd = fT[a_i], fT[(1 + R_SHIFT) * len(ANG) + a_i]   # vị trí 'tiep' sq9
                        for H in H_list:
                            rows[-1 - (len(meta) - 1)].setdefault(f"first_{int(a)}_{H}", None)
                    # (ghi kết quả 'chạm trước' vào bản ghi sq9 'hoi' tương ứng)
                    base_idx = len(rows) - len(meta)
                    for a_i, a in enumerate(ANG):
                        fu = fT[a_i]; fd = fT[(1 + R_SHIFT) * len(ANG) + a_i]
                        for H in H_list:
                            v = "hoi" if (fu < H and fu < fd) else "tiep" if (fd < H and fd < fu) else ("ca_hai" if (fu < H and fu == fd) else "khong")
                            rows[base_idx + a_i][f"first_{H}"] = v
    return pd.DataFrame(rows), pd.DataFrame(grid_rows)


def main():
    rng = np.random.default_rng(9)
    R, G = [], []
    for tf in ("1h", "15m", "5m", "1d"):
        for tk in ("GC=F", "ES=F", "^GSPC"):
            r, g = run(tk, tf, rng); R.append(r); G.append(g)
            print(tf, tk, "sự kiện:", len(g), flush=True)
    R = pd.concat(R, ignore_index=True); G = pd.concat(G, ignore_index=True)
    R.to_pickle("results4/targets.pkl"); G.to_pickle("results4/grid.pkl")
    print("rows", len(R))


if __name__ == "__main__":
    main()
