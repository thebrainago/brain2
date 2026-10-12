# -*- coding: utf-8 -*-
"""KHUNG EA MQL + .set + ham boc buffer (them 11/10/2026).

Ba viec, deu la VIET LAI CU PHAP co chung minh, khong doan nghia:

1. `.set` cua tac gia (`ap_set`): `input <kieu> TEN = mac_dinh;` -> gia tri trong .set (EA
   chay trong tester voi .set do). Chi ap input CO trong ma; `ENUM_TIMEFRAMES` so (MT5:
   5 = PERIOD_M5, 16385 = PERIOD_H1...) -> ten `PERIOD_*`; enum khac dang so -> KHONG ap
   (khong biet ten hang) va ghi `bo_qua`. Chuoi/ngay -> bo qua.

2. Khung CO DINH cua EA (`khung_co_dinh`): moi doi so khung cua ham chuoi/chi bao
   (`iRSI(sym, TF, ..)`, `iTime(sym, TF, k)`, `CopyRates(sym, TF, ..)`, `iBarShift`...)
   giai (input mac dinh / .set / const / #define) ve CUNG MOT `PERIOD_X` co dinh, va file
   KHONG dung khung bieu do o dau ca (`_Period`, `Period()`, `PERIOD_CURRENT`/`0` lam doi
   so khung, `PeriodSeconds()` rong) -> EA hanh xu NHU chay tren bieu do X: viet lai cac
   doi so do thanh `_Period` va tra `khung_ea = "X"`. Vong thu chi duoc chay co che do
   tren du lieu khung X (`vong_thu_nghiem`: khac khung -> `khong_hop_khung`). Tron khung
   (chi bao M5 + cong bar khung bieu do, hay hai khung co dinh) -> khong doi gi (bo doc
   tu choi nhu cu). `PERIOD_CURRENT` chi duoc phep trong phep so sanh `==`/`!=` (kiem
   input trong OnInit), khong lam doi so.

3. Ham boc doc MOT gia tri buffer (`noi_ham_boc_buffer`): dang

       double R(const int h, const int b, const int s) {
          ... CopyBuffer(h, b, s, 1, arr) ...      // DUNG MOT CopyBuffer, count = 1
          return arr[0]; }                          // moi return khac: EMPTY_VALUE / hang
       double G(const int s) { return R(handle, 0, s); }

   `G(k)` / `R(handle, b, k)` voi k la SO -> `__boc_<handle>_<b>[k]` + dong
   `CopyBuffer(handle, b, 0, K, __boc_<handle>_<b>)` (K > k lon nhat) chen o dau tep, kem
   `ArraySetAsSeries(__boc.., true)` - dang mang ma `doc_ma._chuan_hoa_mql5` da hieu (chi
   so k = bar k). Gia tri loi (EMPTY_VALUE khi CopyBuffer hong) = kiem du lieu, `doc_ma`
   da coi la quan tri. Tham so boc khong phai dang tren / co tham chieu `&` -> khong noi.
"""
from __future__ import annotations

import re

#: Gia tri so ENUM_TIMEFRAMES cua MT5 (tai lieu MQL5 "Chart Timeframes").
TF_SO = {1: "M1", 2: "M2", 3: "M3", 4: "M4", 5: "M5", 6: "M6", 10: "M10", 12: "M12",
         15: "M15", 20: "M20", 30: "M30", 16385: "H1", 16386: "H2", 16387: "H3",
         16388: "H4", 16390: "H6", 16392: "H8", 16396: "H12", 16408: "D1", 32769: "W1",
         49153: "MN1"}
_HIEN_TAI = {"_Period", "PERIOD_CURRENT", "0", "Period()"}
#: ham co doi so KHUNG o vi tri 1 (sau symbol)
_HAM_TF = (r"i(?:RSI|ATR|MA|CCI|Momentum|Bands|MACD|Stochastic|ADX|ADXWilder|StdDev|Ichimoku"
           r"|Envelopes|SAR|Force|DeMarker|WPR|RVI|AO|AC|OBV|MFI|Volumes|Custom|Time|Open|High"
           r"|Low|Close|Volume|TickVolume|Bars|BarShift|Highest|Lowest|Spread|RealVolume"
           r"|Fractals|Alligator|Gator|BearsPower|BullsPower|TEMA|DEMA|FrAMA|AMA|VIDyA|TriX"
           r"|BWMFI|Chaikin|AD|OsMA)"
           r"|Copy(?:Rates|Time|Open|High|Low|Close|TickVolume|RealVolume|Spread)|Bars"
           r"|SeriesInfoInteger")
_RX_GOI_TF = re.compile(r"\b(" + _HAM_TF + r")[ \t]*\(")
_RX_INPUT = re.compile(
    r"(?:^|(?<=;))([ \t]*(?:static[ \t]+)?(?:input|sinput|extern)[ \t]+)([\w:]+)([ \t]+)([A-Za-z_]\w*)"
    r"([ \t]*=[ \t]*)([^;\n]+?)([ \t]*;)", re.M)


def _tach_doi(vb: str, mo: int) -> tuple[list[str], int] | None:
    """Doi so cua loi goi co ngoac mo tai `mo` -> (danh sach, vi tri ngoac dong)."""
    sau, doi, dau = 0, [], mo + 1
    for i in range(mo, len(vb)):
        c = vb[i]
        if c in "([{":
            sau += 1
        elif c in ")]}":
            sau -= 1
            if sau == 0:
                doi.append(vb[dau:i].strip())
                return doi, i
        elif c == "," and sau == 1:
            doi.append(vb[dau:i].strip())
            dau = i + 1
    return None


def doc_set(vb: str) -> dict:
    """File .set MT4/MT5 -> {ten_input: gia_tri} (bo dong `;`, phan `||` toi uu)."""
    ra = {}
    for d in (vb or "").splitlines():
        d = d.strip().lstrip("\ufeff")
        if not d or d.startswith(";") or "=" not in d:
            continue
        k, v = d.split("=", 1)
        k = k.strip()
        if k and len(k) <= 64 and re.fullmatch(r"[A-Za-z_]\w*", k):
            ra[k] = v.split("||", 1)[0].strip()
    return ra


def ap_set(vb: str, gt_set: dict | None) -> tuple[str, dict]:
    """Thay mac dinh input bang gia tri .set. Tra (van ban moi, {ap: {ten: (cu, moi)},
    bo_qua: {ten: ly do}, khong_co: [ten .set khong co input]})."""
    ghi = {"ap": {}, "bo_qua": {}, "khong_co": []}
    if not gt_set:
        return vb, ghi
    co = set()

    def _thay(m):
        kieu, ten, cu = m.group(2), m.group(4), m.group(6).strip()
        co.add(ten)
        if ten not in gt_set:
            return m.group(0)
        v = gt_set[ten].strip()
        moi = None
        if kieu == "ENUM_TIMEFRAMES":
            if re.fullmatch(r"\d+", v):
                p = TF_SO.get(int(v))
                moi = ("PERIOD_" + p) if p else None
                if p is None:
                    ghi["bo_qua"][ten] = f"khung so {v} khong ro"
            elif re.fullmatch(r"PERIOD_\w+", v):
                moi = v
        elif kieu == "bool":
            moi = {"true": "true", "false": "false", "1": "true", "0": "false"}.get(v.lower())
        elif kieu in ("int", "uint", "long", "ulong", "short", "ushort", "char", "uchar",
                      "double", "float"):
            if re.fullmatch(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", v):
                moi = v
        else:
            ghi["bo_qua"][ten] = f"kieu {kieu} (enum/chuoi) - khong ap gia tri so"
            return m.group(0)
        if moi is None:
            ghi["bo_qua"].setdefault(ten, f"gia tri '{v[:20]}' khong hop kieu {kieu}")
            return m.group(0)
        try:
            bang_nhau = float(moi) == float(cu)
        except ValueError:
            bang_nhau = moi == cu
        if not bang_nhau:
            ghi["ap"][ten] = (cu, moi)
        return m.group(1) + kieu + m.group(3) + ten + m.group(5) + moi + m.group(7)

    vb2 = _RX_INPUT.sub(_thay, vb)
    ghi["khong_co"] = sorted(k for k in gt_set if k not in co)
    return vb2, ghi


def _bang_gia_tri(vb: str) -> dict:
    """input / const / #define -> chu (mac dinh, sau khi ap .set)."""
    ra = {m.group(4): m.group(6).strip() for m in _RX_INPUT.finditer(vb)}
    for m in re.finditer(r"^[ \t]*(?:static[ \t]+)?const[ \t]+\w+[ \t]+([A-Za-z_]\w*)[ \t]*="
                         r"[ \t]*([A-Za-z_]\w*|\d+)[ \t]*;", vb, re.M):
        truoc = vb[:m.start()]
        if truoc.count("{") == truoc.count("}"):
            ra.setdefault(m.group(1), m.group(2))
    for m in re.finditer(r"^[ \t]*#define[ \t]+([A-Za-z_]\w*)[ \t]+(\S+)[ \t]*$", vb, re.M):
        ra.setdefault(m.group(1), m.group(2))
    return ra


def _giai_tf(tok: str, bang: dict) -> str | None:
    """Doi so khung -> 'HIEN_TAI' | 'M5'... | None (bien khong giai duoc)."""
    for _ in range(4):
        tok = tok.strip()
        if tok.startswith("(ENUM_TIMEFRAMES)"):
            tok = tok[len("(ENUM_TIMEFRAMES)"):].strip()
        if tok in _HIEN_TAI:
            return "HIEN_TAI"
        m = re.fullmatch(r"PERIOD_(\w+)", tok)
        if m:
            return m.group(1) if m.group(1) in TF_SO.values() else None
        if re.fullmatch(r"\d+", tok):
            return TF_SO.get(int(tok))
        if tok in bang:
            tok = bang[tok]
            continue
        return None
    return None


def khung_co_dinh(vb: str) -> tuple[str | None, str, str]:
    """-> (khung_ea | None, van ban (da viet lai neu khung_ea), ly do)."""
    bang = _bang_gia_tri(vb)
    goi = []
    for m in _RX_GOI_TF.finditer(vb):
        if m.start() > 0 and vb[m.start() - 1] in ".":
            continue
        t = _tach_doi(vb, m.end() - 1)
        if t is None or len(t[0]) < 2:
            continue
        doi = t[0]
        if m.group(1) == "SeriesInfoInteger" or m.group(1) == "Bars":
            pass
        goi.append((m, doi))
    if not goi:
        return None, vb, "khong co doi so khung"
    giai = [(_giai_tf(doi[1], bang), doi[1]) for _, doi in goi]
    if any(g is None for g, _ in giai):
        return None, vb, "doi so khung khong giai duoc: " + ",".join(
            sorted({t for g, t in giai if g is None}))[:60]
    ks = {g for g, _ in giai}
    if "HIEN_TAI" in ks:
        return None, vb, ("khung bieu do" if ks == {"HIEN_TAI"} else "tron khung bieu do + co dinh")
    if len(ks) != 1:
        return None, vb, "nhieu khung co dinh: " + ",".join(sorted(ks))
    # khung bieu do dung o cho khac (khong phai doi so khung) -> tron, khong viet lai
    bo_so_sanh = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', vb)          # bo chuoi ky tu
    bo_so_sanh = re.sub(r"\w+[ \t]*(?:==|!=)[ \t]*PERIOD_CURRENT|PERIOD_CURRENT[ \t]*(?:==|!=)",
                        "", bo_so_sanh)
    if re.search(r"\b_Period\b|\bPeriod[ \t]*\([ \t]*\)|\bPERIOD_CURRENT\b"
                 r"|\bPeriodSeconds[ \t]*\([ \t]*\)|\bChartPeriod\b", bo_so_sanh):
        return None, vb, "khung bieu do dung ngoai doi so"
    khung = ks.pop()
    # viet lai doi so khung -> _Period (tu cuoi len de giu vi tri)
    ra = vb
    for m, doi in sorted(goi, key=lambda x: -x[0].start()):
        mo = m.end() - 1
        t = _tach_doi(ra, mo)
        if t is None:
            return None, vb, "loi viet lai"
        # tim vi tri doi so thu 2 trong ra[mo:]
        sau, i, dem = 0, mo, 0
        bat = None
        while i < len(ra):
            c = ra[i]
            if c in "([{":
                sau += 1
                if sau == 1 and c == "(":
                    bat = i + 1
            elif c in ")]}":
                sau -= 1
                if sau == 0:
                    break
            elif c == "," and sau == 1:
                dem += 1
                if dem == 1:
                    bat = i + 1
                elif dem == 2:
                    ra = ra[:bat] + "_Period" + ra[i:]
                    break
            i += 1
        else:
            return None, vb, "loi viet lai"
        if dem < 2:
            # chi co 2 doi so (Bars(sym, tf)) -> doi so cuoi
            j = _tach_doi(ra, mo)[1]
            ra = ra[:bat] + "_Period" + ra[j:]
    return khung, ra, "khung co dinh " + khung


_RX_HAM_DOUBLE = re.compile(r"^[ \t]*(?:static[ \t]+)?double[ \t]+([A-Za-z_]\w*)[ \t]*\(([^()]*)\)"
                            r"\s*\{", re.M)


def _than(vb: str, mo: int) -> tuple[str, int] | None:
    sau = 0
    for i in range(mo, len(vb)):
        if vb[i] == "{":
            sau += 1
        elif vb[i] == "}":
            sau -= 1
            if sau == 0:
                return vb[mo + 1:i], i
    return None


def _ten_tham_so(ds: str) -> list[str] | None:
    ra = []
    for p in [x.strip() for x in ds.split(",") if x.strip()]:
        if "&" in p or "[" in p:
            return None
        m = re.fullmatch(r"(?:const[ \t]+)?\w+[ \t]+([A-Za-z_]\w*)", p)
        if not m:
            return None
        ra.append(m.group(1))
    return ra


def _ham_doc_buffer(vb: str) -> dict:
    """{ten R: (i_handle, i_buffer, i_shift)} cho ham doc MOT gia tri buffer."""
    ra = {}
    for m in _RX_HAM_DOUBLE.finditer(vb):
        ts = _ten_tham_so(m.group(2))
        t = _than(vb, m.end() - 1)
        if not ts or t is None:
            continue
        than = t[0]
        cb = list(re.finditer(r"\bCopyBuffer[ \t]*\(([^;]*?)\)[ \t]*(?:!=|<|<=|==)?", than))
        if len(cb) != 1:
            continue
        doi = [x.strip() for x in cb[0].group(1).split(",")]
        if len(doi) != 5 or doi[3] != "1" or any(d not in ts for d in doi[:3]):
            continue
        arr = doi[4]
        rets = re.findall(r"\breturn\b[ \t]*([^;]*);", than)
        if not rets or rets[-1].strip() not in (f"{arr}[0]", f"({arr}[0])"):
            continue
        if any(r.strip() not in (f"{arr}[0]", f"({arr}[0])", "EMPTY_VALUE", "0", "0.0",
                                 "-1", "(EMPTY_VALUE)") for r in rets):
            continue
        if re.search(rf"\b{arr}[ \t]*\[[ \t]*(?!0[ \t]*\]|\])", than) or \
                re.search(rf"\b{arr}[ \t]*\[0\][ \t]*=(?!=)", than):
            continue
        # tham so khong bi gan lai
        if any(re.search(rf"\b{p}[ \t]*(?:[-+*/]?=(?!=)|\+\+|--)", than) for p in doi[:3]):
            continue
        ra[m.group(1)] = (ts.index(doi[0]), ts.index(doi[1]), ts.index(doi[2]), len(ts))
    return ra


def noi_ham_boc_buffer(vb: str) -> tuple[str, list[str]]:
    """Thay loi goi ham boc bang mang `__boc_<h>_<b>[k]` + CopyBuffer chen o dau tep."""
    R = _ham_doc_buffer(vb)
    if not R:
        return vb, []
    # G(s) { return R(h, b, s); }  -> (h, b, vi tri s)
    G = {}
    for m in _RX_HAM_DOUBLE.finditer(vb):
        if m.group(1) in R:
            continue
        ts = _ten_tham_so(m.group(2))
        t = _than(vb, m.end() - 1)
        if ts is None or t is None:
            continue
        than = t[0].strip()
        mm = re.fullmatch(r"return[ \t]*\(?[ \t]*([A-Za-z_]\w*)[ \t]*\(([^()]*)\)[ \t]*\)?[ \t]*;",
                          than)
        if not mm or mm.group(1) not in R:
            continue
        ih, ib, isf, n = R[mm.group(1)]
        doi = [x.strip() for x in mm.group(2).split(",")]
        if len(doi) != n or not re.fullmatch(r"[A-Za-z_]\w*", doi[ih]) or \
                not re.fullmatch(r"\d+", doi[ib]) or doi[isf] not in ts or len(ts) != 1:
            continue
        G[m.group(1)] = (doi[ih], int(doi[ib]))
    can: dict = {}
    ghi = []

    def _ten(h, b):
        return f"__boc_{h}_{b}"

    def _thay_g(m):
        h, b = G[m.group(1)]
        k = int(m.group(2))
        can[(h, b)] = max(can.get((h, b), 0), k)
        return f"{_ten(h, b)}[{k}]"

    def _thay_r(m):
        ih, ib, isf, n = R[m.group(1)]
        doi = [x.strip() for x in m.group(2).split(",")]
        if len(doi) != n or not re.fullmatch(r"[A-Za-z_]\w*", doi[ih]) or \
                not re.fullmatch(r"\d+", doi[ib]) or not re.fullmatch(r"\d+", doi[isf]):
            return m.group(0)
        h, b, k = doi[ih], int(doi[ib]), int(doi[isf])
        can[(h, b)] = max(can.get((h, b), 0), k)
        return f"{_ten(h, b)}[{k}]"

    # chi thay ngoai dinh nghia ham boc
    ra = vb
    if G:
        ra = re.sub(r"(?<![\w.])(" + "|".join(map(re.escape, G)) + r")[ \t]*\([ \t]*(\d+)[ \t]*\)",
                    _thay_g, ra)
    ra = re.sub(r"(?<![\w.])(" + "|".join(map(re.escape, R)) + r")[ \t]*\(([^()]*)\)"
                r"(?![ \t]*\{)", _thay_r, ra)
    if not can:
        return vb, []
    dau = []
    for (h, b), k in sorted(can.items()):
        t = _ten(h, b)
        dau.append(f"double {t}[]; ArraySetAsSeries({t},true); "
                   f"CopyBuffer({h},{b},0,{k + 1},{t});")
        ghi.append(f"ham boc buffer {h}/{b} -> mang (bar 0..{k})")
    # chen sau include/input: dau ham OnTick (de van la cung pham vi file cho bo doc)
    mo = re.search(r"\bvoid[ \t]+OnTick[ \t]*\([ \t]*\)\s*\{", ra)
    if not mo:
        return vb, []
    ra = ra[:mo.end()] + "\n   " + "\n   ".join(dau) + "\n" + ra[mo.end():]
    return ra, ghi



# ------------------------------------------------------------ MANG HANDLE (vong 7, 12/10/2026)
_RX_MANG_HANDLE = re.compile(r"^[ \t]*(?:static[ \t]+)?int[ \t]+([A-Za-z_]\w*)[ \t]*\[[ \t]*(\d+)[ \t]*\]"
                             r"[ \t]*;", re.M)
_RX_TAO_CB = re.compile(r"i(?:RSI|ATR|MA|CCI|Momentum|Bands|MACD|Stochastic|ADX|ADXWilder|StdDev"
                        r"|Ichimoku|Envelopes|SAR|Force|DeMarker|WPR|RVI|AO|AC|OBV|MFI|OsMA|TEMA"
                        r"|DEMA|FrAMA|AMA|VIDyA|TriX|BearsPower|BullsPower)[ \t]*\(")


def mang_handle(vb: str) -> tuple[str, list[str]]:
    """`int H[N];` + `H[k] = iMA(..);` (k SO, moi k gan DUNG MOT lan bang ham tao chi bao)
    -> bien don `H__k` (viet lai cu phap, cung nghia). Ham boc nhan CHI SO
    `double Val(int idx, int b, int s){ .. CopyBuffer(H[idx], b, s, 1, arr) .. }` -> tham
    so idx thanh handle (`CopyBuffer(idx, ..)`), cho goi `Val(k, ..)` (k SO) -> `Val(H__k, ..)`
    de `noi_ham_boc_buffer` noi tiep. Chi so khong phai SO ngoai `IndicatorRelease(..)` /
    so voi `INVALID_HANDLE` -> khong doi gi (mo ho)."""
    ghi = []
    for m in list(_RX_MANG_HANDLE.finditer(vb)):
        H, N = m.group(1), int(m.group(2))
        gan = {}
        hong = False
        for g in re.finditer(rf"(?<![\w.]){H}[ \t]*\[[ \t]*(\d+)[ \t]*\][ \t]*=(?!=)[ \t]*([^;]*);", vb):
            k = int(g.group(1))
            if k in gan or not _RX_TAO_CB.match(g.group(2).strip()) or k >= N:
                hong = True
            gan[k] = g.group(2)
        if hong or not gan:
            continue
        # chi so khong phai so: chi duoc trong IndicatorRelease / so voi INVALID_HANDLE / ham boc
        ham_boc = {}
        for f in _RX_HAM_DOUBLE.finditer(vb):
            ts = _ten_tham_so(f.group(2))
            t = _than(vb, f.end() - 1)
            if not ts or t is None:
                continue
            than = t[0]
            mm = re.search(rf"\bCopyBuffer[ \t]*\([ \t]*{H}[ \t]*\[[ \t]*([A-Za-z_]\w*)[ \t]*\]", than)
            if mm and mm.group(1) in ts and len(re.findall(rf"(?<![\w.]){H}\b", than)) == 1 and \
                    not re.search(rf"(?<![\w.]){mm.group(1)}\b(?![ \t]*\])", than.replace(mm.group(0), "")):
                ham_boc[f.group(1)] = (ts.index(mm.group(1)), f.start(), f.end() - 1 + len(t[0]) + 2)
        lo = False
        for x in re.finditer(rf"(?<![\w.]){H}[ \t]*\[[ \t]*([^\]]*?)[ \t]*\]", vb):
            if re.fullmatch(r"\d+", x.group(1)):
                continue
            truoc = vb[max(0, x.start() - 40):x.start()]
            sau = vb[x.end():x.end() + 25]
            if re.search(r"IndicatorRelease[ \t]*\([ \t]*$", truoc) or \
                    re.match(r"[ \t]*(?:!=|==)[ \t]*INVALID_HANDLE", sau) or \
                    any(a <= x.start() <= b for _, a, b in ham_boc.values()):
                continue
            lo = True
        if lo:
            continue
        ra = re.sub(rf"(?<![\w.]){H}[ \t]*\[[ \t]*(\d+)[ \t]*\]", lambda q: f"{H}__{q.group(1)}", vb)
        ra = ra.replace(m.group(0), m.group(0) + " int " + ", ".join(f"{H}__{k}" for k in sorted(gan)) + ";", 1)
        for ten, (vi_idx, _, _) in ham_boc.items():
            ra = re.sub(rf"\bCopyBuffer([ \t]*\([ \t]*){H}[ \t]*\[[ \t]*([A-Za-z_]\w*)[ \t]*\]",
                        r"CopyBuffer\1\2", ra)

            def _goi(q, vi_idx=vi_idx):
                doi = [d.strip() for d in q.group(2).split(",")]
                if vi_idx < len(doi) and re.fullmatch(r"\d+", doi[vi_idx]) and int(doi[vi_idx]) in gan:
                    doi[vi_idx] = f"{H}__{doi[vi_idx]}"
                    return f"{q.group(1)}({', '.join(doi)})"
                return q.group(0)
            ra = re.sub(rf"(?<![\w.])({re.escape(ten)})[ \t]*\(([^()]*)\)(?![ \t]*\{{)", _goi, ra)
            ghi.append(f"mang handle {H}[{N}] -> bien don; ham boc chi so {ten}")
        vb = ra
    return vb, ghi


_RX_HAM_GIA = re.compile(r"^[ \t]*(?:static[ \t]+)?(?:double|datetime|long)[ \t]+([A-Za-z_]\w*)[ \t]*"
                         r"\([ \t]*(?:const[ \t]+)?int[ \t]+([A-Za-z_]\w*)[ \t]*\)\s*\{\s*return[ \t]*\(?[ \t]*"
                         r"(i(?:Open|High|Low|Close|Time|Volume|TickVolume))[ \t]*\([ \t]*(_Symbol|Symbol\(\)|NULL)"
                         r"[ \t]*,[ \t]*(_Period|PERIOD_CURRENT)[ \t]*,[ \t]*\2[ \t]*\)[ \t]*\)?[ \t]*;\s*\}", re.M)


def noi_ham_gia(vb: str) -> tuple[str, list[str]]:
    """Ham MOT dong `double Price(int s){ return iClose(_Symbol, _Period, s); }` (sau khi
    khung co dinh da viet ve `_Period`) -> loi goi `Price(k)` (k SO) thay bang
    `iClose(_Symbol,_Period,k)`. Chi chuoi gia chuan, cung nghia (vong 7)."""
    ghi = []
    for m in list(_RX_HAM_GIA.finditer(vb)):
        ten, ham = m.group(1), m.group(3)
        n0 = vb
        dau, cuoi = vb[:m.end()], vb[m.end():]
        cuoi = re.sub(rf"(?<![\w.]){ten}[ \t]*\([ \t]*(\d+)[ \t]*\)",
                      lambda q: f"{ham}(_Symbol,_Period,{q.group(1)})", cuoi)
        dau = dau[:m.start()] + re.sub(rf"(?<![\w.]){ten}[ \t]*\([ \t]*(\d+)[ \t]*\)",
                                       lambda q: f"{ham}(_Symbol,_Period,{q.group(1)})",
                                       dau[:m.start()]) + dau[m.start():]
        vb = dau + cuoi
        if vb != n0:
            ghi.append(f"ham gia mot dong {ten}(k) -> {ham}(_Symbol,_Period,k)")
    return vb, ghi


def chuan_bi(vb: str, set_ea: str | dict | None = None) -> tuple[str, dict]:
    """.set -> khung co dinh -> ham boc buffer. Tra (van ban, ghi chu)."""
    gt = doc_set(set_ea) if isinstance(set_ea, str) else (set_ea or None)
    vb, g_set = ap_set(vb, gt)
    vb, g_mang = mang_handle(vb)
    khung, vb, ly = khung_co_dinh(vb)
    vb, g_gia = noi_ham_gia(vb)
    vb, g_boc = noi_ham_boc_buffer(vb)
    return vb, {"khung_ea": khung, "khung_ly_do": ly, "set": g_set if gt else None,
                "boc_buffer": g_mang + g_gia + g_boc}


# ------------------------------------------------------------ HET GIO THEO SO BAR
_RX_HAM_INT = re.compile(r"^[ \t]*(?:static[ \t]+)?(?:int|long|bool|void)[ \t]+([A-Za-z_]\w*)"
                         r"[ \t]*\(([^()]*)\)\s*\{", re.M)


def _ham_dem_bar_tu_vao(vb: str) -> set:
    """Ham int KHONG tham so tra `iBarShift(sym, _Period, t, ..)` voi t = POSITION_TIME cua
    vi the dang chon (so bar tu bar vao lenh)."""
    ra = set()
    for m in _RX_HAM_INT.finditer(vb):
        if m.group(2).strip() not in ("", "void"):
            continue
        t = _than(vb, m.end() - 1)
        if t is None:
            continue
        than = t[0]
        mb = list(re.finditer(r"\b(\w+)[ \t]*=[ \t]*iBarShift[ \t]*\([^,()]+,[ \t]*_Period[ \t]*,"
                              r"[ \t]*(\w+)[ \t]*(?:,[^()]*)?\)[ \t]*;", than))
        if len(mb) != 1:
            continue
        bien, tg = mb[0].group(1), mb[0].group(2)
        if not re.search(rf"\b{tg}[ \t]*=[ \t]*(?:\(datetime\))?[ \t]*PositionGetInteger[ \t]*\("
                         r"[ \t]*POSITION_TIME[ \t]*\)", than):
            continue
        rets = [r.strip() for r in re.findall(r"\breturn\b[ \t]*([^;]*);", than)]
        if not rets or rets[-1] not in (bien, f"({bien})"):
            continue
        if any(r not in (bien, f"({bien})", "0") for r in rets):
            continue
        ra.add(m.group(1))
    return ra


def het_gio_bar(vb: str, hang: dict) -> tuple[int | None, list[str]]:
    """EA dong vi the khi so bar tu bar vao >= N (o TICK DAU bar moi):

        void T(){ if(!IsOurPosition()) return; if(H() < N) return; ...; trade.PositionClose(..); }
        void OnTick(){ ... if(bar moi){ ...; T(); ... } }

    H = `_ham_dem_bar_tu_vao`; N hang/input so. T goi DUNG MOT lan, lenh don trong OnTick.
    Moi `if(..) return;` khac trong T phai la hoi vi the cua EA (IsOur/HasPosition/PositionSelect).
    -> (N, ghi chu) hoac (None, [ly do]) / (None, []) neu EA khong co dang nay."""
    H = _ham_dem_bar_tu_vao(vb)
    if not H:
        return None, []
    for m in _RX_HAM_INT.finditer(vb):
        t = _than(vb, m.end() - 1)
        if t is None:
            continue
        than = t[0]
        if not re.search(r"\bPositionClose[ \t]*\(", than):
            continue
        mh = re.search(r"\bif[ \t]*\([ \t]*(" + "|".join(map(re.escape, sorted(H)))
                       + r")[ \t]*\([ \t]*\)[ \t]*<[ \t]*(\w+(?:\.\d+)?)[ \t]*\)\s*return[ \t]*;",
                       than)
        if not mh:
            continue
        n = hang.get(mh.group(2), mh.group(2))
        try:
            n = float(n)
        except (TypeError, ValueError):
            return None, [f"het gio: N `{mh.group(2)}` khong phai hang"]
        if n != int(n) or n < 1:
            return None, [f"het gio: N = {n} khong hop le"]
        if than.find("PositionClose") < mh.end():
            continue
        # cac thoat som khac trong T: chi hoi vi the
        for mi in re.finditer(r"\bif[ \t]*\(([^\n]*?)\)\s*return[ \t]*;", than):
            if mi.start() == mh.start():
                continue
            if mi.start() > than.find("PositionClose"):
                continue
            dk = mi.group(1)
            if not re.fullmatch(r"\s*!?\s*\w*(?:Position|Our)\w*[ \t]*\([^()]*\)\s*", dk):
                return None, [f"het gio: thoat som `{dk[:40]}` truoc PositionClose - chua dich"]
        ten = m.group(1)
        goi = [g for g in re.finditer(rf"(?<![\w.>]){ten}[ \t]*\([ \t]*\)", vb)
               if g.start() != m.start(1)]
        if len(goi) != 1:
            return None, [f"het gio: `{ten}()` goi {len(goi)} cho - chua dich"]
        mo = re.search(r"\bvoid[ \t]+OnTick[ \t]*\([ \t]*\)\s*\{", vb)
        if not mo:
            return None, ["het gio: khong co OnTick"]
        tk = _than(vb, mo.end() - 1)
        if tk is None or not (mo.end() <= goi[0].start() <= tk[1]):
            return None, [f"het gio: `{ten}()` khong goi truc tiep tu OnTick - chua dich"]
        sau = vb[goi[0].end():].lstrip()
        if not sau.startswith(";"):
            return None, [f"het gio: `{ten}()` khong phai lenh don"]
        return int(n), [f"dong lenh o TICK DAU bar khi so bar tu bar vao >= {int(n)} "
                        f"(`{ten}`: iBarShift(POSITION_TIME) >= {int(n)} -> PositionClose)"]
    return None, []
