# -*- coding: utf-8 -*-
"""HUONG INT MQL - ham tin hieu tra HUONG so nguyen (+1 / -1 / 0) (them 11/10/2026).

Do tren tap "cho bo doc" cua SEEKER: EA viet

    int GetSignal(double &atr){ ...
       if(fast[0] > slow[0] && fast[1] <= slow[1]) return  1;
       if(fast[0] < slow[0] && fast[1] >= slow[1]) return -1;
       return 0; }
    void OnTick(){ ... int signal = GetSignal(atr); if(signal == 0) return; ...
       OpenPosition(signal, atr); }
    void OpenPosition(const int signal, ...){ bool isBuy = (signal > 0); ...
       bool ok = isBuy ? trade.Buy(..) : trade.Sell(..); }

Bo doc cu thay guard `isBuy` / `signal == 0` (co chon nhanh thuan) va hai tang dieu kien
-> tu choi. File nay chung minh, KHONG doan, rang lenh vao chieu `c` chay KHI VA CHI KHI
ham tin hieu F tra dung MOT gia tri s* (+1 hoac -1), roi tra dieu kien de F tra s*
(nam trong than F, dich bang duong dich guard cu cua `doc_ma`).

Dieu kien nhan (thieu mot -> tu choi CO LY DO, hoac None neu khong phai dang nay):
  1. F la ham tu do kieu so nguyen, dinh nghia mot lan. Than F, o MUC NGOAI CUNG, chi gom:
     lenh khong co `return`; `if(C) return 0;` (thoat som); `if(C) return +-1;` (dang R,
     ket thuc bang `return 0;`) HOAC `if(C) d = +-1;` voi `int d = 0;` (dang V, ket thuc
     `return d;`, `d` khong duoc dung o cho nao khac). Moi chieu toi da MOT dieu kien (hai
     cho tra +1 = OR -> tu choi). Khong `else`, khong `return` trong vong lap / khoi long.
     Tham so (khong tham chieu `&`) cua F khong duoc nam trong dieu kien.
  2. Chuoi goi tu ham chua lenh vao len `OnTick` dung luat `goi_ham_mql` (mot cho goi,
     lenh don, khong else, toi da 4 tang).
  3. Moi dieu kien tren chuoi (if bao, thoat som `if(X) return;`, nhanh ba ngoi chon lenh)
     hoac la QUAN TRI / kiem loi (bo qua co ghi), hoac la BIEU THUC HUONG: chi gom ten, so
     nguyen, so sanh, `!`, `&&`, `||` tren cac bien GIAI DUOC ve gia tri F: bien cuc bo gan
     DUNG MOT lan (`int sig = F(..);`, `bool isBuy = (sig > 0);`) o muc than ham truoc cho
     dung, hoac tham so nhan doi so tu cho goi duy nhat. Bien do khong xuat hien o cho khac.
  4. Thu ba gia tri s in {+1, -1, 0}: lenh vao chay voi DUNG MOT s* khac 0.
  5. Dang R, s* = -1 dung SAU `if(A) return 1;` (hoac dang V, nhanh gan truoc bi GHI DE boi
     nhanh sau): can chung minh loai tru (A va B mau thuan) - viec nay `doc_ma` lam (co bang
     ky hieu); file nay tra `loai_tru` = cac dieu kien can loai tru.
"""
from __future__ import annotations

import re

from nhan import goi_ham_mql as GH

_TEN = r"[A-Za-z_][A-Za-z0-9_]*"
_KIEU_NGUYEN = r"(?:static\s+)?(?:int|long|short|char|ENUM_\w+)"
_SO_HUONG = {"1": 1, "+1": 1, "-1": -1, "0": 0}
TANG_TOI_DA = 4


def _D():
    from nhan import doc_ma as D                  # tre: tranh vong import
    return D


def _gia_tri_return(x: str) -> int | None:
    """`return 1;` / `return(-1);` / `return (0);` -> so; khac -> None."""
    m = re.fullmatch(r"return\s*\(?\s*([-+]?\s*\d+)\s*\)?\s*;", x.strip())
    if not m:
        return None
    return _SO_HUONG.get(m.group(1).replace(" ", ""))


# ------------------------------------------------------------- ham tin hieu F ----
def ham_huong(vb: str, ten: str) -> dict | str | None:
    """Doc ham tin hieu `ten`. Tra {s: {"guard", "vi", "thoat", "loai_tru"}} cho s = +1/-1
    (chi chieu co), chuoi ly do khi dung la ham huong nhung khong chac, None khi khong phai."""
    D = _D()
    mn = GH.mat_na(vb)
    bang = GH.ham_tu_do(mn)
    ds = bang.get(ten)
    if not ds:
        return None
    if len(ds) > 1:
        return f"ham huong {ten} dinh nghia {len(ds)} lan"
    h = ds[0]
    dau = re.sub(r"\s+", " ", GH._dau_khoi(mn, h["mo"]))
    if not re.match(_KIEU_NGUYEN + r"\s", dau):
        return None
    than = vb[h["mo"] + 1:h["dong"]]
    than_mn = mn[h["mo"] + 1:h["dong"]]
    lenh = D._tach_lenh(than_mn)
    if not lenh:
        return None
    # vi tri tung lenh trong vb (than_mn cung do dai voi than)
    vi, tu = [], 0
    for x in lenh:
        k = than_mn.find(x, tu)
        if k < 0:
            return None
        vi.append(h["mo"] + 1 + k)
        tu = k + len(x)
    tham = [p.strip() for p in h["tham_so"].split(",") if p.strip()]
    ten_tham = set()
    for p in tham:
        mp = re.search(rf"({_TEN})\s*(?:=.*)?$", p)
        if mp and "&" not in p:
            ten_tham.add(mp.group(1))
    cuoi = lenh[-1].strip()
    gt_cuoi = _gia_tri_return(cuoi)
    dang, bien_d = None, None
    if gt_cuoi == 0:
        dang = "R"
    else:
        mv = re.fullmatch(rf"return\s*\(?\s*({_TEN})\s*\)?\s*;", cuoi)
        if not mv:
            return None
        dang, bien_d = "V", mv.group(1)
    su_kien = []                                  # (loai, s, dk, vi)
    thay_d0 = False
    for x, p in zip(lenh[:-1], vi[:-1]):
        xs = x.strip()
        if dang == "V" and re.fullmatch(rf"(?:{_KIEU_NGUYEN}\s+)?{bien_d}\s*=\s*0\s*;", xs):
            if thay_d0:
                return f"ham huong {ten}: gan {bien_d} = 0 hai lan"
            thay_d0 = True
            continue
        mi = re.match(r"if\s*\(", xs)
        if mi:
            a = p + mi.end() - 1
            k = D._dong_ngoac(vb, a)
            if k < 0:
                return f"ham huong {ten}: ngoac lech"
            dk = vb[a + 1:k].strip()
            sau = mn[k + 1:p + len(x)].strip()
            if re.search(r"\belse\b", sau):
                return f"ham huong {ten}: co nhanh else"
            if dang == "V" and re.search(rf"\b{bien_d}\b", dk):
                return f"ham huong {ten}: dieu kien dung bien huong {bien_d}"
            lt = D._lenh_thoat(vb, k)
            if lt is not None and lt[0] <= p + len(x):
                mr = re.search(r"return\b[^;]*;", vb[k + 1:lt[0]])
                g = _gia_tri_return(mr.group(0)) if mr else None
                if g is None:
                    return f"ham huong {ten}: return khong phai 0/+1/-1: {vb[k + 1:lt[0]].strip()[:30]}"
                if dang == "V" and g != 0:
                    return f"ham huong {ten}: tron return +-1 voi bien huong"
                su_kien.append(("thoat" if g == 0 else "tra", g, dk, p))
                continue
            if dang == "V":
                mg = re.fullmatch(rf"\{{?\s*{bien_d}\s*=\s*([-+]?\s*\d+)\s*;\s*\}}?", sau)
                if mg and mg.group(1).replace(" ", "") in ("1", "+1", "-1"):
                    su_kien.append(("gan", _SO_HUONG[mg.group(1).replace(" ", "")], dk, p))
                    continue
            if re.search(r"\breturn\b", x):
                return f"ham huong {ten}: return trong khoi long"
            if dang == "V" and re.search(rf"\b{bien_d}\b", x):
                return f"ham huong {ten}: bien huong {bien_d} dung trong dieu kien/khoi khac"
            continue
        if re.search(r"\breturn\b", x):
            return f"ham huong {ten}: return trong vong lap/khoi"
        if dang == "V" and re.search(rf"\b{bien_d}\b", x):
            return f"ham huong {ten}: bien huong {bien_d} dung o lenh khac"
    if dang == "V" and not thay_d0:
        return None
    ra: dict = {}
    for s in (1, -1):
        loai = "tra" if dang == "R" else "gan"
        cung = [e for e in su_kien if e[0] == loai and e[1] == s]
        if not cung:
            continue
        if len(cung) > 1:
            return f"ham huong {ten}: {len(cung)} dieu kien cho {s:+d} (OR) - chua dich"
        _, _, dk, p = cung[0]
        if ten_tham and any(re.search(rf"\b{re.escape(t)}\b", dk) for t in ten_tham):
            return f"ham huong {ten}: dieu kien dung tham so ham"
        if dang == "R":
            thoat = [e[2] for e in su_kien if e[0] == "thoat" and e[3] < p]
            loai_tru = [(e[2], e[3]) for e in su_kien if e[0] == "tra" and e[1] != s and e[3] < p]
        else:
            thoat = [e[2] for e in su_kien if e[0] == "thoat"]
            loai_tru = [(e[2], e[3]) for e in su_kien if e[0] == "gan" and e[1] != s and e[3] > p]
        if any(ten_tham and re.search(rf"\b{re.escape(t)}\b", x) for x in thoat for t in ten_tham):
            return f"ham huong {ten}: thoat som dung tham so ham"
        ra[s] = {"guard": dk, "vi": p, "thoat": thoat, "loai_tru": loai_tru,
                 "goc": h["mo"], "dang": dang}
    if not ra:
        return None
    return ra


# ---------------------------------------------------------------- bieu thuc huong ----
_RX_TOKEN = re.compile(r"\s*(?:(\d+)|([A-Za-z_]\w*)|(&&|\|\||==|!=|>=|<=|>|<|!|\(|\)|\+|-))")


def _sang_py(bt: str) -> str | None:
    """Bieu thuc huong MQL -> Python (chi ten, so nguyen, so sanh, !, &&, ||). None neu khac."""
    ra, i = [], 0
    bt = bt.strip()
    while i < len(bt):
        m = _RX_TOKEN.match(bt, i)
        if not m or m.end() == i:
            if bt[i:].strip() == "":
                break
            return None
        so, ten, op = m.groups()
        if so is not None:
            ra.append(so)
        elif ten is not None:
            if ten in ("true", "false"):
                ra.append("True" if ten == "true" else "False")
            elif ten in ("and", "or", "not"):
                ra.append(ten)
            else:
                ra.append("v_" + ten)
        else:
            ra.append({"&&": " and ", "||": " or ", "!": " not "}.get(op, op))
        i = m.end()
    return " ".join(ra) if ra else None


def _ten_trong(bt: str) -> set:
    return {t for t in re.findall(rf"(?<![\w.]){_TEN}(?![\w(])", bt)
            if t not in ("true", "false", "and", "or", "not")}


def la_bieu_thuc_huong(bt: str) -> bool:
    """Chi ten, so nguyen, so sanh, `!`, `&&`, `||`, ngoac - khong goi ham, mang, so thuc."""
    b = bt.strip()
    if not b or re.search(r"\w\s*\(|[\[\].\"'?:]|\d\.\d", b):
        return False
    return _sang_py(b) is not None


def _danh_gia(bt_py: str, bien: dict):
    return eval(bt_py, {"__builtins__": {}}, bien)  # noqa: S307 - chi token da loc


# ------------------------------------------------------------------- chuoi goi ----
def _chon_tam_nguyen(vb: str, m) -> tuple[str, bool] | None:
    """Lenh vao la mot nhanh cua `C ? X.Buy(..) : X.Sell(..)` -> (C, nhanh `?`)."""
    if not m.group("mql"):
        return None
    pos = m.start()
    s = max(vb.rfind(";", 0, pos), vb.rfind("{", 0, pos), vb.rfind("}", 0, pos)) + 1
    pre = vb[s:pos]
    muc, sau = 0, []
    for c in pre:
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        sau.append(muc)
    if muc != 0 or "?" not in pre:
        return None
    hoi = [i for i, c in enumerate(pre) if c == "?" and sau[i] == 0]
    hai = [i for i, c in enumerate(pre) if c == ":" and sau[i] == 0]
    if len(hoi) != 1 or len(hai) > 1:
        return None
    q = hoi[0]
    if hai and (hai[0] < q or pre[hai[0] + 1:].strip()):
        return None
    if not hai and pre[q + 1:].strip():
        return None
    D = _D()
    mo = vb.find("(", m.end("mql"))
    dong = D._dong_ngoac(vb, mo)
    if mo < 0 or dong < 0:
        return None
    tiep = vb[dong + 1:].lstrip()[:1]
    if (not hai and tiep != ":") or (hai and tiep not in (";", ")")):
        return None
    if hai:
        giua = pre[q + 1:hai[0]].strip()
        mg = re.fullmatch(r"(\w+)\.(Buy|Sell)[ \t]*(\(.*\))", giua, re.S)
        if not mg or mg.group(2) == m.group("mql"):
            return None
    dau = pre[:q]
    cuoi_gan = [x.end() for x in re.finditer(r"(?:^|[^=!<>])=(?!=)|\breturn\b", dau)]
    cond = D._boc_ngoac(dau[cuoi_gan[-1] if cuoi_gan else 0:].strip())
    if not cond:
        return None
    return cond, not hai


def _bien_cuc_bo(vb: str, mn: str, ham: dict, ten: str, den: int) -> tuple[str, int] | str | None:
    """`ten` gan DUNG MOT lan o muc than ham truoc `den`: (ve phai, vi tri). Chuoi = ly do."""
    than = mn[ham["mo"] + 1:ham["dong"]]
    gan = [x for x in re.finditer(rf"(?<![\w.]){re.escape(ten)}\s*(=(?!=)|\+\+|--|\+=|-=|\*=)",
                                  than)]
    if not gan:
        return None
    if len(gan) > 1 or gan[0].group(1) != "=":
        return f"bien {ten} gan {len(gan)} lan / doi gia tri"
    p = ham["mo"] + 1 + gan[0].start()
    if p > den:
        return f"bien {ten} gan sau cho dung"
    if GH._khoi_bao(mn, ham["mo"], p):
        return f"bien {ten} gan trong khoi long"
    het = mn.find(";", p)
    a = p + len(ten)
    a = mn.find("=", a) + 1
    return vb[a:het].strip(), p


def _giai_ten(vb: str, mn: str, ham: dict, ten: str, den: int, ten_tham: list,
              dinh: dict, buoc: int, sau: int = 0) -> str | None:
    """Giai `ten` o tang `buoc` vao `dinh` ("buoc:ten" -> (bieu thuc, tang cua ten trong do)).
    Tra None neu giai duoc (hoac hoan sang tang tren qua tham so), chuoi ly do neu khong."""
    kt = f"{buoc}:{ten}"
    if kt in dinh:
        return None
    if sau > 8:
        return "chuoi gan qua sau"
    r = _bien_cuc_bo(vb, mn, ham, ten, den)
    if isinstance(r, str):
        return r
    if r is not None:
        rhs, p = r
        mf = re.fullmatch(rf"({_TEN})\s*\((.*)\)", rhs, re.S)
        if mf and _D()._dong_ngoac(rhs, rhs.find("(")) == len(rhs) - 1:
            hh = ham_huong(vb, mf.group(1))
            if hh is None:
                return f"{ten} = {mf.group(1)}() khong phai ham huong"
            if isinstance(hh, str):
                return hh
            dinh[kt] = ("__F__", buoc, mf.group(1), p)
            return None
        rb = _D()._boc_ngoac(rhs)
        if not la_bieu_thuc_huong(rb):
            return f"{ten} = bieu thuc khong phai huong"
        dinh[kt] = (rb, buoc, None, p)
        for t2 in _ten_trong(rb):
            ly = _giai_ten(vb, mn, ham, t2, p, ten_tham, dinh, buoc, sau + 1)
            if ly:
                del dinh[kt]
                return ly
        return None
    if ten in ten_tham and ten_tham.count(ten) == 1:
        dinh[kt] = ("__THAM__", buoc + 1, ten_tham.index(ten), None)
        return None
    return f"{ten}: bien toan cuc / khong giai duoc"


_RX_TK = r"AccountInfoDouble\s*\(\s*ACCOUNT_(?:MARGIN_FREE|FREEMARGIN|BALANCE|EQUITY)\s*\)"


def _la_kiem_ky_quy(g: str, than: str) -> bool:
    """`marginNeeded > freeMargin`: hai ve la bien cuc bo ky quy - `x = AccountInfoDouble(
    ACCOUNT_MARGIN_FREE..)` hoac tham so ra cua `OrderCalcMargin(.., x)` (hoac chinh loi goi
    AccountInfoDouble). Kiem tai khoan (quan tri), khong phai tin hieu gia."""
    mm = re.fullmatch(rf"\s*({_TEN}|{_RX_TK})\s*(?:>|>=|<|<=)\s*({_TEN}|{_RX_TK})\s*", g)
    if not mm:
        return False
    loai = []
    for x in (mm.group(1), mm.group(2)):
        if re.fullmatch(_RX_TK, x):
            loai.append("tk")
        elif re.search(rf"(?<![\w.]){x}\s*=\s*{_RX_TK}\s*;", than):
            loai.append("tk")
        elif re.search(rf"OrderCalcMargin\s*\([^;]*,\s*{x}\s*\)", than):
            loai.append("can")
        else:
            return False
    return sorted(loai) == ["can", "tk"]


_RX_DAO = re.compile(
    rf"if\s*\(\s*({_TEN})\s*(?:!=\s*0|>\s*0)\s*\)\s*\{{\s*"
    rf"if\s*\(\s*({_TEN})\s*==\s*({_TEN})\s*\)\s*(?:return\s*;|\{{\s*return\s*;\s*\}})\s*"
    rf"(?:if\s*\(\s*!\s*{_TEN}\.PositionClose\s*\(\s*\1\s*\)\s*\)\s*"
    rf"(?:\{{[^{{}}]*?return\s*;\s*\}}|return\s*;)"
    rf"|{_TEN}\.PositionClose\s*\(\s*\1\s*\)\s*;)\s*\}}")


def _khoi_dao(vb: str, mn: str, bang: dict, ham: dict, den: int) -> tuple[int, int, str, str] | None:
    """DONG-VA-DAO (stop and reverse) o tang goi:
        ulong ticket = FindOwnPosition(side);
        if(ticket != 0){ if(side == signal) return; if(!t.PositionClose(ticket)) {..return;} }
    `FindOwnPosition` = ham tu do chi HOI vi the cua EA, gan `side` = +1 mua / -1 ban
    (`POSITION_TYPE_BUY ? 1 : -1`) va tra ticket (0 = khong co). Tra (a, b, bien_huong, side)."""
    than = mn[ham["mo"]:den]
    for x in _RX_DAO.finditer(than):
        tk, side, huong = x.group(1), x.group(2), x.group(3)
        mg = re.search(rf"(?<![\w.]){tk}\s*=\s*({_TEN})\s*\(\s*{side}\s*\)\s*;", than)
        if not mg or len(bang.get(mg.group(1), [])) != 1:
            continue
        h = bang[mg.group(1)][0]
        if not re.search(rf"&\s*{_TEN}\s*$", h["tham_so"].strip()):
            continue
        tf = mn[h["mo"]:h["dong"]]
        if not re.search(r"PositionGetInteger\s*\(\s*POSITION_TYPE\s*\)\s*==\s*POSITION_TYPE_BUY"
                         r"\s*\)?\s*\?\s*1\s*:\s*-\s*1", tf) or \
                re.search(r"\.(?:Buy|Sell|PositionOpen)\s*\(|OrderSend", tf):
            continue
        return ham["mo"] + x.start(), ham["mo"] + x.end(), huong, side
    return None


def nang_huong(vb: str, m, chieu: int) -> dict | str | None:
    """Lenh vao `m` (chieu +1/-1) chon theo gia tri ham tin hieu so nguyen.

    Tra None khi khong phai dang nay; chuoi ly do khi dung dang nhung khong chac; hoac
    {"ham": F, "s": s*, "guard", "vi", "thoat", "loai_tru", "goc", "qt", "tang", "ghi"}."""
    D = _D()
    if chieu == 0:
        return None
    mn = GH.mat_na(vb)
    bang = GH.ham_tu_do(mn)
    if not bang:
        return None
    rang = []                                     # (bieu thuc, phai_dung, tang)
    qt: list[str] = []
    dinh: dict = {}
    tn = _chon_tam_nguyen(vb, m)
    vi = m.start()
    tang: list[str] = []
    cho_goi: dict[int, int] = {}                  # tang -> vi tri loi goi tang duoi
    dao = None                                    # (tang, bien huong, bien side) khoi dong-va-dao
    for buoc in range(TANG_TOI_DA + 1):
        hc = GH._ham_chua(bang, vi)
        if hc is None:
            return None
        ten, ham = hc
        tang.append(ten)
        if len(bang[ten]) > 1:
            return None
        khoi = GH._khoi_bao(mn, ham["mo"], vi)
        if any(GH._loai_khoi(d) not in ("if", "khoi") for _, d in khoi):
            return None
        ifs, gap_else = D._cac_if_bao(vb, vi)
        if gap_else:
            return None
        ifs = [(p, g) for p, g in ifs if ham["mo"] < p < ham["dong"]
               and not D._LA_KIEM_LOI.search(g)
               and not (buoc > 0 and re.search(rf"\b{re.escape(tang[-2])}\s*\(", g))]
        thoat = D._thoat_som(vb, ham["mo"], vi)
        rl = D._return_long(vb, ham["mo"], vi)
        kd = _khoi_dao(vb, mn, bang, ham, vi) if rl else None
        if kd is not None:
            # khoi dong-va-dao: bo khoi khoi xet return long (mo phong bang `dao_khi_nguoc`)
            vb_d = vb[:kd[0]] + re.sub(r"[^\n]", " ", vb[kd[0]:kd[1]]) + vb[kd[1]:]
            rl = D._return_long(vb_d, ham["mo"], vi)
            dao = (buoc, kd[2], kd[3])
        tham = [p.strip() for p in ham["tham_so"].split(",") if p.strip()]
        ten_tham = []
        for p in tham:
            mp = re.search(rf"({_TEN})\s*(?:=.*)?$", p)
            ten_tham.append(mp.group(1) if mp and "&" not in p else "")
        dk_tang = [(g, True) for _, g in ifs] + [(t, False) for t in thoat]
        if buoc == 0 and tn is not None:
            dk_tang.append((tn[0], tn[1]))
        for g, dung in dk_tang:
            gb = D._boc_ngoac(g.strip())
            if la_bieu_thuc_huong(gb):
                thu = dict(dinh)
                ly = None
                for t in _ten_trong(gb):
                    ly = ly or _giai_ten(vb, mn, ham, t, vi, ten_tham, thu, buoc)
                if not ly:
                    dinh = thu
                    rang.append((gb, dung, buoc))
                    continue
                if ly.startswith("ham huong "):
                    return "huong int: " + ly          # dung dang, ham huong khong chac
            if _la_kiem_ky_quy(D._boc_ngoac(g.strip()), mn[ham["mo"]:ham["dong"]]):
                qt.append(g.strip()[:60] + " (ky quy)")
                continue
            q, con = GH._phan_quan_tri([g])
            if con:
                return None
            qt += q
        # tham so can doi so tu tang tren
        can = {k: v for k, v in dinh.items() if v[0] == "__THAM__" and v[1] == buoc + 1}
        if rl:
            return None if not rang else "huong int: return long co dieu kien: " + rl[0][:50]
        if ten == "OnTick":
            if can:
                return None
            break
        if ten in GH._SU_KIEN or buoc == TANG_TOI_DA:
            return None
        ds, ly = GH._cho_goi_don(mn, ten, ham)
        if ly or len(ds) != 1 or GH._hop_le_cho_goi(mn, ds[0], ten):
            return None
        vi = ds[0]
        cho_goi[buoc + 1] = vi
        if can:
            doi = D._tach_doi_so(vb, vb.find("(", vi))
            hc2 = GH._ham_chua(bang, vi)
            if not doi or hc2 is None:
                return None
            ham2 = hc2[1]
            tham2 = [p.strip() for p in ham2["tham_so"].split(",") if p.strip()]
            ten_tham2 = []
            for p in tham2:
                mp = re.search(rf"({_TEN})\s*(?:=.*)?$", p)
                ten_tham2.append(mp.group(1) if mp and "&" not in p else "")
            for kt, v in can.items():
                i = v[2]
                if i >= len(doi):
                    return None
                a = D._boc_ngoac(doi[i].strip())
                if not la_bieu_thuc_huong(a):
                    return None
                dinh[kt] = (a, buoc + 1, None, "tham")
                for t2 in _ten_trong(a):
                    ly = _giai_ten(vb, mn, ham2, t2, vi, ten_tham2, dinh, buoc + 1)
                    if ly:
                        return "huong int: " + ly
    fs = {(v[2], v[3], v[1]) for v in dinh.values() if v[0] == "__F__"}
    if not rang or not fs:
        return None
    if len(fs) > 1:
        return "huong int: hai loi goi ham huong tren mot chuoi"
    ten_f, goi_f, tang_f = next(iter(fs))
    if dao is not None:
        v = dinh.get(f"{dao[0]}:{dao[1]}")
        if v is None or v[0] != "__F__":
            return "huong int: khoi dong-va-dao so voi bien khong phai gia tri ham huong"

    # bien theo doi KHONG duoc doi gia tri sau khi gan: gan lai / ++ da chan o `_bien_cuc_bo`;
    # o day chan truyen vao ham cua tac gia co tham so tham chieu `&` (co the ghi de) va `&ten`
    ham_ref = [t for t, ds in bang.items() if len(ds) == 1 and "&" in ds[0]["tham_so"]]
    for kt, v in dinh.items():
        if v[0] == "__THAM__":
            continue
        b, t = int(kt.split(":", 1)[0]), kt.split(":", 1)[1]
        la_tham = v[3] == "tham"
        hc = GH._ham_chua(bang, cho_goi.get(b, m.start()) if la_tham else v[3])
        if hc is None:
            return None
        than = mn[hc[1]["mo"]:hc[1]["dong"]]
        if re.search(rf"&\s*{re.escape(t)}\b", than):
            return f"huong int: bien {t} lay dia chi (&)"
        for g in ham_ref:
            for x in re.finditer(rf"(?<![\w.]){re.escape(g)}\s*\(", than):
                k = D._dong_ngoac(than, than.find("(", x.start()))
                if k > 0 and re.search(rf"(?<![\w.]){re.escape(t)}\b", than[x.end():k]):
                    return f"huong int: bien {t} truyen vao {g}() co tham so tham chieu"

    def _gia(kt: str, s: int, sau: int = 0):
        if sau > 16:
            raise ValueError("vong")
        bt, tg, x2, _ = dinh[kt]
        if bt == "__F__":
            return s
        if bt == "__THAM__":
            raise KeyError(kt)
        bien = {"v_" + t2: _gia(f"{tg}:{t2}", s, sau + 1) for t2 in _ten_trong(bt)}
        return _danh_gia(_sang_py(bt), bien)

    def _chay(s: int) -> bool:
        for bt, dung, b in rang:
            bien = {"v_" + t: _gia(f"{b}:{t}", s) for t in _ten_trong(bt)}
            if bool(_danh_gia(_sang_py(bt), bien)) != dung:
                return False
        return True

    try:
        chay = {s: _chay(s) for s in (1, -1, 0)}
    except (KeyError, ValueError, TypeError, SyntaxError, NameError):
        return "huong int: khong danh gia duoc bieu thuc huong"
    hop = [s for s in (1, -1) if chay[s]]
    if chay[0]:
        return "huong int: lenh vao chay ca khi ham huong tra 0"
    if len(hop) != 1:
        return f"huong int: lenh vao chay voi {len(hop)} gia tri huong"
    s = hop[0]
    hh = ham_huong(vb, ten_f)
    if s not in hh:
        return f"huong int: {ten_f} khong bao gio tra {s:+d}"
    f = hh[s]
    return {"ham": ten_f, "s": s, "guard": f["guard"], "vi": f["vi"],
            "thoat": list(f["thoat"]), "loai_tru": list(f["loai_tru"]), "goc": f["goc"],
            "qt": qt + ([f"dong-va-dao: {dao[2]} == {dao[1]} -> bo; nguoc chieu -> dong roi vao"]
                        if dao else []),
            "tang": tang, "dang": f["dang"], "dao": dao is not None,
            # nhanh ba ngoi chon lenh (cho bo doc SL/TP `isBuy ? a : b`): (dieu kien, nhanh ?)
            "chon": tn,
            "ghi": f"lenh vao chieu {chieu:+d} khi {ten_f}() tra {s:+d} (thu {{+1,-1,0}}: "
                   + " ; ".join(('' if d else '!') + '(' + b + ')' for b, d, _ in rang)[:90] + ")"}
