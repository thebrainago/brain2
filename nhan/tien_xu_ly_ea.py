# -*- coding: utf-8 -*-
"""Tien xu ly ma EA truoc bo doc (vong 27). Chi bien doi NGU NGHIA TUONG DUONG hoac gia dinh GHI RO:
1. kiem_tai_nguyen: loi goi kiem ky quy/khoi luong/tien (CheckMargin, CheckVolumeValue, CheckMoneyForTrade...)
   -> `true` (mo phong khong mo hinh ky quy; gia dinh ghi vao 'gia_dinh').
2. IsNewBar/IsNewCandle() -> `true` (bo mo phong da chay theo bar dong) - gia dinh.
3. ham co tham so bool nhan bieu thuc: `F(expr)` dung mot minh lam cau lenh -> `if(expr) F(true); else F(false);`
4. chuyen biet hoa: ham co tham so ma moi cho goi deu la hang -> nhan ban F__k voi tham so thay hang (thay tu, ranh gioi tu).
5. OnTimer: neu khong co OnTick (hoac OnTick rong) va OnTimer co lenh dat lenh -> doi ten OnTimer thanh OnTick (gia dinh timer ~ moi tick).
6. (chu ky 3 vong 27) chieu lenh qua bien hang cuc bo - TUONG DUONG ngu nghia:
   a. gap ba ngoi hang `true ? A : B` -> A (A, B la toan hang don);
   b. bien cuc bo gan DUNG MOT LAN bang hang chieu (`ENUM_ORDER_TYPE t = ORDER_TYPE_BUY;`) -> thay vao doi so lenh dat;
   c. `MqlTradeRequest r; r.type = ORDER_TYPE_BUY;` (gan dung mot lan trong ham) -> danh dau chieu tren `OrderSend(r, res)`
      bang chu thich `/*ORDER_TYPE_BUY*/` (bo doc doc chieu tu doi so lenh).
7. (chu ky 3 vong 27) lenh vao trong nhanh `else` (khong phai `else if`): `if(A) S1 else S2` voi S2 chua lenh dat
   (truc tiep hoac qua mot ham co lenh dat) -> `if(A) S1 if(!(A)) S2`. Gia dinh (ghi log): S1 khong doi gia tri A
   trong cung tick (luat bo doc la dieu kien tren bar, khong mo phong thu tu cau lenh). A co gan/goi lenh -> bo qua.
Tra (van_ban_moi, danh_sach_bien_doi)."""
from __future__ import annotations
import re

_KIEM = re.compile(r"\b(Check(?:Margin|Volume\w*|Money\w*|Lot\w*|FreeMargin\w*)|IsEnoughMoney|EnoughMargin)\s*\(")
_MOI = re.compile(r"\b(IsNew(?:Bar|Candle)\w*)\s*\(\s*\)")
_DAT = re.compile(r"\b(OrderSend|PositionOpen|\.Buy|\.Sell|trade\.\w+Open|BuyOpen|SellOpen)\s*\(")
_HAM = re.compile(r"\b(?:void|bool|int|double|ulong|long)\s+([A-Za-z_]\w*)\s*\(([^()]*)\)\s*\{")


def _dong(vb, i, mo="(", dg=")"):
    d = 0
    for j in range(i, len(vb)):
        if vb[j] == mo: d += 1
        elif vb[j] == dg:
            d -= 1
            if d == 0: return j
    return -1


def _ham(vb):
    out = {}
    for m in _HAM.finditer(vb):
        b = m.end() - 1; e = _dong(vb, b, "{", "}")
        if e > 0: out.setdefault(m.group(1), (m.start(), e + 1, m.group(2), b))
    return out


def _thay_goi(vb, rx, thay):
    out, i = [], 0
    for m in rx.finditer(vb):
        if m.start() < i: continue
        p = vb.find("(", m.start()); e = _dong(vb, p)
        if e < 0: continue
        dau = vb[max(0, m.start() - 40):m.start()]
        if re.search(r"\b(bool|int|double|void)\s+$", dau): continue  # dinh nghia, khong phai loi goi
        out.append(vb[i:m.start()]); out.append(thay); i = e + 1
    out.append(vb[i:]); return "".join(out)


_HANG = re.compile(r"^\s*(true|false|-?\d+(\.\d+)?|ORDER_TYPE_\w+|OP_\w+|POSITION_TYPE_\w+|\"[^\"]*\")\s*$")


def _tach(s):
    o, d, c = [], 0, ""
    for ch in s:
        if ch in "([": d += 1
        if ch in ")]": d -= 1
        if ch == "," and d == 0: o.append(c); c = ""
        else: c += ch
    if c.strip(): o.append(c)
    return [x.strip() for x in o]


def _ten_ts(ts):
    o = []
    for p in _tach(ts):
        p = p.split("=")[0].strip(); m = re.search(r"([A-Za-z_]\w*)\s*(\[\])?$", p.replace("&", " "))
        if m: o.append((m.group(1), "bool" in p.split()))
    return o


def bien_doi(vb: str):
    log = []
    if _KIEM.search(vb):
        n = len(_KIEM.findall(vb)); vb = _thay_goi(vb, _KIEM, "true"); log.append(f"kiem_tai_nguyen->true x{n} (gia dinh: du ky quy)")
    if _MOI.search(vb):
        vb2 = re.sub(r"(?<![\w\s])(\s*)" + _MOI.pattern, r"\1true", vb)
        vb2 = re.sub(r"(if\s*\(\s*!?\s*)" + _MOI.pattern, lambda m: m.group(1) + "true", vb)
        if vb2 != vb: vb = vb2; log.append("IsNewBar()->true (gia dinh: mo phong theo bar)")
    H = _ham(vb)
    # 3. bool tham so voi bieu thuc -> if/else
    for ten, (_, _, ts, _) in H.items():
        tn = _ten_ts(ts)
        if len(tn) != 1 or not tn[0][1]: continue
        rx = re.compile(r"(^|[;{})]\s*)" + re.escape(ten) + r"\s*\(")
        def f(m):
            return m.group(0)
        out, i, n = [], 0, 0
        for m in rx.finditer(vb):
            p = vb.find("(", m.end() - 1); e = _dong(vb, p)
            if e < 0 or not vb[e + 1:].lstrip().startswith(";"): continue
            a = vb[p + 1:e].strip()
            if _HANG.match(a) or not a: continue
            sc = vb.index(";", e)
            out.append(vb[i:m.end() - len(ten) - 1 - (len(m.group(0)) - len(m.group(1)) - len(ten) - 1)] if False else vb[i:m.start() + len(m.group(1))])
            out.append(f"{{if({a}) {ten}(true); else {ten}(false);}}"); i = sc + 1; n += 1
        if n: out.append(vb[i:]); vb = "".join(out); log.append(f"{ten}(bieu_thuc bool)->if/else x{n}")
    # 4. chuyen biet hoa theo cho goi hang
    H = _ham(vb)
    for ten, (s, e, ts, b) in sorted(H.items(), key=lambda x: -x[1][0]):
        tn = _ten_ts(ts)
        if not tn or ten in ("OnTick", "OnInit", "OnDeinit", "OnTimer", "start", "init", "deinit"): continue
        rx = re.compile(r"(?<![\w.])" + re.escape(ten) + r"\s*\(")
        goi = []
        for m in rx.finditer(vb):
            if s <= m.start() < b: continue
            p = vb.find("(", m.start()); q = _dong(vb, p)
            if q < 0: break
            a = _tach(vb[p + 1:q])
            if len(a) != len(tn) or not all(_HANG.match(x) for x in a): goi = None; break
            goi.append((m.start(), q + 1, tuple(a)))
        if not goi or not _DAT.search(vb[b:e]): continue
        khac = sorted(set(g[2] for g in goi))
        than = vb[b:e]; moi = []
        for k, a in enumerate(khac):
            t = than
            for (nm, _), v in zip(tn, a): t = re.sub(r"(?<![\w.])" + nm + r"(?!\w)", v, t)
            moi.append(f"\nvoid {ten}__{k}() {t}\n")
        out, i = [], 0
        for (p0, p1, a) in sorted(goi):
            out.append(vb[i:p0]); out.append(f"{ten}__{khac.index(a)}()"); i = p1
        out.append(vb[i:]); vb2 = "".join(out)
        vb = vb2 + "".join(moi); log.append(f"chuyen_biet {ten} x{len(khac)}")
    # gap hang: so sanh hai hang sau chuyen biet
    def _so(m):
        a, op, c = m.group(1), m.group(2), m.group(3)
        return "true" if (a == c) == (op == "==") else "false"
    vb2 = re.sub(r"\b((?:ORDER_TYPE|OP|POSITION_TYPE)_\w+|true|false)\s*(==|!=)\s*((?:ORDER_TYPE|OP|POSITION_TYPE)_\w+|true|false)\b", _so, vb)
    vb2 = re.sub(r"!\s*true\b", "false", re.sub(r"!\s*false\b", "true", vb2))
    if vb2 != vb: vb = vb2; log.append("gap_hang so sanh hang")
    vb, l6 = _chieu_hang(vb); log += l6
    vb, l7 = _else_thanh_if(vb); log += l7
    # 5. OnTimer
    H = _ham(vb)
    if "OnTimer" in H:
        ot = H.get("OnTick"); tb = vb[ot[3]:ot[1]] if ot else ""
        s, e, _, b = H["OnTimer"]
        if (not ot or not re.search(r"\w+\s*\(", tb)) and (_DAT.search(vb[b:e]) or re.search(r"\b(Open|Buy|Sell|Trade)\w*\s*\(", vb[b:e])):
            if ot: vb = vb[:ot[0]] + vb[ot[1]:]
            vb = re.sub(r"\bvoid\s+OnTimer\s*\(", "void OnTick(", vb, count=1); log.append("OnTimer->OnTick (gia dinh: timer ~ moi bar)")
    return vb, log


_CHIEU = r"(?:ORDER_TYPE_BUY|ORDER_TYPE_SELL|OP_BUY|OP_SELL|POSITION_TYPE_BUY|POSITION_TYPE_SELL)"
_DON = r"(?:[A-Za-z_][\w.]*(?:\[[^\[\]]*\])?(?:\([^()?:;]*\))?|-?\d+(?:\.\d+)?)"
_BA_NGOI = re.compile(r"(\(\s*(?:true|false)\s*\)|\b(?:true|false))\s*\?\s*(" + _DON + r")\s*:\s*(" + _DON + r")(?=\s*[;,)])")
_GOI_DAT = re.compile(r"\b(OrderSend|PositionOpen|OrderOpen)\s*\(")


def _gan_lai(than, ten, bo_khai=None):
    """So lan bien `ten` bi gan (=, +=, ++, truyen &) trong than ham, tru dong khai bao bo_khai."""
    n = 0
    for m in re.finditer(r"(?<![\w.])" + re.escape(ten) + r"\s*(=(?!=)|\+=|-=|\*=|/=|\|=|&=|\+\+|--)", than):
        if bo_khai is not None and m.start() == bo_khai: continue
        n += 1
    n += len(re.findall(r"(\+\+|--)\s*" + re.escape(ten) + r"\b", than))
    return n


def _chieu_hang(vb):
    log = []
    # a. ba ngoi hang
    n = 0
    def _bn(m):
        nonlocal n; n += 1
        return m.group(2) if "true" in m.group(1) else m.group(3)
    vb = _BA_NGOI.sub(_bn, vb)
    if n: log.append(f"gap_ba_ngoi_hang x{n}")
    H = _ham(vb); sua = []
    for ten, (s, e, ts, b) in H.items():
        than = vb[b:e]; t2 = than; nb = nc = 0
        # b. bien cuc bo hang chieu
        for m in re.finditer(r"\b(?:ENUM_ORDER_TYPE|ENUM_POSITION_TYPE|int|long)\s+([A-Za-z_]\w*)\s*=\s*(" + _CHIEU + r")\s*;", than):
            v, c = m.group(1), m.group(2)
            if _gan_lai(than, v, bo_khai=than.find(v, m.start())) or re.search(r"&\s*" + v + r"\b", than): continue
            out, i = [], 0
            for g in _GOI_DAT.finditer(t2):
                p = t2.find("(", g.start()); q = _dong(t2, p)
                if q < 0: continue
                a = re.sub(r"(?<![\w.])" + v + r"(?!\w)", c, t2[p:q + 1])
                if a != t2[p:q + 1]: out.append(t2[i:p]); out.append(a); i = q + 1; nb += 1
            out.append(t2[i:]); t2 = "".join(out)
        # c. MqlTradeRequest .type gan mot lan
        for r in set(re.findall(r"\bMqlTradeRequest\s+([A-Za-z_]\w*)", t2)) | set(re.findall(r"\bMqlTradeRequest\s*&\s*([A-Za-z_]\w*)", ts)):
            gan = re.findall(r"(?<![\w.])" + r + r"\.type\s*=(?!=)\s*([^;]+);", t2)
            if len(gan) != 1 or not re.fullmatch(r"\s*(ORDER_TYPE_BUY|ORDER_TYPE_SELL)\s*", gan[0]): continue
            c = gan[0].strip()
            out, i = [], 0
            for g in re.finditer(r"\bOrderSend\s*\(\s*" + r + r"\s*,", t2):
                p = t2.find("(", g.start()); q = _dong(t2, p)
                if q < 0 or "ORDER_TYPE_" in t2[p:q]: continue
                out.append(t2[i:q]); out.append(f" /*{c}*/"); i = q; nc += 1
            out.append(t2[i:]); t2 = "".join(out)
        if t2 != than: sua.append((b, e, t2, ten, nb, nc))
    for b, e, t2, ten, nb, nc in sorted(sua, key=lambda x: -x[0]):
        vb = vb[:b] + t2 + vb[e:]
        if nb: log.append(f"bien_hang_chieu {ten} x{nb}")
        if nc: log.append(f"request_type_hang {ten} x{nc}")
    return vb, log


def _cau_lenh(vb, i):
    """Tu vi tri i (dau cau lenh), tra vi tri SAU cau lenh, hoac -1 neu khong chac (if/for/while long khong ngoac)."""
    m = re.compile(r"\s*").match(vb, i); j = m.end()
    if j >= len(vb): return -1
    if vb[j] == "{":
        e = _dong(vb, j, "{", "}"); return e + 1 if e > 0 else -1
    if re.match(r"(if|for|while|switch|do|else)\b", vb[j:j + 7]): return -1
    k = j; d = 0
    while k < len(vb):
        ch = vb[k]
        if ch == "(": d += 1
        elif ch == ")": d -= 1
        elif ch == ";" and d == 0: return k + 1
        elif ch in "{}" and d == 0: return -1
        k += 1
    return -1


def _else_thanh_if(vb):
    H = _ham(vb)
    co_dat = {t for t, (s0, e0, _, b0) in H.items() if _DAT.search(vb[b0:e0])}
    rx_goi = re.compile(r"(?<![\w.])(" + "|".join(map(re.escape, co_dat)) + r")\s*\(") if co_dat else None
    n, pos = 0, 0
    rx_if = re.compile(r"(?<![\w.])if\s*\(")
    while n < 50:
        m = rx_if.search(vb, pos)
        if not m: break
        pos = m.end()
        # if phai la cau lenh doc lap: truoc no la `;`, `{`, `}` (khong phai than cua if/for/while/else khong ngoac)
        an = re.sub(r"//[^\n]*|/\*.*?\*/", lambda z: " " * len(z.group(0)), vb[max(0, m.start() - 2000):m.start()], flags=re.S)
        an = an.rstrip()
        if an and an[-1] not in ";{}": continue
        p = m.end() - 1; q = _dong(vb, p)
        if q < 0: continue
        a = vb[p + 1:q]
        e1 = _cau_lenh(vb, q + 1)
        if e1 < 0: continue
        me = re.compile(r"\s*else\b(?!\s*if\b)").match(vb, e1)
        if not me: continue
        e2 = _cau_lenh(vb, me.end())
        if e2 < 0: continue
        s2 = vb[me.end():e2]
        if not (_DAT.search(s2) or (rx_goi and rx_goi.search(s2))): continue
        if re.search(r"(?<![=!<>])=(?!=)|\+\+|--|OrderSend|PositionOpen|\.Buy|\.Sell", a): continue
        moi = f" if(!({a.strip()}))"
        vb = vb[:e1] + moi + vb[me.end():]
        n += 1
    return vb, ([f"else->if(!A) x{n} (gia dinh: nhanh truoc khong doi A cung tick)"] if n else [])
