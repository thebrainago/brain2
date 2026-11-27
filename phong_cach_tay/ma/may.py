# -*- coding: utf-8 -*-
"""Tham số máy phong cách tay (cent) — bọc may_hyb, không đặt lệnh thật.

Quy cách cent (giả định Exness Standard Cent, vì không mở được E:\\exness_cent):
- Tiền tệ USC; 100 USC = 1 USD. P/L và số dư ×100 so với USD; lot và giá giữ nguyên.
- Vàng: cỡ HĐ 100, bước lot 0,01, pv=100 USD/1,00 giá/1,00 lot (tức 10.000 USC).
- US500: pv=1, bước 0,10 (nếu sàn cent bước 0,01 thì cần chạy lại K).
- Vốn vận hành: 10.000 USD = 1.000.000 USC (đủ so với kiểu nạp 10k→30k, và với lần reset demo 1 triệu).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

SPEC = {
    "XAU": dict(
        pv=100.0, step=0.01, minlot=0.01, spr=0.20,
        swl=-83.83, sws=20.64, lev=1000.0, scale_crash=4000.0,
        m1=Path("/workspace/backtests/rapid_hedge/data/GOLD_i_M1.csv"),
        pq=Path("/workspace/quet_intraday/m5/xauusd.parquet"),
        ten_xm="GOLD.i#",
    ),
    "US500": dict(
        pv=1.0, step=0.1, minlot=0.1, spr=0.65,
        swl=-1.24, sws=0.17, lev=1000.0, scale_crash=7000.0,
        m1=Path("/workspace/backtests/rapid_hedge/data/US500Cash_M1.csv"),
        pq=Path("/workspace/quet_intraday/m5/spxusd.parquet"),
        ten_xm="US500Cash#",
    ),
}


def P_tay(sym="XAU", spr=None, K=3, coef=1.15, G=3.0, th=1.5,
          EQ0=10000.0, ddb=3000.0, maxL=15, hN=5, htp=0.8, hr=1.0, hcap=2.0,
          **kw):
    """HYB+AG chỉnh theo phong cách tay đo được:

    - Không SL cứng (hstop=0).
    - Vào cụm K lệnh nhỏ (lot = K * step; vàng 0,03 / US500 0,30).
    - DCA theo khoảng ATR + neo vùng (lmode=1); hệ số lot 1,15 (trung vị tay = 1,0,
      nhưng tăng lot không hệ số đã làm vàng lỗ sâu — giữ 1,15 theo bài học quét).
    - Trần tầng 15 (Anh từng 77–110 lệnh cùng lúc; trần đó cháy cent, nên cắt).
    - Cắt một nửa +1 ATR M15; đóng rổ hòa/lãi tổng.
    - Hedge cụm 5 lệnh ngược, TP 0,8 ATR M5, tối đa 2 lần rổ; không DCA khi hedge mở.
    - AG 1,5x khi D1 EMA200 dốc âm và rổ ≥5 tầng hoặc >5 ngày.
    """
    sp = SPEC[sym]
    if spr is None:
        spr = sp["spr"]
    pv, step = sp["pv"], sp["step"]
    swl, sws, lev = sp["swl"], sp["sws"], sp["lev"]
    zmode = 0
    tp1 = 1.0
    sfrac = 0.5
    bx = 0.0
    bxu = 0
    hmode = 1
    hrecl = 1
    hexp = 960
    brk = 0.0
    mlf = 200.0
    emode = 0
    refill = 1
    dmin = 0.5
    mg = 3.0
    lmode = 1
    ks = 1.5
    gmin = 1.5
    gmax = 4.8
    wP, wF, wV, wO = 0.5, 1.0, 1.5, 1.5
    se = 1.0
    sd = 1.0
    shi = 99.0
    chi = 99.0
    mhi = 1.0
    sfd = 0.5
    flipx = 0
    oppx = 0
    deadw = 960
    tf = 0
    tmode = 1
    tnl = 5
    tnd = 5 * 1380
    trel = 1
    hstop = 0
    bpd = 1380
    # overrides
    for k, v in kw.items():
        if k in locals() or k in ("K", "coef", "G", "th", "EQ0", "ddb", "maxL", "hN", "htp", "hr", "hcap", "spr"):
            pass
    loc = dict(
        zmode=zmode, K=K, coef=coef, maxL=maxL, tp1=tp1, sfrac=sfrac, bx=bx, bxu=bxu,
        hmode=hmode, hN=hN, hr=hr, hcap=hcap, htp=htp, hrecl=hrecl, hexp=hexp, brk=brk,
        spr=spr, EQ0=EQ0, ddb=ddb, mlf=mlf, lev=lev, swl=swl, sws=sws, emode=emode,
        refill=refill, dmin=dmin, mg=mg, lmode=lmode, G=G, ks=ks, gmin=gmin, gmax=gmax,
        wP=wP, wF=wF, wV=wV, wO=wO, se=se, sd=sd, shi=shi, chi=chi, mhi=mhi, sfd=sfd,
        flipx=flipx, oppx=oppx, deadw=deadw, tf=tf, th=th, tmode=tmode, tnl=tnl,
        tnd=tnd, trel=trel, hstop=hstop, bpd=bpd, pv=pv, step=step,
    )
    loc.update(kw)
    return np.array([
        loc["zmode"], loc["K"], loc["coef"], loc["maxL"], loc["tp1"], loc["sfrac"], loc["bx"], loc["bxu"],
        loc["hmode"], loc["hN"], loc["hr"], loc["hcap"], loc["htp"], loc["hrecl"], loc["hexp"], loc["brk"],
        loc["spr"], loc["EQ0"], loc["ddb"], loc["mlf"], loc["lev"], loc["swl"], loc["sws"], loc["emode"],
        loc["refill"], loc["dmin"], loc["mg"], loc["lmode"], loc["G"], loc["ks"], loc["gmin"], loc["gmax"],
        loc["wP"], loc["wF"], loc["wV"], loc["wO"], loc["se"], loc["sd"], loc["shi"], loc["chi"], loc["mhi"],
        loc["sfd"], loc["flipx"], loc["oppx"], loc["deadw"], loc["tf"], loc["th"], loc["tmode"], loc["tnl"],
        loc["tnd"], loc["trel"], loc["hstop"], loc["bpd"], loc["pv"], loc["step"],
    ], dtype=np.float64)


def S_xac_nhan(S_truyen_thong: np.ndarray, bonus: np.ndarray | None) -> np.ndarray:
    """Vào từ tín hiệu data, chỉ khi chỉ báo truyền thống cũng đồng thuận (S>=1).

    - Không có sự kiện data (bonus==0): dùng điểm truyền thống (cửa sổ không có Fxaurum).
    - Data cùng chiều (bonus>0): chỉ vào nếu S_truyen_thong >= 1, cộng thêm 1.
    - Data ngược (bonus<0): chặn vào.
    """
    s = np.asarray(S_truyen_thong, dtype=np.float64)
    if bonus is None:
        return s
    b = np.asarray(bonus, dtype=np.float64)
    out = s.copy()
    dong = b > 0
    nguoc = b < 0
    out[dong] = np.where(s[dong] >= 1.0, s[dong] + 1.0, 0.0)
    out[nguoc] = 0.0
    return out
