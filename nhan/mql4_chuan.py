# -*- coding: utf-8 -*-
"""LAN MQL4 MONG: chuan hoa CU PHAP MQL4 -> dang MQL5 bo doc `doc_ma` da hieu (11/10/2026).

Chi doi CU PHAP co tuong duong 1-1, KHONG them logic, KHONG doan:
  - `extern` -> `input`; `int start()` (MQL4 cu, khi khong co OnTick) -> `void OnTick()`;
  - `OP_BUY` / `OP_SELL` (dung token) -> `ORDER_TYPE_BUY` / `ORDER_TYPE_SELL`. Lenh CHO
    (`OP_BUYSTOP`, `OP_SELLLIMIT`...) GIU NGUYEN -> bo doc khong xac dinh chieu = tu choi;
  - chuoi gia dinh san `Close[k]`/`Open[k]`/`High[k]`/`Low[k]` (k so nguyen) ->
    `iClose(_Symbol,_Period,k)` ...; `Bid`/`Ask` -> `SymbolInfoDouble(_Symbol,SYMBOL_BID/ASK)`;
    `Point`/`Digits` -> `_Point`/`_Digits`; `Symbol()` -> `_Symbol`;
  - chi bao MQL4 tra GIA TRI (`iMA(NULL,0,p,ms,meth,pr,k)`, `iRSI`, `iATR`, `iCCI`,
    `iMomentum`, `iStdDev`, `iBands`, `iMACD`, `iStochastic`) voi symbol hien tai
    (NULL/_Symbol/Symbol()), khung hien tai (0/PERIOD_CURRENT/_Period/Period()) va dich bar k
    la SO NGUYEN -> CUNG ky hieu ma `doc_ma._chuan_hoa_mql5` sinh tu handle + CopyBuffer
    (`iMA(_Symbol,_Period,..)` = bar 1 da dong, `[j]` = bar j+1, `[S0]` = bar 0 dang chay).
    Khung CO DINH khac (PERIOD_H4...) / dich bar la bien -> GIU NGUYEN (bo doc tu choi).
Tham so input trong loi goi chi bao thay bang gia tri mac dinh cua tac gia (nhu ban MQL5).

`dau_hieu_chan(src)` liet ke LY DO CAU TRUC khong dich duoc (lenh cho, khong OrderSend,
mang chi bao tu tinh, trailing tung tick) - de bao cao, KHONG thay bo doc.
"""
from __future__ import annotations

import re

_TF0 = r"(?:0|PERIOD_CURRENT|_Period|Period\(\))"
_SYM0 = r"(?:NULL|_Symbol|Symbol\(\))"
_MODE_BANDS = {"MODE_MAIN": 0, "MODE_BASE": 0, "0": 0, "MODE_UPPER": 1, "1": 1,
               "MODE_LOWER": 2, "2": 2}
_MODE_MS = {"MODE_MAIN": 0, "0": 0, "MODE_SIGNAL": 1, "1": 1}
_LAY_BANDS = {0: "giua", 1: "tren", 2: "duoi"}
_LAY_MS = {0: "chinh", 1: "tinhieu"}


def _D():
    from nhan import doc_ma as D
    return D


def _ky_hieu(goi: str, k: int) -> str:
    """Ky hieu bar cua `doc_ma` cho chi bao tai dich bar MQL k."""
    if k == 0:
        return goi + "[S0]"
    return goi + (f"[{k - 1}]" if k > 1 else "")


def _chi_bao(vb: str, gt: dict) -> str:
    D = _D()
    ra, i = [], 0
    rx = re.compile(r"(?<![\w.])(iMA|iRSI|iATR|iCCI|iMomentum|iStdDev|iBands|iMACD|iStochastic)"
                    r"[ \t]*\(")
    while True:
        m = rx.search(vb, i)
        if not m:
            ra.append(vb[i:])
            break
        mo = m.end() - 1
        ds = D._tach_doi_so(vb, mo)
        dong = D._dong_ngoac(vb, mo)
        ten = m.group(1)
        moi = None
        if ds and dong > 0:
            ds = [x.strip() for x in ds]
            n = {"iMA": 7, "iRSI": 5, "iATR": 4, "iCCI": 5, "iMomentum": 5, "iStdDev": 7,
                 "iBands": 8, "iMACD": 8, "iStochastic": 9}[ten]
            if len(ds) == n and re.fullmatch(_SYM0, ds[0]) and re.fullmatch(_TF0, ds[1]) \
                    and re.fullmatch(r"\d+", ds[-1]):
                k = int(ds[-1])
                a = [gt.get(x, x) for x in ds[2:-1]]
                dau = "_Symbol,_Period,"
                if ten in ("iMA", "iRSI", "iATR", "iCCI", "iMomentum", "iStdDev"):
                    moi = _ky_hieu(f"{ten}({dau}{','.join(a)})", k)
                elif ten == "iBands":         # MQL4 (p,dev,bshift,price,mode) -> MQL5 (p,bshift,dev,price)
                    md = _MODE_BANDS.get(a[4])
                    if md is not None:
                        moi = _ky_hieu(f"iBands_{_LAY_BANDS[md]}({dau}{a[0]},{a[2]},{a[1]},{a[3]})", k)
                elif ten == "iMACD":          # (fast,slow,signal,price,mode)
                    md = _MODE_MS.get(a[4])
                    if md is not None:
                        moi = _ky_hieu(f"iMACD_{_LAY_MS[md]}({dau}{','.join(a[:4])})", k)
                else:                         # iStochastic (K,D,slowing,method,price_field,mode)
                    md = _MODE_MS.get(a[5])
                    pf = {"0": "STO_LOWHIGH", "1": "STO_CLOSECLOSE"}.get(a[4], a[4])
                    if md is not None:
                        moi = _ky_hieu(f"iStochastic_{_LAY_MS[md]}({dau}{','.join(a[:4])},{pf})", k)
        if moi is None:
            ra.append(vb[i:m.end()])
            i = m.end()
            continue
        ra.append(vb[i:m.start()] + moi.replace(" ", ""))
        i = dong + 1
    return "".join(ra)


def chuan_hoa(src: str) -> str:
    """MQL4 -> dang MQL5 tuong duong cu phap (xem dau file). Khong them logic."""
    vb = src.replace("\r\n", "\n")
    vb = re.sub(r"(?m)^([ \t]*)extern\b", r"\1input", vb)
    if not re.search(r"\bOnTick[ \t]*\(", vb):
        vb = re.sub(r"(?m)^([ \t]*)int[ \t]+start[ \t]*\([ \t]*\)", r"\1void OnTick()", vb)
    vb = re.sub(r"(?<![\w.])OP_BUY(?!\w)", "ORDER_TYPE_BUY", vb)
    vb = re.sub(r"(?<![\w.])OP_SELL(?!\w)", "ORDER_TYPE_SELL", vb)
    vb = re.sub(r"(?<![\w.])(Close|Open|High|Low)\[[ \t]*(\d+)[ \t]*\]",
                lambda m: f"i{m.group(1)}(_Symbol,_Period,{m.group(2)})", vb)
    vb = re.sub(r"(?<![\w.])(Bid|Ask)(?![\w(])",
                lambda m: f"SymbolInfoDouble(_Symbol,SYMBOL_{m.group(1).upper()})", vb)
    vb = re.sub(r"(?<![\w.])Point(?![\w(])", "_Point", vb)
    vb = re.sub(r"(?<![\w.])Digits(?![\w(])", "_Digits", vb)
    vb = re.sub(r"(?<![\w.])Symbol\(\)", "_Symbol", vb)
    gt = {k: v for k, v in _D()._gia_tri_input(vb).items() if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", v)}
    vb = _chi_bao(vb, gt)
    return vb


def dau_hieu_chan(src: str) -> list[str]:
    """Ly do CAU TRUC (bao cao) - khong phai bo doc, khong doi ket qua doc."""
    if not re.search(r"\bOrderSend\s*\(", src):
        return ["khong co OrderSend (khung/khuon mau, khong dat lenh)"]
    ra = []
    if re.search(r"\bOrderSend\s*\([^;]*\bOP_(?:BUY|SELL)(?:STOP|LIMIT)\b", src, re.S) or \
            re.search(r"=\s*[^;]*\bOP_(?:BUY|SELL)(?:STOP|LIMIT)\b[^;]*;", src):
        ra.append("lenh CHO (OP_BUYSTOP/SELLSTOP/LIMIT) - DSL chua co lenh cho MQL4")
    if re.search(r"\bOrderModify\s*\(", src) and re.search(r"(?i)\btrail", src):
        ra.append("trailing/sua lenh (OrderModify)")
    D = _D()
    for m in re.finditer(r"\bfor\s*\(", src):
        k = D._dong_ngoac(src, m.end() - 1)
        if k < 0:
            continue
        j = k + 1
        while j < len(src) and src[j] in " \t\r\n":
            j += 1
        if j >= len(src) or src[j] != "{":
            continue
        e = D._cuoi_khoi(src, j)
        than = src[j:e]
        if re.search(r"(?<![\w.])(?:Open|High|Low|Close)\s*\[\s*[A-Za-z_]\w*\s*\]", than):
            mang = sorted(set(re.findall(r"(?<![\w.])([A-Za-z_]\w*)\s*\[\s*[A-Za-z_]\w*\s*\]\s*=(?!=)",
                                         than)))
            if mang:
                ra.append("chuoi tu tinh trong vong lap tu gia (%s) - chua dich" % ", ".join(mang[:3]))
    if re.search(r"\bGetTickCount\s*\(", src) and re.search(r"(?i)latency", src):
        ra.append("scalper tick/HFT (do tre ms) - khong mo phong theo bar")
    return ra
