# -*- coding: utf-8 -*-
"""
TEST 6 – PHẦN 2: CHART PHI CHUẨN (Heikin Ashi, Renko, Point & Figure, Three Line Break, Kagi).
Nguyên tắc chống ảo:
  * Nến/brick/cột chỉ được biết khi đã HOÀN THÀNH ở giá đóng cửa nến thật t (dựng từ close – không dùng H/L trong nến
    để tránh mơ hồ thứ tự).
  * Tín hiệu ở close t -> khớp ở OPEN THẬT của nến t+1 (bản "thật").
  * Bản "ảo" (naive) dùng cùng tín hiệu nhưng khớp ở giá HA close / giá brick tại t (kiểu backtest quảng cáo) để đo độ ảo.
  * Phí: spread (vàng 0.3, ES 0.25, ^GSPC 0.5 điểm), trả 1/2 spread mỗi lần đổi 1 đơn vị vị thế.
IS/OOS: daily tách 2016, intraday chia đôi. Chọn tham số tốt nhất trên IS (Sharpe ròng), đánh giá OOS.
Đối chứng: Donchian, EMA cross, Buy&Hold trên nến thường; block-bootstrap OOS (khối 20 nến) cho cấu hình đã chọn.
"""
import sys, os, numpy as np, pandas as pd
from multiprocessing import Pool
from common6 import load_tf, SPREAD, atr_rma

N_BOOT = int(os.environ.get("N_BOOT", 200)); BLOCK = 20


# ===================== DỰNG CHART =====================
def heikin(o, h, l, c):
    hc = (o + h + l + c) / 4; ho = np.empty_like(c); ho[0] = (o[0] + c[0]) / 2
    for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    return ho, np.maximum(h, np.maximum(ho, hc)), np.minimum(l, np.minimum(ho, hc)), hc


def renko(c, box, logmode):
    """box: mảng theo nến (động) hoặc hằng (log). Trả: run-length có dấu (+k = k brick tăng liên tiếp) tại mỗi nến,
    và giá brick cuối (giá 'ảo')."""
    x = np.log(c) if logmode else c
    n = len(c); run = np.zeros(n, int); F = np.empty(n)
    Lv = x[0]; d = 0; r = 0
    for t in range(n):
        b = box if logmode else box[t]
        if not np.isfinite(b) or b <= 0: run[t] = r; F[t] = Lv; continue
        if d >= 0 and x[t] >= Lv + b:
            k = int((x[t] - Lv) // b); Lv += k * b; r = r + k if d == 1 else k; d = 1
        elif d <= 0 and x[t] <= Lv - b:
            k = int((Lv - x[t]) // b); Lv -= k * b; r = r - k if d == -1 else -k; d = -1
        elif d == 1 and x[t] <= Lv - 2 * b:
            k = int((Lv - b - x[t]) // b); Lv = Lv - b - k * b; r = -k; d = -1
        elif d == -1 and x[t] >= Lv + 2 * b:
            k = int((x[t] - Lv - b) // b); Lv = Lv + b + k * b; r = k; d = 1
        run[t] = r; F[t] = Lv
    return run, (np.exp(F) if logmode else F)


def pnf(c, box):
    """PnF theo close, box log hằng, đảo 3 ô. Trả tín hiệu theo nến: dt (+1 DT mua / -1 DB bán), tri, cat; giá ảo."""
    idx = np.floor(np.log(c) / box).astype(int); n = len(c)
    dt = np.zeros(n, int); tri = np.zeros(n, int); cat = np.zeros(n, int); F = np.empty(n)
    cols = []          # [type, top, bottom, flags(dict)]
    i0 = idx[0]
    for t in range(n):
        v = idx[t]
        if not cols:
            if v >= i0 + 3: cols.append([1, v, i0, {}])
            elif v <= i0 - 3: cols.append([-1, i0, v, {}])
            F[t] = c[t]; continue
        cur = cols[-1]; newcol = False; moved = False
        if cur[0] == 1:
            if v > cur[1]: cur[1] = v; moved = True
            elif v <= cur[1] - 3: cols.append([-1, cur[1] - 1, v, {}]); newcol = True
        else:
            if v < cur[2]: cur[2] = v; moved = True
            elif v >= cur[2] + 3: cols.append([1, v, cur[2] + 1, {}]); newcol = True
        cur = cols[-1]
        if (moved or newcol) and len(cols) >= 3:
            p1 = cols[-3]                                 # cột cùng loại trước đó
            if cur[0] == 1 and not cur[3].get("dt") and cur[1] > p1[1]:
                cur[3]["dt"] = True; dt[t] = 1
                if len(cols) >= 5 and cols[-5][1] == p1[1]: tri[t] = 1; cur[3]["tri"] = True
                # catapult: cột X (-5... ) có triple, cột O ở giữa không phá đáy cột O trước, nay vượt đỉnh cột X đó
                if len(cols) >= 5 and cols[-3][3].get("tri") and cols[-2][2] > cols[-4][2]: cat[t] = 1
            if cur[0] == -1 and not cur[3].get("dt") and cur[2] < p1[2]:
                cur[3]["dt"] = True; dt[t] = -1
                if len(cols) >= 5 and cols[-5][2] == p1[2]: tri[t] = -1; cur[3]["tri"] = True
                if len(cols) >= 5 and cols[-3][3].get("tri") and cols[-2][1] < cols[-4][1]: cat[t] = -1
        F[t] = np.exp(box * (cur[1] + 1 if cur[0] == 1 else cur[2]))
    return dt, tri, cat, F


def three_lb(c, nl):
    n = len(c); d = np.zeros(n, int); F = np.empty(n); lines = []   # (lo, hi, dir)
    ref = c[0]
    for t in range(n):
        x = c[t]
        if not lines:
            if x != ref: lines.append((min(ref, x), max(ref, x), 1 if x > ref else -1))
        else:
            lo, hi, dr = lines[-1]; last = lines[-nl:]
            if dr == 1:
                if x > hi: lines.append((hi, x, 1))
                elif x < min(z[0] for z in last): lines.append((x, lo, -1))
            else:
                if x < lo: lines.append((x, lo, -1))
                elif x > max(z[1] for z in last): lines.append((hi, x, 1))
        if lines:
            lo, hi, dr = lines[-1]; d[t] = dr; F[t] = hi if dr == 1 else lo
        else: F[t] = x
        if len(lines) > 50: lines = lines[-10:]
    return d, F


def kagi(c, rev):
    n = len(c); thick = np.zeros(n, int); F = np.empty(n)
    d = 0; E = c[0]; sh = np.nan; wa = np.nan; th = 0
    for t in range(n):
        x = c[t]; R = rev[t]
        if not np.isfinite(R): F[t] = E; continue
        if d >= 0 and x > E: E = x; d = 1 if d == 0 and x > c[0] + R else d
        if d <= 0 and x < E: E = x; d = -1 if d == 0 and x < c[0] - R else d
        if d == 1 and x <= E - R: sh = E; E = x; d = -1
        elif d == -1 and x >= E + R: wa = E; E = x; d = 1
        if d == 1 and np.isfinite(sh) and E > sh: th = 1
        if d == -1 and np.isfinite(wa) and E < wa: th = -1
        thick[t] = th; F[t] = E
    return thick, F


# ===================== CHIẾN LƯỢC -> TÍN HIỆU =====================
def hold_fill(sig):
    """sig: +1/-1 = lệnh mới, 0 = giữ nguyên -> vị thế."""
    s = np.zeros(len(sig)); cur = 0
    for i, v in enumerate(sig):
        if v != 0: cur = v
        s[i] = cur
    return s


def strategies(d, ismask):
    o, h, l, c, atr = (d[k].values for k in ("Open", "High", "Low", "Close", "atr"))
    medr = np.nanmedian((atr / c)[ismask])          # ATR% trung vị trong IS -> box log hằng
    out = []                                        # (method, param, s(L/S), F)
    ho, hh, hl, hc = heikin(o, h, l, c); green = hc > ho
    for N in (1, 2, 3):
        g = pd.Series(green.astype(float)).rolling(N).sum().values
        sig = np.where(g == N, 1, np.where(g == 0, -1, 0)); out.append(("HA_doi_mau", f"N={N}", hold_fill(sig), hc))
    nlw = green & (hl >= ho - 1e-12); nuw = (~green) & (hh <= ho + 1e-12)
    for k in (1, 2):
        a = pd.Series(nlw.astype(float)).rolling(k).sum().values == k
        b = pd.Series(nuw.astype(float)).rolling(k).sum().values == k
        s = np.zeros(len(c)); cur = 0
        for i in range(len(c)):
            if cur == 1 and not green[i]: cur = 0
            if cur == -1 and green[i]: cur = 0
            if a[i]: cur = 1
            elif b[i]: cur = -1
            s[i] = cur
        out.append(("HA_khong_bong", f"k={k}", s, hc))
    boxes = [(f"ATRx{k}", k * atr, False) for k in (0.5, 1, 2)] + [(f"log{k}xATR%", k * medr, True) for k in (1, 2)]
    for bn, bx, lg in boxes:
        run, F = renko(c, bx, lg)
        for N in (1, 2, 3):
            sig = np.where(run >= N, 1, np.where(run <= -N, -1, 0)); out.append(("Renko_dao_N", f"{bn},N={N}", hold_fill(sig), F))
        for M in (3, 5):
            s = np.where(run >= M, 1, np.where(run <= -M, -1, 0)).astype(float)
            # đã vào thì giữ tới khi có brick ngược (run đổi dấu)
            cur = 0
            for i in range(len(c)):
                if cur == 1 and run[i] < 0: cur = 0
                if cur == -1 and run[i] > 0: cur = 0
                if s[i] != 0: cur = s[i]
                s[i] = cur
            out.append(("Renko_dem_brick", f"{bn},M={M}", s, F))
    for k in (0.5, 1, 2):
        dt, tri, cat, F = pnf(c, k * medr)
        out.append(("PnF_double", f"box={k}xATR%", hold_fill(dt), F))
        for name, sg in (("PnF_triple", tri), ("PnF_catapult", cat)):
            s = np.zeros(len(c)); cur = 0
            for i in range(len(c)):
                if cur == 1 and dt[i] == -1: cur = 0
                if cur == -1 and dt[i] == 1: cur = 0
                if sg[i] != 0: cur = sg[i]
                s[i] = cur
            out.append((name, f"box={k}xATR%", s, F))
    for nl in (2, 3, 4):
        dr, F = three_lb(c, nl); out.append(("Line_Break", f"{nl}LB", dr.astype(float), F))
    for k in (0.5, 1, 2, 3):
        th, F = kagi(c, k * atr); out.append(("Kagi", f"dao={k}ATR", th.astype(float), F))
    # ---- đối chứng trên nến thường ----
    for N in (20, 55):
        hiN = pd.Series(h).rolling(N).max().shift(1).values; loN = pd.Series(l).rolling(N).min().shift(1).values
        sig = np.where(c > hiN, 1, np.where(c < loN, -1, 0)); out.append(("BL_Donchian", f"N={N}", hold_fill(sig), c))
    for f, sl in ((10, 50), (20, 100)):
        ef = pd.Series(c).ewm(span=f, adjust=False).mean().values; es = pd.Series(c).ewm(span=sl, adjust=False).mean().values
        s = np.sign(ef - es); s[:sl] = 0; out.append(("BL_EMA", f"{f}/{sl}", s, c))
    out.append(("BL_BuyHold", "-", np.ones(len(c)), c))
    return out


# ===================== BACKTEST =====================
def backtest(d, s, F, spread, fake, mask_sets):
    o, c, atr = d.Open.values, d.Close.values, d.atr.values; n = len(c)
    if fake:
        held = s.copy(); px = F
        pnl = np.r_[held[:-1] * np.diff(px), 0.0]
        cost = 0.5 * spread * np.abs(np.diff(np.r_[0, held]))
        base = px
    else:
        held = np.r_[0, s[:-1]]                      # vị thế tại open j (quyết định ở close j-1)
        nxt = np.r_[o[1:], c[-1]]
        pnl = held * (nxt - o)
        cost = 0.5 * spread * np.abs(np.diff(np.r_[0, held]))
        base = o
    net = pnl - cost
    ret = net / base
    # giao dịch
    chg = np.flatnonzero(np.diff(np.r_[0, held, 0]) != 0)
    res = {}
    dates = d.index.normalize() if hasattr(d.index, "normalize") else d.index
    for nm, m in mask_sets.items():
        r = pd.Series(np.where(m, ret, 0.0), index=dates).groupby(level=0).sum()
        r = r[r.index.isin(dates[m])]
        sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0.0
        eq = np.cumsum(r.values); dd = (np.maximum.accumulate(np.r_[0, eq])[1:] - eq).max() if len(eq) else 0
        tr = []
        for a, b in zip(chg[:-1], chg[1:]):
            if held[a] == 0 or not m[a]: continue
            p = net[a:b].sum() + (-0.5 * spread * abs(held[a]) if b < n else 0)
            ref = atr[a - 1] if a > 0 and np.isfinite(atr[a - 1]) else np.nan
            tr.append((p, p / ref if ref else np.nan))
        tr = np.array(tr) if tr else np.zeros((0, 2))
        gp, gl = tr[tr[:, 0] > 0, 0].sum(), -tr[tr[:, 0] < 0, 0].sum()
        res[nm] = dict(sharpe=sh, tot_ret_pct=100 * eq[-1] if len(eq) else 0, maxdd_pct=100 * dd, trades=len(tr),
                       win=100 * (tr[:, 0] > 0).mean() if len(tr) else np.nan, PF=gp / gl if gl > 0 else np.nan,
                       expR=np.nanmean(tr[:, 1]) if len(tr) and np.isfinite(tr[:, 1]).any() else np.nan, exposure=100 * (held[m] != 0).mean())
    return res


def boot_series(d, rng):
    """Block-bootstrap nến OOS (giữ quan hệ O/H/L/C trong nến, khối BLOCK nến), có 150 nến khởi động."""
    oo = d[d.period == "OOS"]; prevc = d.Close.shift(1)[d.period == "OOS"].values
    R = np.log(np.c_[oo.Open.values, oo.High.values, oo.Low.values, oo.Close.values] / prevc[:, None])
    R = R[np.isfinite(R).all(1)]; m = len(R); need = m + 150
    starts = rng.integers(0, m - BLOCK, need // BLOCK + 1)
    ix = (starts[:, None] + np.arange(BLOCK)[None, :]).ravel()[:need]
    rr = R[ix]; c = oo.Close.values[0] * np.exp(np.cumsum(rr[:, 3]))
    pc = np.r_[oo.Close.values[0], c[:-1]]
    O, H, L = pc * np.exp(rr[:, 0]), pc * np.exp(rr[:, 1]), pc * np.exp(rr[:, 2])
    H = np.maximum.reduce([H, O, c]); L = np.minimum.reduce([L, O, c])
    bpd = max(1, int(round(len(oo) / oo.index.normalize().nunique())))      # số nến/ngày như dữ liệu thật
    days = pd.bdate_range("2000-01-03", periods=need // bpd + 2)
    idx = pd.DatetimeIndex(np.repeat(days, bpd)[:need])
    b = pd.DataFrame(dict(Open=O, High=H, Low=L, Close=c), index=idx)
    b["atr"] = atr_rma(H, L, c); b["period"] = np.r_[["WU"] * 150, ["OOS"] * m]
    return b


def run(args):
    tk, tf = args
    d = load_tf(tk, tf); sp = SPREAD[tk]
    ism = (d.period == "IS").values; oos = (d.period == "OOS").values
    rows = []
    strat = strategies(d, ism)
    for meth, par, s, F in strat:
        for mode in ("LS", "L"):
            ss = s if mode == "LS" else np.maximum(s, 0)
            if meth == "BL_BuyHold" and mode == "LS": continue
            for fake in (False, True):
                if fake and meth.startswith("BL_"): continue
                r = backtest(d, ss, F, sp, fake, {"IS": ism, "OOS": oos})
                for per, v in r.items():
                    rows.append(dict(ticker=tk, tf=tf, method=meth, param=par, mode=mode, fill="ao" if fake else "that", period=per, **v))
    R = pd.DataFrame(rows)
    # chọn tốt nhất IS (khớp thật) mỗi phương pháp, rồi bootstrap OOS
    real = R[R.fill == "that"]; isr = real[(real.period == "IS") & (real.trades >= 10)]
    best = isr.loc[isr.groupby("method").sharpe.idxmax()][["method", "param", "mode"]]
    rng = np.random.default_rng(7)
    boots = [boot_series(d, rng) for _ in range(N_BOOT)]
    nulls = {i: [] for i in range(len(best))}
    for bd in boots:
        bm = (bd.period == "OOS").values
        SD = {(m, p): (sg, F) for m, p, sg, F in strategies(bd, bm)}
        for i, (_, b) in enumerate(best.iterrows()):
            sg, F = SD[(b.method, b.param)]
            ss = sg if b["mode"] == "LS" else np.maximum(sg, 0)
            nulls[i].append(backtest(bd, ss, F, sp, False, {"OOS": bm})["OOS"]["sharpe"])
    brow = []
    for i, (_, b) in enumerate(best.iterrows()):
        oosr = real[(real.method == b.method) & (real.param == b.param) & (real["mode"] == b["mode"]) & (real.period == "OOS")].iloc[0]
        null = np.array(nulls[i])
        brow.append(dict(ticker=tk, tf=tf, method=b.method, param=b.param, mode=b["mode"], OOS_sharpe=oosr.sharpe,
                         boot_mean=null.mean(), boot_p95=np.percentile(null, 95), p_boot=(1 + (null >= oosr.sharpe).sum()) / (len(null) + 1)))
    return R, pd.DataFrame(brow)


def strategies_one(d, meth, par, ism):
    for m, p, s, F in strategies(d, ism):
        if m == meth and p == par: return s, F


if __name__ == "__main__":
    jobs = [("GC=F", "1d"), ("ES=F", "1d"), ("^GSPC", "1d"), ("GC=F", "1h"), ("ES=F", "1h"), ("^GSPC", "1h"), ("GC=F", "15m"), ("ES=F", "15m")]
    if len(sys.argv) > 1: jobs = [tuple(a.split(":")) for a in sys.argv[1:]]
    allR, allB = [], []
    with Pool(min(4, len(jobs))) as P:
        for R, B in P.imap_unordered(run, jobs):
            allR.append(R); allB.append(B); print(R.ticker.iloc[0], R.tf.iloc[0], len(R), flush=True)
    pd.concat(allR).to_csv("results6/charts_all.csv", index=False); pd.concat(allB).to_csv("results6/charts_boot.csv", index=False)
