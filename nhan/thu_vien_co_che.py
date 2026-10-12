# -*- coding: utf-8 -*-
"""THU VIEN CO CHE NHO, TACH ROI (vong 7, 12/10/2026) - viec (A) cua ban giao.

Moi MANH la mot phep bien doi CHAN (dict tu `ngu_phap.sinh_chan`) truoc khi vao
`mo_phong.chay_he`; khong dong vao bo doc hay diem vao cua EA. Tham so CO DINH, lay MODE
gia tri mac dinh input cua chinh cac tac gia trong kho `data/cau_kho` (dem ngay 12/10/2026,
xem `NGUON_THAM_SO`) - khong toi uu, khong chon theo ket qua.

  A  SL/TP ATR      SL = 1.5 x ATR(14), TP = 3.0 x ATR(14) (thay SL/TP cua EA)
  T  keo SL ATR     keo = close -/+ 1.0 x ATR(14), chi siet; chua co SL -> SL dau 1.5 x ATR
  S  loc spread     bo lenh khi spread bar vao > 30 point
  P  loc phien      chi vao khi gio server cua bar vao trong [7, 22)
  D  gioi han ngay  toi da 1 lenh / ngay cho CA he (moi chan chung mot bien ngay)

To hop toi da 3 manh (`to_hop()`): vong 7 (5 manh) 26; vong 9 them B (hoa von 1,5 ATR -> vao +10 point)
va R (rui ro 1 %/lenh, chi khi SL theo khoang) -> 7 manh, 64. MOI to hop chay deu phai dem
vao so phep thu khi hieu chinh nhieu phep thu (Holm).
Chan RO (luoi / hedge) KHONG ap manh (khong co SL/TP don) -> `ap_duoc()` = False.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

MANH = ("A", "T", "S", "P", "D", "B", "R")
NGUON_THAM_SO = {
    "A": "mode input SL-ATR = 1.5 (58 file), TP-ATR = 3.0 (32 file), ATR period = 14 (397 file)",
    "T": "mode input trail-ATR khac 0 = 1.0 (39 file)",
    "S": "mode input MaxSpread = 30 point (99 file)",
    "P": "mode gio bat dau khac 0 = 7 (63 file), gio ket thuc = 22 (47 file)",
    "D": "mode MaxTradesPerDay = 1 (44 file)",
    "B": "vong 9: mode InpBreakEvenATR = 1.5 (18 file), InpBEBufferPoints = 10 (15 file)",
    "R": "vong 9: mode input *Risk* = 1.0 % (509 file)",
}
HOA_VON_ATR, HOA_VON_CONG_DIEM = 1.5, 10.0
RUI_RO = 0.01
#: vong 9: loc tin (InpNewsMinutesBefore = 30) CHUA DO DUOC - khong co lich tin lich su tren box
ATR_N, SL_ATR, TP_ATR, KEO_ATR = 14, 1.5, 3.0, 1.0
SPREAD_MAX_DIEM = 30.0
GIO_TU, GIO_DEN = 7, 22
BIEN_NGAY = "__tv_ngay"
TRAN_MANH = 3


def to_hop(tran: int = TRAN_MANH) -> list[tuple[str, ...]]:
    """() + moi to hop 1..tran manh, thu tu co dinh."""
    ra = [()]
    for k in range(1, tran + 1):
        ra += list(itertools.combinations(MANH, k))
    return ra


def atr(df: pd.DataFrame, n: int = ATR_N) -> np.ndarray:
    """ATR Wilder (RMA cua true range) tai CLOSE bar i - giong iATR cua MT5 xap xi."""
    h, l, c = (df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    ra = pd.Series(tr).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean().to_numpy()
    return ra


def ap_duoc(chan: list[dict]) -> bool:
    return bool(chan) and not any(c.get("ro") for c in chan)


def ap_manh(chan: list[dict], df: pd.DataFrame, manh: tuple[str, ...],
            diem: float = 1e-5, _atr: np.ndarray | None = None) -> list[dict]:
    """Ban SAO cua `chan` voi cac manh `manh`. Khong nhin truoc: moi mang tai i dung du lieu
    toi close bar i; loc phien dung gio cua bar vao j = i+1 (biet truoc khi bar mo)."""
    if not manh:
        return [dict(c) for c in chan]
    if not ap_duoc(chan):
        raise ValueError("chan RO / rong - khong ap manh")
    a = atr(df) if _atr is None else _atr
    cl = df["close"].to_numpy(dtype=float)
    n = len(df)
    ra = []
    for c0 in chan:
        c = dict(c0)
        ch = int(c["chieu"])
        if "A" in manh:
            c.update(mt5=False, sl_diem=None, tp_diem=None, sl=None, tp=None,
                     sl_kc=SL_ATR * a, tp_kc=TP_ATR * a, sl_kc_min_spread=None, rui_ro=None)
        if "T" in manh:
            co_sl = c.get("sl") is not None or c.get("sl_kc") is not None or \
                (c.get("mt5") and c.get("sl_diem"))
            if not co_sl:
                tp_kc = c.get("tp_kc")
                if c.get("mt5") and c.get("tp_diem"):
                    tp_kc = np.full(n, float(c["tp_diem"]) * diem)
                c.update(mt5=False, sl_diem=None, tp_diem=None, sl=None,
                         sl_kc=SL_ATR * a, tp_kc=tp_kc)
            c["keo"] = cl - ch * KEO_ATR * a
        if "S" in manh:
            c["spread_max_diem"] = SPREAD_MAX_DIEM
        if "P" in manh:
            gio = np.asarray(df.index.hour)
            ok = np.zeros(n, dtype=bool)
            ok[:-1] = (gio[1:] >= GIO_TU) & (gio[1:] < GIO_DEN)
            c["cho"] = np.asarray(c["cho"], dtype=bool) & ok
        if "B" in manh:
            c["hoa_von_kc"] = HOA_VON_ATR * a
            c["hoa_von_cong"] = HOA_VON_CONG_DIEM * diem
        if "R" in manh and c.get("sl_kc") is not None:
            c["rui_ro"] = RUI_RO
        if "D" in manh:
            c["chan_boi"] = list(c.get("chan_boi") or []) + [BIEN_NGAY]
            c["dat"] = list(c.get("dat") or []) + [BIEN_NGAY]
        ra.append(c)
    return ra
