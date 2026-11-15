# -*- coding: utf-8 -*-
"""
VÒNG 7 – HƯỚNG 4: BIẾN ĐỘNG & TIN TỨC (daily). Khai báo trước:
 A) Nén biên độ -> breakout: NR7 hoặc Inside bar tại t; phiên t+1 đặt buy-stop tại High[t], sell-stop tại Low[t]
    (khớp tại mức stop, hoặc tại OPEN nếu mở cửa vượt qua). Nếu cả 2 mức cùng bị chạm trong phiên -> lấy kết quả XẤU hơn
    (không biết thứ tự). Thoát: close t+1 (1D) hoặc close t+3 (3D). Bản LS và bản chỉ Long.
    Đối chứng riêng: cùng quy tắc bracket áp lên MỌI phiên (không điều kiện nén) -> nén có giúp gì không.
 B) VIX (Yahoo ^VIX): RSI2<10&>SMA200 / IBS<0.2 tách VIX>20 vs <=20; C>SMA200 chỉ khi VIX<=20; VIX spike
    (VIX > 1.25 x SMA10 VIX) -> mua giữ 5 phiên. Thị trường S&P (ES=F, ^GSPC, SPY).
 C) Tin: FOMC (lịch Fed 2007+), CPI & NFP (ngày phát hành BLS 2000+). (i) drift ngày tin: close(e-1)->close(e);
    (ii) đi tiếp sau tin: theo dấu phiên tin, giữ từ OPEN e+1, 1 hoặc 3 phiên; (iii) đảo chiều sau tin (ngược dấu, 1 phiên).
"""
import numpy as np, pandas as pd
from multiprocessing import Pool
from scipy import stats
from common7 import *

EV = {k: pd.to_datetime(open(f"events/{k}_dates.txt").read().split()) for k in ("fomc", "cpi", "nfp")}


def vix_series(idx):
    v = pd.read_pickle("data_VIX_1d.pkl")
    if isinstance(v.columns, pd.MultiIndex): v.columns = v.columns.droplevel(1)
    v.index = pd.to_datetime(v.index).tz_localize(None).normalize()
    return v.Close.reindex(idx).ffill().values


# ---------------- A) NR7 / inside bar ----------------
def bracket(d, cond, hold, side, sp):
    O, H, L, C = d.Open.values, d.High.values, d.Low.values, d.Close.values; n = len(C); out = []
    for t in np.flatnonzero(cond):
        u = t + 1; x = min(n - 1, t + hold)
        if u >= n or x >= n: continue
        res = []
        if H[u] >= H[t]:
            e = max(O[u], H[t]); res.append(C[x] / e - 1)
        if side == "LS" and L[u] <= L[t]:
            e = min(O[u], L[t]); res.append(1 - C[x] / e)
        if not res: continue
        r = min(res) if len(res) == 2 else res[0]   # cả 2 chạm -> kết quả xấu hơn
        out.append((t, r - sp / C[t]))
    return out


def run_bracket():
    rows = []
    for tk in ("GC=F", "ES=F", "^GSPC"):
        d = load_d(tk); H, L = d.High.values, d.Low.values; rg = H - L; sp = SPREAD[tk]
        nr7 = rg <= pd.Series(rg).rolling(7).min().values
        inside = np.r_[False, (H[1:] < H[:-1]) & (L[1:] > L[:-1])]
        allc = np.ones(len(d), bool); per = d.period.values
        for hold in (1, 3):
            for side in ("LS", "L"):
                base = dict(bracket(d, allc, hold, side, sp))
                for nm, cnd in (("NR7", nr7), ("InsideBar", inside)):
                    tr = bracket(d, cnd, hold, side, sp)
                    r = dict(direction="4_volnews", ticker=tk, tf="1d", strategy=f"{nm}_breakout_{hold}D", param=side, fill="stop/open->close")
                    for p_ in ("IS", "OOS"):
                        x = np.array([v for t, v in tr if per[t] == p_]); b = np.array([v for t, v in base.items() if per[t] == p_])
                        if len(x) < 10: continue
                        # Sharpe năm hoá theo số lệnh/năm thực tế
                        yrs = (per == p_).sum() / 252; tpy = len(x) / yrs
                        r[f"{p_}_sharpe"] = x.mean() / x.std() * np.sqrt(tpy) * np.sqrt(hold) / np.sqrt(hold)  # xấp xỉ theo lệnh
                        r[f"{p_}_pf"] = x[x > 0].sum() / -x[x < 0].sum(); r[f"{p_}_trades"] = len(x); r[f"{p_}_win"] = 100 * (x > 0).mean()
                        r[f"{p_}_avg_bp"] = 1e4 * x.mean(); r[f"{p_}_uncond_avg_bp"] = 1e4 * b.mean()
                        eq = np.cumprod(1 + x); r[f"{p_}_maxdd"] = 100 * (1 - eq / np.maximum.accumulate(eq)).max()
                        r[f"{p_}_cagr"] = 100 * (eq[-1] ** (1 / yrs) - 1) if eq[-1] > 0 else -100
                        t1 = stats.ttest_ind(x, b, equal_var=False)
                        r[f"{p_}_p_rand"] = t1.pvalue / 2 if t1.statistic > 0 else 1 - t1.pvalue / 2   # nén tốt hơn vô điều kiện?
                        t0 = stats.ttest_1samp(x, 0); r[f"{p_}_p_gt0"] = t0.pvalue / 2 if t0.statistic > 0 else 1 - t0.pvalue / 2
                    rows.append(r)
    return rows


# ---------------- B) VIX ----------------
def vix_job(a):
    tk, nm = a; d = load_d(tk); C, H, L = d.Close.values, d.High.values, d.Low.values; vix = vix_series(d.index)
    s200 = sma(C, 200); up = np.nan_to_num(C > s200).astype(bool); r2 = rsi(C, 2); ex5 = C > sma(C, 5)
    ibs = (C - L) / np.where(H > L, H - L, np.nan); hi = vix > 20
    if nm == "RSI2<10&>SMA200|VIX>20": w = hold_state((r2 < 10) & up & hi, ex5)
    elif nm == "RSI2<10&>SMA200|VIX<=20": w = hold_state((r2 < 10) & up & ~hi, ex5)
    elif nm == "IBS<0.2|VIX>20": w = np.nan_to_num((ibs < 0.2) & hi).astype(float)
    elif nm == "IBS<0.2|VIX<=20": w = np.nan_to_num((ibs < 0.2) & ~hi).astype(float)
    elif nm == "C>SMA200&VIX<=20": w = (up & ~hi).astype(float)
    elif nm == "VIXspike>1.25xSMA10_hold5": w = hold_n(vix > 1.25 * sma(vix, 10), 5)
    rng = np.random.default_rng(abs(hash(a)) % 2**32)
    return eval_daily(tk, d, w, "open", rng, nm, "4_volnews", "L")


# ---------------- C) Tin tức ----------------
def ev_job(a):
    tk, ev, kind = a; d = load_d(tk); idx = d.index; n = len(d); C = d.Close.values
    e_ix = idx.get_indexer(EV[ev][EV[ev] <= idx[-1]]); e_ix = e_ix[e_ix > 0]
    w = np.zeros(n); rng = np.random.default_rng(abs(hash(a)) % 2**32)
    if kind == "eventday_long":
        w[e_ix - 1] = 1; mode = "close"
    else:
        sgn = np.sign(C[e_ix] / C[e_ix - 1] - 1)
        hold = 3 if kind == "follow_3D" else 1; s = -1 if kind == "fade_1D" else 1
        for e, g in zip(e_ix, sgn):
            w[e:min(n, e + hold)] = s * g          # quyết định tại close e -> giữ từ OPEN e+1
        mode = "open"
    return eval_daily(tk, d, w, mode, rng, f"{ev.upper()}_{kind}", "4_volnews", "LS" if kind != "eventday_long" else "L")


if __name__ == "__main__":
    rows = run_bracket()
    vj = [(tk, nm) for tk in ("ES=F", "^GSPC", "SPY") for nm in ["RSI2<10&>SMA200|VIX>20", "RSI2<10&>SMA200|VIX<=20",
          "IBS<0.2|VIX>20", "IBS<0.2|VIX<=20", "C>SMA200&VIX<=20", "VIXspike>1.25xSMA10_hold5"]]
    ej = [(tk, ev, k) for tk in ("GC=F", "ES=F", "^GSPC", "SPY") for ev in ("fomc", "cpi", "nfp")
          for k in ("eventday_long", "follow_1D", "follow_3D", "fade_1D")]
    with Pool(8) as p:
        rows += p.map(vix_job, vj); rows += p.map(ev_job, ej)
    df = pd.DataFrame(rows); df.to_csv("results7/h4_volnews.csv", index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_rows", 300)
    print(df[["ticker", "strategy", "param", "IS_sharpe", "OOS_sharpe", "IS_p_rand", "OOS_p_rand", "IS_pf", "OOS_pf",
              "IS_trades", "OOS_trades", "OOS_maxdd", "IS_avg_bp", "OOS_avg_bp", "OOS_uncond_avg_bp"]].round(3).to_string())
