# -*- coding: utf-8 -*-
"""
VÒNG 7 – HƯỚNG 3: HIỆU ỨNG LỊCH / THỜI GIAN. Khai báo trước:
 A) Overnight (close->open kế tiếp) vs Intraday (open->close) – SPY 2000+ (giá mở cửa thật, đã điều chỉnh cổ tức),
    ^GSPC chỉ 2014+ (trước đó open 'cũ' = close hôm trước), ES=F 1h (16:00 -> 09:00 ET vs 09:00 -> 16:00 ET, 2024-06+).
    Mỗi ngày 1 lượt vào/ra -> trả 1 spread/ngày.
 B) Turn-of-month: giữ từ close phiên áp chót của tháng tới close phiên +3 tháng sau (4 phiên) – khớp close (đúng quy tắc);
    kiểm tra thêm bản khớp open.
 C) Day-of-week: giữ close(t-1)->close(t) của từng thứ.  D) Pre-holiday: giữ close->close của phiên trước ngày nghỉ NYSE.
 E) Vàng & ES 1h: lợi nhuận theo giờ ET (23 giờ), theo phiên Á (18-03h), London (03-08h), NY (08-17h); chiến lược
    long theo phiên. Kiểm định t (Welch) + FDR.
"""
import numpy as np, pandas as pd
from scipy import stats
from common7 import *

rows = []


def tt(x, y=None):
    """p một phía: mean(x) > mean(y) (Welch) hoặc mean(x) > 0."""
    x = x[np.isfinite(x)]
    if len(x) < 10: return np.nan, np.nan
    if y is None: r = stats.ttest_1samp(x, 0.0)
    else: y = y[np.isfinite(y)]; r = stats.ttest_ind(x, y, equal_var=False)
    p = r.pvalue / 2 if r.statistic > 0 else 1 - r.pvalue / 2
    return r.statistic, p


def met_days(pnl, ann=252):
    pnl = pnl[np.isfinite(pnl)]
    if len(pnl) < 10: return {}
    eq = np.cumprod(1 + pnl); yrs = len(pnl) / ann
    return dict(sharpe=pnl.mean() / pnl.std() * np.sqrt(ann), cagr=100 * (eq[-1] ** (1 / yrs) - 1),
                maxdd=100 * (1 - eq / np.maximum.accumulate(eq)).max(),
                pf=pnl[pnl > 0].sum() / -pnl[pnl < 0].sum(), trades=len(pnl), expo=np.nan, tot=100 * (eq[-1] - 1),
                win=100 * np.mean(pnl > 0))


def add_row(direction, tk, tf, name, param, fill, per_pnl, per_p, extra=None):
    r = dict(direction=direction, ticker=tk, tf=tf, strategy=name, param=param, fill=fill)
    for per in ("IS", "OOS"):
        for k, v in met_days(per_pnl[per], 252 if tf != "1h_bar" else 252 * 23).items(): r[f"{per}_{k}"] = v
        r[f"{per}_p_rand"] = per_p[per]
    if extra: r.update(extra)
    rows.append(r)


# ---------- A) overnight vs intraday ----------
for tk, start in (("SPY", "2000-01-01"), ("^GSPC", "2014-01-01")):
    d = load_d(tk); d = d[d.index >= start].copy()
    if tk == "^GSPC":   # chia đôi 2014+ (2016 quá sớm) -> dùng mốc giữa
        mid = d.index[0] + (d.index[-1] - d.index[0]) / 2; d["period"] = np.where(d.index < mid, "IS", "OOS")
    O, C = d.Open.values, d.Close.values; sp = SPREAD[tk]
    on = np.r_[np.nan, O[1:] / C[:-1] - 1] - sp / np.r_[np.nan, C[:-1]]       # mua close t-1, bán open t
    da = C / O - 1 - sp / O                                                      # mua open, bán close
    for nm, x, y in (("Overnight(close->open)", on, da), ("Intraday(open->close)", da, on)):
        pp = {per: tt(x[d.period.values == per])[1] for per in ("IS", "OOS")}
        add_row("3_calendar", tk, "1d", nm, f"từ {start[:4]}", "close/open", {per: x[d.period.values == per] for per in ("IS", "OOS")}, pp,
                {f"{per}_p_vs_other": tt(x[d.period.values == per], y[d.period.values == per])[1] for per in ("IS", "OOS")})
# ES 1h
h = load_h("ES=F"); h["date"] = h.index.date; sp = SPREAD["ES=F"]
g = h.groupby("date")
c16 = h[h.index.hour == 15].groupby("date").Close.last()      # bar 15:00-16:00 -> close 16:00
o09 = h[h.index.hour == 9].groupby("date").Open.first()       # bar 09:00 mở 09:00
per = h.groupby("date").period.first()
dd = pd.DataFrame({"c16": c16, "o09": o09, "per": per}).dropna()
ov = (dd.o09 / dd.c16.shift(1) - 1 - sp / dd.c16.shift(1)).values
dy = (dd.c16 / dd.o09 - 1 - sp / dd.o09).values
for nm, x, y in (("Overnight(16h->09h)", ov, dy), ("Intraday(09h->16h)", dy, ov)):
    pp = {p_: tt(x[dd.per.values == p_])[1] for p_ in ("IS", "OOS")}
    add_row("3_calendar", "ES=F", "1h", nm, "2024-06+", "open/close bar", {p_: x[dd.per.values == p_] for p_ in ("IS", "OOS")}, pp,
            {f"{p_}_p_vs_other": tt(x[dd.per.values == p_], y[dd.per.values == p_])[1] for p_ in ("IS", "OOS")})

# ---------- B,C,D) TOM, DOW, pre-holiday (daily) ----------
gs = load_d("^GSPC"); allbd = pd.bdate_range(gs.index[0], gs.index[-1]); nyse_closed = set(allbd.difference(gs.index))
for tk in ("ES=F", "^GSPC", "SPY", "GC=F"):
    d = load_d(tk); idx = d.index; n = len(d); C = d.Close.values; sp = SPREAD[tk]
    ym = idx.year * 12 + idx.month
    last = np.r_[ym[1:] != ym[:-1], False]                       # phiên cuối tháng
    pos_in_month = pd.Series(1, index=idx).groupby(ym).cumsum().values   # 1 = phiên đầu tháng
    wtom = np.zeros(n)
    for t in range(n - 1):
        if (t + 1 < n and last[t + 1]) or last[t] or pos_in_month[t] in (1, 2): wtom[t] = 1  # giữ qua: cuối, +1, +2, +3
    r_cc = np.r_[np.nan, C[1:] / C[:-1] - 1]
    rng = np.random.default_rng(7)
    for mode in ("close", "open"):
        rw = eval_daily(tk, d, wtom, mode, rng, "TurnOfMonth(-1..+3)", "3_calendar", "L")
        rows.append(rw)
    # DOW: giữ close(t-1)->close(t) với t = thứ X; so với các ngày khác
    dow = idx.day_of_week.values
    for k, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
        inn = dow == k; net = r_cc - sp / np.r_[np.nan, C[:-1]]
        pp = {p_: tt(r_cc[inn & (d.period.values == p_)], r_cc[~inn & (d.period.values == p_)])[1] for p_ in ("IS", "OOS")}
        add_row("3_calendar", tk, "1d", f"DOW_{nm}", "giữ close->close", "close", {p_: net[inn & (d.period.values == p_)] for p_ in ("IS", "OOS")}, pp)
    # pre-holiday: phiên t mà ngày làm việc kế tiếp NYSE đóng cửa
    nxt = idx + pd.tseries.offsets.BDay(1)
    preh = np.array([x in nyse_closed for x in nxt])
    wph = np.r_[preh[1:], False].astype(float)                  # quyết định tại close t-1 -> giữ tới close phiên trước lễ
    rows.append(eval_daily(tk, d, wph, "close", rng, "PreHoliday", "3_calendar", "L"))

# ---------- E) 1h: giờ trong ngày & phiên ----------
hour_rows = []
for tk in ("GC=F", "ES=F"):
    h = load_h(tk); sp = SPREAD[tk]
    r = (h.Close / h.Open - 1).values; hr = h.index.hour.values; per_ = h.period.values
    for H in sorted(set(hr)):
        if (hr == H).sum() < 100: continue
        rec = dict(ticker=tk, hour_ET=H)
        for p_ in ("IS", "OOS"):
            x = r[(hr == H) & (per_ == p_)]; allx = r[per_ == p_]
            rec[f"{p_}_mean_bp"] = 1e4 * x.mean(); rec[f"{p_}_n"] = len(x)
            t, _ = stats.ttest_1samp(x, 0); rec[f"{p_}_t"] = t; rec[f"{p_}_p2"] = stats.ttest_1samp(x, 0).pvalue
            rec[f"{p_}_vs_avg_p2"] = stats.ttest_ind(x, allx[(hr[per_ == p_] != H)], equal_var=False).pvalue
        hour_rows.append(rec)
    # phiên: long từ open bar đầu tới close bar cuối, mỗi ngày 1 lượt
    h["sday"] = (h.index + pd.Timedelta(hours=6)).date          # ngày giao dịch bắt đầu 18:00 ET hôm trước
    SESS = {"Asia(18-03h)": list(range(18, 24)) + [0, 1, 2], "London(03-08h)": [3, 4, 5, 6, 7], "NY(08-17h)": list(range(8, 17)),
            "NYam(09-12h)": [9, 10, 11], "NYpm(13-16h)": [13, 14, 15]}
    for nm, hrs in SESS.items():
        s = h[np.isin(h.index.hour, hrs)].groupby("sday").agg(o=("Open", "first"), c=("Close", "last"), per=("period", "first"))
        x = (s.c / s.o - 1 - sp / s.o).values
        pp = {p_: tt(x[s.per.values == p_])[1] for p_ in ("IS", "OOS")}
        add_row("3_calendar", tk, "1h", f"Session_{nm}", "long mỗi ngày", "open/close bar", {p_: x[s.per.values == p_] for p_ in ("IS", "OOS")}, pp)
    # chọn giờ tốt nhất trên IS (t>2) -> giao dịch OOS (1 lựa chọn duy nhất, kiểm tra ngoài mẫu)
hdf = pd.DataFrame(hour_rows)
for c in ("IS_p2", "OOS_p2"): hdf[c.replace("p2", "q")] = bh_fdr(hdf[c].values)
hdf.to_csv("results7/h3_hour_of_day.csv", index=False)
for tk in ("GC=F", "ES=F"):
    hs = hdf[hdf.ticker == tk]; best = hs[(hs.IS_t > 2)].hour_ET.tolist(); worst = hs[(hs.IS_t < -2)].hour_ET.tolist()
    h = load_h(tk); sp = SPREAD[tk]; r = (h.Close / h.Open - 1).values - sp / h.Open.values; hr = h.index.hour.values
    for lab, hl, sg in (("IS_best_hours_long", best, 1), ("IS_worst_hours_short", worst, -1)):
        if not hl: continue
        m = np.isin(hr, hl); x = sg * (h.Close / h.Open - 1).values - sp / h.Open.values
        pp = {p_: tt(x[m & (h.period.values == p_)])[1] for p_ in ("IS", "OOS")}
        add_row("3_calendar", tk, "1h", lab, str(hl), "open/close bar", {p_: x[m & (h.period.values == p_)] for p_ in ("IS", "OOS")}, pp)

df = pd.DataFrame(rows); df.to_csv("results7/h3_calendar.csv", index=False)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 300)
cols = ["ticker", "tf", "strategy", "fill", "IS_sharpe", "OOS_sharpe", "IS_p_rand", "OOS_p_rand", "IS_pf", "OOS_pf", "IS_trades", "OOS_trades", "OOS_maxdd", "OOS_cagr"]
print(df[cols].round(3).to_string())
print(hdf.round(3).to_string())
