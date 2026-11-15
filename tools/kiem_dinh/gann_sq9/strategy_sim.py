# Mô phỏng nhanh gann_sq9_strategy.pine (mặc định: SL 1×ATR dưới/trên mức, TP = mức Sq9 kế tiếp,
# vào lệnh ở open nến sau, nếu cùng nến chạm cả SL và TP thì tính SL trước – bảo thủ).
# So sánh góc Sq9 (45°..360°) với chế độ đối chứng lệch −22.5°. Phí 0.01%/chiều.
import numpy as np, pandas as pd, sys
sys.path.insert(0, ".")
from sq9_stats import anchor_events, atr_rma, sq9, ANGLES

def run(df, events, shift, life=20, tolm=0.2, sl_atr=1.0, fee=0.0001, same_bar=False):
    o, h, l, c = (df[x].values.astype(float) for x in ("Open", "High", "Low", "Close"))
    atr = atr_rma(h, l, c, 14); n = len(c); trades = []
    evb = {t: a for t, a in events}; starts = sorted(evb)
    pos = 0; i = 0; si = -1; levels = ladder = used = None; setbar = None
    for t in range(1, n - 1):
        if t in evb:
            a = evb[t]; setbar = t
            lv = [x for ang in ANGLES + shift for s in (1, -1) for x in [float(sq9(a, ang, s))] if np.isfinite(x)]
            levels = sorted(lv); ladder = sorted(lv + [a]); used = [False] * len(levels)
            if not same_bar: continue
        if pos != 0:
            # quản lý lệnh trên nến t
            if pos == 1:
                if l[t] <= sl: trades.append(sl / ep - 1 - 2 * fee); pos = 0
                elif h[t] >= tp: trades.append(tp / ep - 1 - 2 * fee); pos = 0
            else:
                if h[t] >= sl: trades.append(1 - sl / ep - 2 * fee); pos = 0
                elif l[t] <= tp: trades.append(1 - tp / ep - 2 * fee); pos = 0
            continue
        if setbar is None or t - setbar > life or not np.isfinite(atr[t]): continue
        tol = tolm * atr[t]; best = None
        for k, L in enumerate(levels):
            if used[k]: continue
            if c[t-1] >= L and l[t] <= L + tol and c[t] > L and c[t] > o[t]: sig = 1
            elif c[t-1] <= L and h[t] >= L - tol and c[t] < L and c[t] < o[t]: sig = -1
            else: continue
            if best is None or abs(c[t] - L) < abs(c[t] - best[1]): best = (sig, L, k)
        if best is None: continue
        sig, L, k = best
        if sig == 1:
            s_ = L - sl_atr * atr[t]; up = [x for x in ladder if x > c[t]]; tp_ = up[0] if up else c[t] + 2 * atr[t]
        else:
            s_ = L + sl_atr * atr[t]; dn = [x for x in ladder if x < c[t]]; tp_ = dn[-1] if dn else c[t] - 2 * atr[t]
        ep = o[t + 1]
        if (sig == 1 and not (s_ < ep < tp_)) or (sig == -1 and not (tp_ < ep < s_)): continue
        used[k] = True; pos, sl, tp = sig, s_, tp_
    r = np.array(trades)
    if len(r) == 0: return dict(trades=0)
    return dict(trades=len(r), win=100 * (r > 0).mean(), avg_bp=1e4 * r.mean(),
                pf=r[r > 0].sum() / -r[r < 0].sum() if (r < 0).any() else np.inf, total=100 * r.sum())

rows = []
for tk, iv, intra, fut in [("GC=F", "1h", 1, 1), ("ES=F", "1h", 1, 1), ("^GSPC", "1h", 1, 0), ("GC=F", "1d", 0, 1), ("^GSPC", "1d", 0, 0)]:
    df = pd.read_pickle(f"data_{tk.replace('=','').replace('^','')}_{iv}.pkl").dropna(subset=["Open","High","Low","Close"])
    if not intra: df = df[df.index >= "2000-01-01"]
    for kind in ("pdc", "swh", "swl"):
        ev = anchor_events(df, kind, intra, fut=fut)
        for name, sh in (("sq9", 0.0), ("control-22.5", -22.5)):
            rows.append(dict(ticker=tk, tf=iv, anchor=kind, levels=name, **run(df, ev, sh, same_bar=(kind == 'pdc'))))
R = pd.DataFrame(rows).round(2); R.to_csv("results/strategy_sim.csv", index=False); print(R.to_string(index=False))
