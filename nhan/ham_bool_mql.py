"""Ham `bool F()` KHONG tham so cua tac gia trong guard / loc thoat som (vong 6, 12/10/2026).

Vd `if(!IsSessionOK()) return;`, `if(CheckBuySignal()) trade.Buy(..)`. Truoc day ca lenh vao
bi bo vi `F()` khong phai phep so sanh. O day than ham duoc DOC (khong doan):

    bool IsSessionOK() {
       if(!UseSessionFilter) return true;          // dieu kien CHI tren input -> TINH bang gia tri
       MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
       if(SessionStartHour <= SessionEndHour)        //   input (mac dinh / .set tac gia)
          return (dt.hour >= SessionStartHour && dt.hour < SessionEndHour);
       return (dt.hour >= SessionStartHour || dt.hour < SessionEndHour);
    }

Than ham chi duoc chap nhan o dang tuan tu o muc ngoac ngoai cung:
  - `if(C) return true|false|X;` (hoac `{ return ..; }`), khong `else`;
  - cac lenh khai bao / gan cuc bo khong co `return`;
  - `return X;` cuoi cung.
Khong vong lap, khong switch, khong dat/dong lenh. `C` chi tren input/hang -> tinh ra
dung/sai bang gia tri input (giong `_hang_mql`); `C` khac phai co `return false` (thanh
"VA khong C") hoac la nhanh `return true` duy nhat roi moi duong sau deu `return false`
(thanh "VA C"). Ket qua: F = VA cua cac ve (pos, bieu thuc) / (neg, bieu thuc), dich tiep
bang chinh bo doc tai VI TRI cua bieu thuc trong than ham (bien cuc bo dung dinh nghia).
Khong khop dang -> None (lenh vao giu ly do cu, khong doan).
"""
from __future__ import annotations

import re

_TEN = r"[A-Za-z_]\w*"
_VB = {"vb": None, "mn": None, "ham": None, "input": {}, "cache": {}}
_CAM = re.compile(r"\b(?:for|while|do|switch|goto|static)\b|\b(?:OrderSend\w*|PositionOpen|"
                  r"PositionClose\w*|OrderClose|OrderDelete|OrderModify|PositionModify)\s*\(|"
                  r"\.(?:Buy|Sell|BuyLimit|SellLimit|BuyStop|SellStop|PositionOpen|"
                  r"PositionClose\w*|OrderOpen)\s*\(")


def _GH():
    from nhan import goi_ham_mql as GH
    return GH


def _D():
    from nhan import doc_ma as D
    return D


def dat_van_ban(vb: str, gia_tri_input: dict) -> None:
    """Goi o dau `_doc_chien_luoc_mql` (vb DA chuan hoa)."""
    GH = _GH()
    mn = GH.mat_na(vb)
    _VB.update(vb=vb, mn=mn, ham=None, input=dict(gia_tri_input), cache={})


def _bang_ham() -> dict:
    if _VB["ham"] is None:
        _VB["ham"] = _GH().ham_tu_do(_VB["mn"]) if _VB["mn"] else {}
    return _VB["ham"]


def _gia_tri(ten: str):
    v = _VB["input"].get(ten)
    if v is None:
        return None
    v = str(v).strip()
    if v in ("true", "false"):
        return v == "true"
    try:
        return float(v)
    except ValueError:
        return None


def tinh_input(c: str):
    """Bieu thuc chi gom input/hang so -> True/False; khac -> None."""
    s = c.strip()
    out = []
    for tk in re.findall(r"\d+\.\d*|\d*\.\d+|\d+|[A-Za-z_]\w*|&&|\|\||==|!=|<=|>=|[<>()!+\-*/]|\S", s):
        if re.fullmatch(r"\d+\.\d*|\d*\.\d+|\d+", tk):
            out.append(tk)
        elif tk in ("and", "or", "true", "false"):
            out.append({"true": "True", "false": "False"}.get(tk, tk))
        elif tk == "&&":
            out.append("and")
        elif tk == "||":
            out.append("or")
        elif tk == "!":
            out.append(" not ")
        elif tk in ("==", "!=", "<=", ">=", "<", ">", "(", ")", "+", "-", "*", "/"):
            out.append(tk)
        elif re.fullmatch(_TEN, tk):
            v = _gia_tri(tk)
            if v is None:
                return None
            out.append(repr(v))
        else:
            return None
    try:
        kq = eval(" ".join(out), {"__builtins__": {}}, {})   # noqa: S307 - chi so/toan tu da loc
    except Exception:                                        # noqa: BLE001
        return None
    return bool(kq) if isinstance(kq, (bool, int, float)) else None


def _lenh_return(mn: str, k: int, het: int):
    """Sau `)` cua if tai k: `return X;` hoac `{ return X; }` -> (X_tu, X_den, ket_thuc)."""
    D = _D()
    j = k + 1
    while j < het and mn[j] in " \t\r\n":
        j += 1
    ngoac = j < het and mn[j] == "{"
    if ngoac:
        dong = D._cuoi_khoi(mn, j)
        if dong < 0 or dong > het:
            return None
        m = re.fullmatch(r"\s*return\b([^;]*);\s*", mn[j + 1:dong])
        if not m:
            return None
        return j + 1 + m.start(1), j + 1 + m.end(1), dong + 1
    m = re.match(r"return\b([^;]*);", mn[j:het])
    if not m:
        return None
    return j + m.start(1), j + m.end(1), j + m.end()


def phan_tich(ten: str):
    """F() -> list[(kind, vi_tri, bieu_thuc)] kind in {"pos","neg"} (VA), hoac None."""
    if ten in _VB["cache"]:
        return _VB["cache"][ten]
    _VB["cache"][ten] = None                      # chan de quy
    ra = _phan_tich(ten)
    _VB["cache"][ten] = ra
    return ra


def _phan_tich(ten: str):
    D = _D()
    vb, mn = _VB["vb"], _VB["mn"]
    if not vb:
        return None
    ds = _bang_ham().get(ten) or []
    if len(ds) != 1:
        return None
    h = ds[0]
    if h["tham_so"].strip() not in ("", "void"):
        return None
    dau = _GH()._dau_khoi(mn, h["mo"])
    if not re.match(r"(?:inline\s+)?bool\s", dau):
        return None
    mo, dong = h["mo"], h["dong"]
    than = mn[mo + 1:dong]
    if _CAM.search(than):
        return None
    buoc = []                                     # ("if", c, cpos, x, xpos) / ("ret", x, xpos)
    i = mo + 1
    while i < dong:
        while i < dong and mn[i] in " \t\r\n;":
            i += 1
        if i >= dong:
            break
        m = re.match(r"if\s*\(", mn[i:dong])
        if m:
            a = i + m.end() - 1
            k = D._dong_ngoac(mn, a)
            if k < 0 or k >= dong:
                return None
            r = _lenh_return(mn, k, dong)
            if r is None:
                return None
            x0, x1, het = r
            if re.match(r"\s*else\b", mn[het:dong]):
                return None
            buoc.append(("if", vb[a + 1:k].strip(), a + 1, vb[x0:x1].strip(), x0))
            i = het
            continue
        m = re.match(r"return\b([^;]*);", mn[i:dong])
        if m:
            # lenh sau `return` vo dieu kien = ma chet (bo chuan hoa da gap san `if(input)`)
            buoc.append(("ret", vb[i + m.start(1):i + m.end(1)].strip(), i + m.start(1)))
            break
        if mn[i] == "{" or re.match(r"(?:else|case|default)\b", mn[i:dong]):
            return None
        j = mn.find(";", i, dong)
        if j < 0 or "return" in mn[i:j] or "{" in mn[i:j]:
            return None
        i = j + 1
    if not buoc or buoc[-1][0] != "ret":
        return None
    T = []
    for n, b in enumerate(buoc):
        if b[0] == "ret":
            x, xp = b[1], b[2]
            x_ = D._boc_ngoac(x)
            if x_ == "true":
                return T
            if x_ == "false":
                return None                       # luon sai -> khong co lenh: khong dich
            return T + [("pos", xp, x)]
        _, c, cp, x, xp = b
        v = tinh_input(c)
        x_ = D._boc_ngoac(x)
        if v is False:
            continue
        if v is True:
            if x_ == "true":
                return T
            if x_ == "false":
                return None
            return T + [("pos", xp, x)]
        if x_ == "false":
            T.append(("neg", cp, c))
            continue
        if x_ == "true":
            sau = buoc[n + 1:]
            if all(D._boc_ngoac(s[3] if s[0] == "if" else s[1]) == "false" for s in sau):
                return T + [("pos", cp, c)]
            return None
        return None                               # `if(C) return X;` X la bieu thuc: OR -> chua
    return None


RX_GOI = re.compile(rf"\s*\(?\s*(!\s*)?({_TEN})\s*\(\s*\)\s*\)?\s*")


# ---------------------------------------------------------------------------
# LOC TRANG THAI TAI KHOAN / NHIP LENH (vong 6): gioi han lenh/ngay, lo/ngay, dung giao dich
# sau khi lo, gian cach giua hai lenh. Day la QUAN TRI RUI RO cua tai khoan, khong phai tin
# hieu gia: bo doc BO QUA (ghi ro o `bo_qua_quan_tri` + `gia_dinh`), giong `cntBuy==0`.
# Mo phong vi the/lan nen co the vao NHIEU hon EA vao nhung ngay da cham gioi han.
# Chi bien DUOC CHUNG MINH la trang thai moi tinh (khong doan theo ten bien):
#   (a) bien dem lenh: co `x = 0` va `x++`/`x += 1` ma lenh tang nam trong khoi CO lenh dat
#       lenh, hoac trong OnTrade/OnTradeTransaction, hoac trong vong duyet lich su lenh;
#   (b) bien tien: MOI phep gan deu dung API tai khoan/lich su (Equity, Balance, Profit,
#       HistoryDeal*) hoac bien (b) khac;
#   (c) co bool: MOI `x = true` nam trong khoi `if` co dieu kien chua API/bien (a)(b);
#   (d) moc thoi gian vao lenh: bien datetime gan TimeCurrent()/iTime trong khoi co dat lenh.
# ---------------------------------------------------------------------------
_RX_TK = re.compile(r"\bAccountInfo(?:Double|Integer)\b|\bAccount(?:Balance|Equity|Profit|FreeMargin)"
                    r"\s*\(|\.(?:Equity|Balance|Profit|FreeMargin|Margin)\s*\(\s*\)|\bHistory\w+|"
                    r"\bOrdersHistoryTotal\b|\bACCOUNT_(?:BALANCE|EQUITY|PROFIT|MARGIN\w*)\b")
_RX_DAT_LENH = re.compile(r"\b(?:OrderSend\w*|PositionOpen)\s*\(|\.(?:Buy|Sell|BuyLimit|SellLimit|"
                          r"BuyStop|SellStop|PositionOpen|OrderOpen)\s*\(")


def _khoi_bao_quanh(mn: str, vi: int) -> tuple[int, int]:
    """Khoi `{..}` hep nhat chua vi."""
    D = _D()
    muc = 0
    for i in range(vi - 1, -1, -1):
        c = mn[i]
        if c == "}":
            muc += 1
        elif c == "{":
            if muc == 0:
                return i, D._cuoi_khoi(mn, i)
            muc -= 1
    return 0, len(mn)


def _dau_if(mn: str, mo: int) -> str | None:
    """Dieu kien `if(..)` ngay truoc `{` tai mo (khong co -> None)."""
    D = _D()
    j = mo - 1
    while j >= 0 and mn[j] in " \t\r\n":
        j -= 1
    if j < 0 or mn[j] != ")":
        return None
    muc = 0
    for a in range(j, -1, -1):
        if mn[a] == ")":
            muc += 1
        elif mn[a] == "(":
            muc -= 1
            if muc == 0:
                if re.search(r"\bif\s*$", mn[:a]):
                    return mn[a + 1:j]
                return None
    return None


def bien_trang_thai(vb: str, mn: str | None = None) -> set:
    mn = mn or _GH().mat_na(vb)
    ham = _GH().ham_tu_do(mn)
    ten_ham = {}
    for t, ds in ham.items():
        for h in ds:
            ten_ham[(h["mo"], h["dong"])] = t

    def ham_chua(vi):
        for (a, b), t in ten_ham.items():
            if a < vi < b:
                return t, a, b
        return None, 0, len(mn)

    ra = set()
    # (a) bien dem lenh
    for m in re.finditer(rf"(?<![\w.])({_TEN})\s*(?:\+\+|\+=\s*1\b)|\+\+\s*({_TEN})\b", mn):
        x = m.group(1) or m.group(2)
        if x in ra or not re.search(rf"(?<![\w.]){x}\s*=\s*0\s*;", mn):
            continue
        a, b = _khoi_bao_quanh(mn, m.start())
        t, ha, hb = ham_chua(m.start())
        if t is None:
            continue
        # lenh dat lenh TRUOC lenh tang, trong CUNG khoi hep nhat (`if(trade.Buy(..)) n++;`,
        # `ok = trade.Buy(..); if(ok) n++;`) - khong phai moi `n++` trong ham co lenh
        if _RX_DAT_LENH.search(mn[a:m.start()]) or t in ("OnTrade", "OnTradeTransaction") or \
                re.search(r"\bfor\s*\([^;]*;[^;]*\b(?:HistoryDealsTotal|OrdersHistoryTotal)\b",
                          mn[ha:m.start()]):
            # vong lap thuong (`for(i..;i++)`) khong phai bien dem lenh
            if re.match(r"\s*\)", mn[m.end():]) and re.search(r"\bfor\s*\([^)]*$", mn[a:m.start()]):
                continue
            ra.add(x)
    # (b) bien tien (lap toi dong) + (d) moc thoi gian vao lenh + (c) co bool
    gan_ds: dict = {}
    for g in re.finditer(rf"(?<![\w.])({_TEN})\s*(?:[-+*/]?=)(?!=)\s*([^;]*);", mn):
        gan_ds.setdefault(g.group(1), []).append((g.start(), g.group(2)))
    dt_bien = set(re.findall(rf"\bdatetime\s+({_TEN})\b", mn))
    co_bool = set(re.findall(rf"\bbool\s+({_TEN})\s*(?:=\s*false\s*)?;", mn))
    doi = True
    while doi:
        doi = False
        for x, gan in gan_ds.items():
            if x in ra:
                continue
            rhs = [g for _, g in gan]

            def ok(g):
                if _RX_TK.search(g):
                    return True
                tn = set(re.findall(_TEN, g)) - {"double", "int", "long"}
                return (bool(tn) and tn <= (ra | {x})) or g.strip() in ("0", "0.0")
            if all(ok(g) for g in rhs) and any(_RX_TK.search(g) or (set(re.findall(_TEN, g)) & ra)
                                               for g in rhs):
                ra.add(x)
                doi = True
                continue
            if x in dt_bien:
                vi = [v for v, g in gan if re.fullmatch(r"\s*(?:TimeCurrent\s*\(\s*\)|iTime\s*\([^;]*\))\s*", g)]
                if vi and all(_RX_DAT_LENH.search(mn[slice(*_khoi_bao_quanh(mn, v))]) for v in vi):
                    ra.add(x)
                    doi = True
                    continue
            if x in co_bool:
                tv = [v for v, g in gan if g.strip() == "true"]
                if not tv:
                    continue
                tot = True
                for v in tv:
                    a_, _ = _khoi_bao_quanh(mn, v)
                    dk = _dau_if(mn, a_)
                    if dk is None or not (_RX_TK.search(dk) or set(re.findall(_TEN, dk)) & ra):
                        tot = False
                        break
                if tot:
                    ra.add(x)
                    doi = True
    return ra


_TT = {"vb": None, "ra": set()}


def la_trang_thai(p: str, input_: dict) -> bool:
    """Ve `p` chi tren API tai khoan / bien trang thai / input / so / TimeCurrent()."""
    vb = _VB["vb"]
    if not vb:
        return False
    if _TT["vb"] is not vb:
        _TT.update(vb=vb, ra=bien_trang_thai(vb, _VB["mn"]))
    tn = set(re.findall(_TEN, p)) - {"and", "or", "true", "false", "TimeCurrent", "double", "int"}
    if not tn:
        return False
    co = _RX_TK.search(p) or (tn & _TT["ra"])
    if not co:
        return False
    du = {x for x in tn if x not in _TT["ra"] and x not in input_ and not _RX_TK.search(x)
          and not re.fullmatch(r"ACCOUNT_\w+|_Symbol|Symbol|MathAbs|NormalizeDouble|"
                               r"AccountInfoDouble|AccountInfoInteger", x)}
    return not du
