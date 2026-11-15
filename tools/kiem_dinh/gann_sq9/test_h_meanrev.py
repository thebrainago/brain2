# -*- coding: utf-8 -*-
"""
VÒNG 7 – HƯỚNG 2: MEAN-REVERSION NGẮN HẠN (long-only, daily). Quy tắc khai báo trước (kiểu Connors):
  RSI2<10 & C>SMA200 -> thoát khi C>SMA5 | RSI2<5 & C>SMA200 | RSI3<20 & C>SMA200 | RSI2<10 không lọc
  IBS<0.2 giữ 1 phiên | IBS<0.1 giữ 1 phiên | C = đáy 5 phiên & C>SMA200 (thoát C>đỉnh hôm trước hoặc tối đa 5 phiên)
  | C = đáy 10 phiên & C>SMA200 (như trên)
Khớp: 'open' = OPEN THẬT phiên sau (thực tế); 'close' = khớp ngay close phiên tín hiệu (MOC, như bài gốc – lạc quan).
Thị trường: GC=F, ES=F, ^GSPC, SPY (kiểm tra chéo – SPY có giá mở cửa thật từ 1993; ^GSPC trước ~2014 open bị 'cũ' = close hôm trước).
"""
import numpy as np, pandas as pd
from multiprocessing import Pool
from common7 import *

TICKERS = ["GC=F", "ES=F", "^GSPC", "SPY"]
RULES = ["RSI2<10&>SMA200", "RSI2<5&>SMA200", "RSI3<20&>SMA200", "RSI2<10_noFilter", "IBS<0.2_1d", "IBS<0.1_1d",
         "Low5&>SMA200", "Low10&>SMA200"]


def rule_w(d, r):
    C, H, L = d.Close.values, d.High.values, d.Low.values
    s200 = sma(C, 200); s5 = sma(C, 5); up = np.nan_to_num(C > s200).astype(bool)
    r2, r3 = rsi(C, 2), rsi(C, 3); ibs = (C - L) / np.where(H > L, H - L, np.nan)
    ex5 = C > s5
    if r == "RSI2<10&>SMA200": return hold_state((r2 < 10) & up, ex5)
    if r == "RSI2<5&>SMA200": return hold_state((r2 < 5) & up, ex5)
    if r == "RSI3<20&>SMA200": return hold_state((r3 < 20) & up, ex5)
    if r == "RSI2<10_noFilter": return hold_state(r2 < 10, ex5)
    if r == "IBS<0.2_1d": return np.nan_to_num(ibs < 0.2).astype(float)
    if r == "IBS<0.1_1d": return np.nan_to_num(ibs < 0.1).astype(float)
    if r.startswith("Low"):
        N = int(r[3:r.index("&")]); lowN = C <= pd.Series(C).rolling(N).min().values
        prevH = np.r_[np.nan, H[:-1]]
        return hold_n(lowN & up, 5, exitc=C > prevH)


def job(a):
    tk, r, mode = a; d = load_d(tk); w = rule_w(d, r)
    rng = np.random.default_rng(abs(hash(a)) % 2**32)
    return eval_daily(tk, d, w, mode, rng, r, "2_meanrev", "L")


if __name__ == "__main__":
    jobs = [(tk, r, m) for tk in TICKERS for r in RULES for m in ("open", "close")]
    with Pool(8) as p: rows = p.map(job, jobs)
    df = pd.DataFrame(rows); df.to_csv("results7/h2_meanrev.csv", index=False)
    pd.set_option("display.width", 250)
    print(df[["ticker", "strategy", "fill", "IS_sharpe", "OOS_sharpe", "IS_p_rand", "OOS_p_rand", "IS_pf", "OOS_pf",
              "IS_trades", "OOS_trades", "OOS_maxdd", "OOS_expo", "OOS_win"]].round(2).to_string())
