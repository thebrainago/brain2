# -*- coding: utf-8 -*-
"""Tien xu ly ma EA truoc bo doc (vong 27). Chi bien doi NGU NGHIA TUONG DUONG hoac gia dinh GHI RO:
1. kiem_tai_nguyen: loi goi kiem ky quy/khoi luong/tien (CheckMargin, CheckVolumeValue, CheckMoneyForTrade...)
   -> `true` (mo phong khong mo hinh ky quy; gia dinh ghi vao 'gia_dinh').
2. IsNewBar/IsNewCandle() -> `true` (bo mo phong da chay theo bar dong) - gia dinh.
3. ham co tham so bool nhan bieu thuc: `F(expr)` dung mot minh lam cau lenh -> `if(expr) F(true); else F(false);`
4. chuyen biet hoa: ham co tham so ma moi cho goi deu la hang -> nhan ban F__k voi tham so thay hang (thay tu, ranh gioi tu).
5. OnTimer: neu khong co OnTick (hoac OnTick rong) va OnTimer co lenh dat lenh -> doi ten OnTimer thanh OnTick (gia dinh timer ~ moi tick).
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
    # 5. OnTimer
    H = _ham(vb)
    if "OnTimer" in H:
        ot = H.get("OnTick"); tb = vb[ot[3]:ot[1]] if ot else ""
        s, e, _, b = H["OnTimer"]
        if (not ot or not re.search(r"\w+\s*\(", tb)) and (_DAT.search(vb[b:e]) or re.search(r"\b(Open|Buy|Sell|Trade)\w*\s*\(", vb[b:e])):
            if ot: vb = vb[:ot[0]] + vb[ot[1]:]
            vb = re.sub(r"\bvoid\s+OnTimer\s*\(", "void OnTick(", vb, count=1); log.append("OnTimer->OnTick (gia dinh: timer ~ moi bar)")
    return vb, log
