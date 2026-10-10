# -*- coding: utf-8 -*-
"""DOC LOGIC DONG "RO LENH" (hedge / chot dinh / cat lo theo TIEN) cua EA MQL5.

Them 10/10/2026 (vong "ro hedge"). Breakout2/2-2/3 khong dong lenh bang SL/TP
hay theo so bar: `OnTick` goi `checkForClose()` MOI tick khi dang co vi the, va
ham do lam viec tren TONG LOI LO (tien) cua CA RO lenh:

    profits = GetProfits();                     // tong POSITION_PROFIT moi lenh
    if(profits<=0) peakwin=0; else peakwin=MathMax(peakwin,profits);
    if(peakwin>=45 && profits<(peakwin*0.9)) CloseAll();     // chot dinh
    if(profits<=-120) CloseAll();                             // cat lo ro
    if(postotal==1) { ... hedge nguoc chieu 0.4 lot khi gia cham hedgeprice }

Truoc vong nay mo phong dong cac EA do sau `giu` bar - mot he KHAC han.

Module nay doc dung CAC DANG tren (va chi chung). Gap cau lenh nao chua hieu
trong phan ma SONG cua ham dong -> tra None kem ly do, KHONG doan. Phan sau
`return;` vo dieu kien la ma chet (bo qua). Khoi hedge `if(postotal==n)` voi
n khong bao gio dat duoc (EA chi mo lenh dau khi KHONG co vi the, moi khoi
hedge them dung 1 lenh) duoc bao la `khong_toi_duoc`.

Ket qua (khoa DSL `ro`, doc o `ngu_phap.sinh_chan` / `mo_phong.chay_he`):
    {"lot_dau": 0.1, "hop_dong": 100000,
     "dinh": {"moc": 45, "ti_le": 0.9, "reset_am": bool, "reset_vao": bool} | None,
     "cat_lo": -120 | None,
     "hedge": [{"khi_so_lenh": 1, "kich": "diem", "khoang_diem": 300, "lot": 0.4,
                "reset_dinh": bool}
               | {"khi_so_lenh": 1, "kich": "loi", "nguong": -30, "lot": 0.3,
                  "reset_dinh": bool}],
     "dinh_tu": "input HedgeRange" ...}
Moi lenh hedge deu NGUOC chieu lenh dau (dang khac -> khong dich).
"""
from __future__ import annotations

import re

_SO = r"[-+]?\d+(?:\.\d+)?"
_KHAI_HAM = re.compile(r"^[ \t]*(?:static[ \t]+)?(?:void|bool|int|double|long|datetime)"
                       r"[ \t]+(\w+)[ \t]*\(([^)]*)\)\s*\{", re.M)


def _dong(s: str, i: int, mo: str = "(", dong: str = ")") -> int:
    muc = 0
    for k in range(i, len(s)):
        if s[k] == mo:
            muc += 1
        elif s[k] == dong:
            muc -= 1
            if muc == 0:
                return k
    return -1


def than_ham(vb: str, ten: str) -> tuple[int, int] | None:
    """(vi tri sau `{`, vi tri `}`) cua than ham `ten` (dinh nghia DAU TIEN)."""
    for m in _KHAI_HAM.finditer(vb):
        if m.group(1) == ten:
            a = m.end() - 1
            b = _dong(vb, a, "{", "}")
            if b > 0:
                return a + 1, b
    return None


def _gon(s: str) -> str:
    return re.sub(r"\s+", "", s)


def cau_lenh(s: str, goc: int = 0) -> list[dict]:
    """Tach `s` thanh cac cau lenh muc dinh: {loai, dk, than, khac, a, b, goc}.

    loai: "if" (dk, than, khac=than else hoac None) | "khoi" | "don".
    `a`, `b` la vi tri tuyet doi (cong `goc`)."""
    ra, i, n = [], 0, len(s)
    while i < n:
        while i < n and s[i] in " \t\r\n;":
            i += 1
        if i >= n:
            break
        m = re.match(r"if\s*\(", s[i:])
        if m:
            p = i + m.end() - 1
            q = _dong(s, p)
            if q < 0:
                raise ValueError("ngoac if khong dong")
            dk = s[p + 1:q]
            than, j = _mot_than(s, q + 1)
            khac = None
            m2 = re.match(r"\s*else\b", s[j:])
            if m2:
                khac, j = _mot_than(s, j + m2.end())
            ra.append({"loai": "if", "dk": dk, "than": than, "khac": khac,
                       "a": goc + i, "b": goc + j})
            i = j
            continue
        if s[i] == "{":
            q = _dong(s, i, "{", "}")
            ra.append({"loai": "khoi", "than": s[i + 1:q], "a": goc + i, "b": goc + q + 1})
            i = q + 1
            continue
        j = _het_cau(s, i)
        ra.append({"loai": "don", "than": s[i:j], "a": goc + i, "b": goc + j + 1})
        i = j + 1
    return ra


def _het_cau(s: str, i: int) -> int:
    muc = 0
    for k in range(i, len(s)):
        c = s[k]
        if c in "([{":
            muc += 1
        elif c in ")]}":
            muc -= 1
        elif c == ";" and muc == 0:
            return k
    return len(s)


def _mot_than(s: str, i: int) -> tuple[str, int]:
    while i < len(s) and s[i] in " \t\r\n":
        i += 1
    if i < len(s) and s[i] == "{":
        q = _dong(s, i, "{", "}")
        return s[i + 1:q], q + 1
    if re.match(r"if\s*\(", s[i:]):
        # `else if(...)` - lay ca cau if long
        cl = cau_lenh(s[i:])
        if cl:
            return s[i:i + (cl[0]["b"])], i + cl[0]["b"]
    j = _het_cau(s, i)
    return s[i:j] + ";", j + 1


# cau lenh KHONG doi trang thai giao dich: khai bao, doc gio, doc thong tin vi the
_BO_QUA = [
    r"(?:static)?(?:MqlRates|MqlDateTime|bool|datetime|double|int|long|ENUM_ORDER_TYPE|CTrade)"
    r"\w+(?:\[\])?(?:,\w+(?:\[\])?)*",
    r"datetime\w+=getCurrentTime\(\)",
    r"TimeToStruct\(\w+,\w+\)",
    r"(?:double|long|int)\w+=PositionGet(?:Double|Integer)\(POSITION_\w+\)",
]


def _la_kiem_loi_copy(c: dict) -> bool:
    return c["loai"] == "if" and re.fullmatch(
        r"Copy\w+\(.*\)==-1", _gon(c["dk"])) is not None and \
        _gon(c["than"]).rstrip(";") == "return" and c["khac"] is None


def _cat_ma_song(than: str, goc: int) -> tuple[list[dict], bool]:
    """Cau lenh muc dinh TRUOC `return;` vo dieu kien dau tien (phan sau la ma chet)."""
    ds = cau_lenh(than, goc)
    for k, c in enumerate(ds):
        if c["loai"] == "don" and _gon(c["than"]) == "return":
            return ds[:k], True
    return ds, False


def _ham_dong_mo(vb: str) -> tuple[str, str] | None:
    tk = than_ham(vb, "OnTick")
    if not tk:
        return None
    g = _gon(vb[tk[0]:tk[1]])
    m = re.search(r"if\(PositionSelect\(_Symbol\)\)\{?(\w+)\(\);\}?else\{?(\w+)\(\);\}?", g)
    if not m:
        return None
    return m.group(1), m.group(2)


def _ham_tong_loi(vb: str, ten: str) -> bool:
    t = than_ham(vb, ten)
    if not t:
        return False
    g = _gon(vb[t[0]:t[1]])
    return ("PositionsTotal()" in g and "+=PositionGetDouble(POSITION_PROFIT)" in g
            and "MAGIC" not in g and "PositionClose" not in g and "PositionOpen" not in g)


def _ham_dong_het(vb: str, ten: str) -> bool:
    t = than_ham(vb, ten)
    if not t:
        return False
    g = _gon(vb[t[0]:t[1]])
    return ("PositionsTotal()" in g and re.search(r"PositionClose\(PositionGetSymbol\(\w+\)\)", g)
            is not None and "MAGIC" not in g and "PositionOpen" not in g)


def _gia_tri(x: str, hang: dict) -> float | None:
    if re.fullmatch(_SO, x):
        return float(x)
    v = hang.get(x)
    return float(v) if v is not None else None


def doc_ro(vb: str, hang: dict, khai: dict | None = None) -> dict:
    """Doc logic ro lenh. `vb` = van ban DA chuan hoa (`_chuan_hoa` + `_chuan_hoa_mql5`:
    `&&` -> ` and `, gia song `current[0].close` -> `_gia0_`). `hang` = bang hang so.

    Tra {"ro": dict|None, "ly_do": str|None, "ham_dong", "ham_mo",
         "khoi": [{"a", "b", "khi_so_lenh", "dich": bool, "toi_duoc": bool}],
         "ghi": [mo ta]}.
    """
    ra = {"ro": None, "ly_do": None, "ham_dong": None, "ham_mo": None, "khoi": [], "ghi": []}
    hm = _ham_dong_mo(vb)
    if not hm:
        ra["ly_do"] = "OnTick khong co dang `if(PositionSelect(_Symbol)) dong(); else mo();`"
        return ra
    ten_dong, ten_mo = hm
    ra["ham_dong"], ra["ham_mo"] = ten_dong, ten_mo
    td, tm = than_ham(vb, ten_dong), than_ham(vb, ten_mo)
    if not td or not tm:
        ra["ly_do"] = "khong thay than ham dong/mo"
        return ra
    try:
        ds, _ = _cat_ma_song(vb[td[0]:td[1]], td[0])
    except ValueError as e:
        ra["ly_do"] = str(e)
        return ra
    bien_loi = bien_so = bien_dinh = None
    dinh = {}
    cat_lo = None
    khoi_hedge: list[tuple[dict, int, str | None]] = []   # (cau, n, nguong loi | None)
    for c in ds:
        g = _gon(c["than"]).rstrip(";")
        if c["loai"] == "don":
            m = re.fullmatch(r"(?:double)?(\w+)=(\w+)\(\)", g)
            if m and m.group(2) != "PositionsTotal" and _ham_tong_loi(vb, m.group(2)):
                bien_loi = m.group(1)
                continue
            m = re.fullmatch(r"(?:int)?(\w+)=PositionsTotal\(\)", g)
            if m:
                bien_so = m.group(1)
                continue
            m = re.fullmatch(r"(\w+)=MathMax\(\1,(\w+)\)", g)
            if m and bien_loi and m.group(2) == bien_loi:
                bien_dinh = m.group(1)
                dinh["reset_am"] = False
                continue
            if any(re.fullmatch(p, g) for p in _BO_QUA):
                continue
            ra["ly_do"] = f"cau lenh chua hieu trong {ten_dong}: `{g[:60]}`"
            return ra
        if c["loai"] != "if":
            ra["ly_do"] = f"khoi lenh chua hieu trong {ten_dong}"
            return ra
        if _la_kiem_loi_copy(c):
            continue
        dk = _gon(c["dk"])
        than = _gon(c["than"]).rstrip(";")
        khac = _gon(c["khac"]).rstrip(";") if c["khac"] is not None else None
        # peak: if(P<=0) K=0; else K=MathMax(K,P);
        m = re.fullmatch(r"(\w+)<=0", dk)
        if m and bien_loi == m.group(1) and khac is not None:
            m1 = re.fullmatch(r"(\w+)=0", than)
            m2 = re.fullmatch(r"(\w+)=MathMax\(\1,(\w+)\)", khac)
            if m1 and m2 and m1.group(1) == m2.group(1) and m2.group(2) == bien_loi:
                bien_dinh = m1.group(1)
                dinh["reset_am"] = True
                continue
        if khac is not None:
            ra["ly_do"] = f"if/else chua hieu: `{dk[:50]}`"
            return ra
        # chot dinh: if(K>=A and P<(K*B)) CloseAll();
        m = re.fullmatch(rf"\(?(\w+)>=({_SO}|\w+)\)?and\(?(\w+)<\(?\1\*({_SO}|\w+)\)?\)?", dk)
        if m and bien_dinh == m.group(1) and m.group(3) == bien_loi:
            hm_ = re.fullmatch(r"(\w+)\(\)", than)
            a, b = _gia_tri(m.group(2), hang), _gia_tri(m.group(4), hang)
            if hm_ and _ham_dong_het(vb, hm_.group(1)) and a is not None and b is not None:
                dinh.update(moc=a, ti_le=b)
                continue
        # cat lo: if(P<=C) CloseAll();
        m = re.fullmatch(rf"(\w+)<=({_SO}|\w+)", dk)
        if m and m.group(1) == bien_loi:
            hm_ = re.fullmatch(r"(\w+)\(\)", than)
            v = _gia_tri(m.group(2), hang)
            if hm_ and _ham_dong_het(vb, hm_.group(1)) and v is not None and v < 0:
                cat_lo = v
                continue
        # khoi hedge: if(postotal==n) {...} | if(P<=V and postotal==n) {...}
        if bien_so:
            m = re.fullmatch(rf"{bien_so}==(\d+)", dk)
            if m:
                khoi_hedge.append((c, int(m.group(1)), None))
                continue
            m = re.fullmatch(rf"\(?{bien_loi}<=({_SO})\)?and\(?{bien_so}==(\d+)\)?", dk) \
                if bien_loi else None
            if m:
                khoi_hedge.append((c, int(m.group(2)), m.group(1)))
                continue
        ra["ly_do"] = f"dieu kien chua hieu trong {ten_dong}: `{dk[:60]}`"
        return ra
    if not bien_loi:
        ra["ly_do"] = "ham dong khong dung tong loi lo ca ro"
        return ra
    if dinh and ("moc" not in dinh or "reset_am" not in dinh):
        ra["ly_do"] = "chot dinh doc khong du (thieu cap nhat dinh hoac nguong)"
        return ra
    # --- lenh dau (ham mo) ---
    gm = _gon(vb[tm[0]:tm[1]])
    if len(re.findall(r"PositionOpen\(", gm)) != 1:
        ra["ly_do"] = "ham mo co != 1 lenh PositionOpen"
        return ra
    po = gm.find("PositionOpen(")
    vol = re.findall(rf"(?:^|[;{{}}])volume=({_SO});", gm[:po])
    if not vol:
        ra["ly_do"] = "khoi luong lenh dau khong phai hang so"
        return ra
    lot0 = float(vol[-1])
    reset_vao = bool(bien_dinh and re.search(rf"(?<![\w.]){bien_dinh}=0;", gm[po:]))
    if dinh:
        dinh["reset_vao"] = reset_vao
    # --- khoi hedge ---
    toi = {1}
    hedge = []
    # thu tu MA (khong sap xep): EA kiem theo thu tu dong code
    con = list(khoi_hedge)
    doi = True
    toi_duoc = set()
    while doi:
        doi = False
        for c, n, _ in con:
            if n in toi and id(c) not in toi_duoc:
                toi_duoc.add(id(c))
                toi.add(n + 1)
                doi = True
    for c, n, nguong in khoi_hedge:
        kh = {"a": c["a"], "b": c["b"], "khi_so_lenh": n, "dich": False,
              "toi_duoc": id(c) in toi_duoc}
        ra["khoi"].append(kh)
        if not kh["toi_duoc"]:
            ra["ghi"].append(f"khoi hedge `{bien_so}=={n}` KHONG toi duoc: lenh dau mo khi "
                             f"khong co vi the, moi khoi hedge them 1 lenh -> so lenh chi "
                             f"{sorted(toi - {max(toi)}) + [max(toi)]} (gia dinh tai khoan "
                             f"chi co EA nay)")
            continue
        h, ly = _doc_khoi_hedge(c["than"], gm, bien_dinh, nguong, hang, khai or {})
        if h is None:
            ra["ly_do"] = f"khoi hedge `{bien_so}=={n}`: {ly}"
            return ra
        h["khi_so_lenh"] = n
        kh["dich"] = True
        hedge.append(h)
    ro = {"lot_dau": lot0, "hop_dong": 100000.0,
          "dinh": dinh or None, "cat_lo": cat_lo, "hedge": hedge}
    ra["ro"] = ro
    mo_ta = [f"dong theo TONG loi lo ca ro (tien, `{bien_loi}`), lenh dau {lot0:g} lot"]
    if dinh:
        mo_ta.append(f"chot dinh: dinh>={dinh['moc']:g} va loi<dinh*{dinh['ti_le']:g} -> dong het"
                     + (" (dinh ve 0 khi loi<=0)" if dinh["reset_am"] else "")
                     + (" (dinh ve 0 khi vao lenh)" if reset_vao else ""))
    if cat_lo is not None:
        mo_ta.append(f"cat lo ro: loi<={cat_lo:g} -> dong het")
    for h in hedge:
        mo_ta.append(f"hedge NGUOC chieu {h['lot']:g} lot khi so lenh=={h['khi_so_lenh']} va "
                     + (f"gia cham gia_vao -+ {h['khoang_diem']:g} point" if h["kich"] == "diem"
                        else f"loi<={h['nguong']:g}")
                     + (" (dinh ve 0)" if h["reset_dinh"] else ""))
    ra["ghi"] = mo_ta + ra["ghi"]
    return ra


def _doc_khoi_hedge(than: str, gm: str, bien_dinh: str | None, nguong: str | None,
                    hang: dict, khai: dict) -> tuple[dict | None, str]:
    g = _gon(than)
    if len(re.findall(r"PositionOpen\(", g)) != 1:
        return None, "khong dung 1 lenh PositionOpen"
    if not re.search(r"\.PositionOpen\(_Symbol,type,volume,price,(?:NULL|0),(?:NULL|0)\)", g):
        return None, "PositionOpen khong o dang (type, volume, price, khong SL/TP)"
    # `double price=0, volume=0;` la khai bao; phep gan THAT la cau rieng `volume=X;`
    vol = re.findall(rf"(?:^|[;{{}}])volume=({_SO});", g)
    if len(vol) != 1:
        return None, "khoi luong hedge khong phai mot hang so"
    reset = bool(bien_dinh and re.search(rf"(?<![\w.]){bien_dinh}=0;", g))
    con = g
    con = re.sub(rf"(?<![\w.]){bien_dinh}=0;", "", con) if bien_dinh else con
    if nguong is not None:
        # dang loi: posType BUY -> SELL, SELL -> BUY
        m = re.search(r"long(\w+)=PositionGetInteger\(POSITION_TYPE\);", con)
        if not m:
            return None, "khong doc duoc chieu lenh dang mo"
        pt = m.group(1)
        if not (re.search(rf"if\({pt}==POSITION_TYPE_BUY\)\{{type=ORDER_TYPE_SELL;price="
                          r"SymbolInfoDouble\(_Symbol,SYMBOL_BID\);\}", con) and
                re.search(rf"if\({pt}==POSITION_TYPE_SELL\)\{{type=ORDER_TYPE_BUY;price="
                          r"SymbolInfoDouble\(_Symbol,SYMBOL_ASK\);\}", con)):
            return None, "hedge theo loi khong phai dang nguoc chieu lenh dang mo"
        return {"kich": "loi", "nguong": float(nguong), "lot": float(vol[0]),
                "reset_dinh": reset}, ""
    # dang Tradesinfo: X = Tradesinfo.initup and _gia0_ <= Tradesinfo.hedgeprice ...
    gg = con
    m1 = re.search(r"(\w+)=Tradesinfo\.initupand_gia0_<=Tradesinfo\.hedgeprice;", gg)
    m2 = re.search(r"(\w+)=!Tradesinfo\.initupand_gia0_>=Tradesinfo\.hedgeprice;", gg)
    if not (m1 and m2):
        return None, "dieu kien hedge khong o dang `initup && gia<=hedgeprice` / nguoc lai"
    x_mua0, x_ban0 = m1.group(1), m2.group(1)     # bien bat khi lenh dau MUA / BAN
    if not re.search(rf"if\({x_mua0}or{x_ban0}\)|if\({x_ban0}or{x_mua0}\)", gg):
        return None, "khong thay `if(hedgeup||hedgedown)`"
    if not (re.search(rf"if\({x_mua0}\)\{{type=ORDER_TYPE_SELL;price=SymbolInfoDouble\(_Symbol,"
                      r"SYMBOL_BID\);\}", gg) and
            re.search(rf"if\({x_ban0}\)\{{type=ORDER_TYPE_BUY;price=SymbolInfoDouble\(_Symbol,"
                      r"SYMBOL_ASK\);\}", gg)):
        return None, "hedge Tradesinfo khong nguoc chieu lenh dau"
    # hedgeprice dat o ham mo: mua: price-(R*_Point), ban: price+(R*_Point)
    mm = re.search(r"Tradesinfo\.initup=true;(?:(?!Tradesinfo\.initup=).)*?Tradesinfo\."
                   r"hedgeprice=price-\((\w+)\*_Point\);", gm)
    mb = re.search(r"Tradesinfo\.initup=false;(?:(?!Tradesinfo\.initup=).)*?Tradesinfo\."
                   r"hedgeprice=price\+\((\w+)\*_Point\);", gm)
    if not (mm and mb) or mm.group(1) != mb.group(1):
        return None, "hedgeprice o ham mo khong o dang gia_vao -+ (R*_Point)"
    if not (re.search(r"Tradesinfo\.initup=true;(?:(?!Tradesinfo\.initup=).)*?price="
                      r"SymbolInfoDouble\(_Symbol,SYMBOL_ASK\);", gm) or
            re.search(r"price=SymbolInfoDouble\(_Symbol,SYMBOL_ASK\);(?:(?!price=).)*?"
                      r"Tradesinfo\.initup=true;", gm)):
        return None, "gia vao lenh mua khong phai ASK"
    if not re.search(r"Tradesinfo\.initprice=price;", gm):
        return None, "khong thay initprice=price"
    R = _gia_tri(mm.group(1), hang)
    if R is None or R <= 0:
        return None, f"khoang hedge `{mm.group(1)}` khong ro"
    # bien khoang co gan lai o noi khac khong (ngoai khai bao) -> khong chac
    return {"kich": "diem", "khoang_diem": float(R), "lot": float(vol[0]),
            "reset_dinh": reset}, ""


# ---------------------------------------------------------------------------
# SL/TP THEO KHOANG CACH ATR (EA Template) - them 10/10/2026
#
#   OpenTrade(sig>0 ? BUY : SELL, atr*InpSlAtrMult, atr*InpTpAtrMult);
#   bool OpenTrade(type, slDist, tpDist) {
#      isBuy = (type==ORDER_TYPE_BUY); dir = isBuy ? 1 : -1;
#      price = SymbolInfoDouble(_Symbol, isBuy ? SYMBOL_ASK : SYMBOL_BID);
#      slDist = MathMax(slDist, MinStopDistance());   // stops/freeze level, 0 -> 3*spread
#      sl = NormalizePrice(price - dir*slDist); tp = NormalizePrice(price + dir*tpDist);
#      lot = LotsForRisk(slDist);                    // equity*InpRiskPct/100 / (slDist*gia tri)
#      g_trade.Buy(lot, _Symbol, 0, sl, tp);
#   atr = GetATR() = CopyBuffer(iATR(_Symbol,PERIOD_CURRENT,InpAtrPeriod), 0, 1, 1, v) -> v[0]
# -> sltp {"sl_kc": InpSlAtrMult*ATR, "tp_kc": InpTpAtrMult*ATR, "sl_kc_min_spread": 3,
#          "rui_ro": InpRiskPct/100}. MT5 iATR = TRUNG BINH CONG cua TR (khong phai Wilder).
# Chi doc khi MOI mau khop; khong thi tra None + ly do.
# ---------------------------------------------------------------------------
def _tham_so_ham(vb: str, ten: str) -> list[str] | None:
    m = re.search(rf"^[ \t]*\w+[ \t]+{re.escape(ten)}[ \t]*\(([^)]*)\)\s*\{{", vb, re.M)
    if not m:
        return None
    ra = []
    for p in m.group(1).split(","):
        w = re.findall(r"\w+", p.split("=")[0])
        if w:
            ra.append(w[-1])
    return ra


def _tach_doi(s: str) -> list[str]:
    ra, muc, dau = [], 0, 0
    for i, c in enumerate(s):
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        elif c == "," and muc == 0:
            ra.append(s[dau:i])
            dau = i + 1
    ra.append(s[dau:])
    return ra


#: dau cau lenh + kieu khai bao tuy chon: `boolisBuy=` (van ban da bo khoang trang)
_DAU = r"(?:^|(?<=[;{}]))(?:const)?(?:bool|int|double|long|ulong|datetime)?"


def doc_sltp_kc(vb: str, ten_f: str, hang: dict) -> tuple[dict | None, list[str], float | None]:
    """`vb` = van ban CHUA chuan hoa MQL5 (da bo chu thich). (khoi sltp, ghi_chu, spread_max)."""
    ts = _tham_so_ham(vb, ten_f)
    t = than_ham(vb, ten_f)
    if not ts or not t or len(ts) != 3:
        return None, [], None
    p_type, p_sl, p_tp = ts
    g = _gon(vb[t[0]:t[1]])
    m = re.search(rf"{_DAU}(\w+)=\({p_type}==ORDER_TYPE_BUY\);", g)
    if not m:
        return None, ["SL/TP khoang cach: khong thay isBuy"], None
    isb = m.group(1)
    m = re.search(rf"{_DAU}(\w+)={isb}\?1:-1;", g)
    mp = re.search(rf"{_DAU}(\w+)=SymbolInfoDouble\(_Symbol,{isb}\?SYMBOL_ASK:SYMBOL_BID\);", g)
    if not m or not mp:
        return None, ["SL/TP khoang cach: khong thay dir / gia ASK-BID"], None
    dr, gia = m.group(1), mp.group(1)
    gan_sl = re.findall(rf"(?:^|[;{{}}]){p_sl}=([^;]+);", g)
    min_x = None
    if gan_sl:
        if len(gan_sl) != 1:
            return None, ["SL/TP khoang cach: slDist bi gan nhieu lan"], None
        mm = re.fullmatch(rf"MathMax\({p_sl},(\w+)\(\)\)", gan_sl[0])
        if not mm:
            return None, ["SL/TP khoang cach: phep gan slDist chua hieu"], None
        tm = than_ham(vb, mm.group(1))
        gm = _gon(vb[tm[0]:tm[1]]) if tm else ""
        mx = re.search(r"if\(\w+==0\)\w+=SymbolInfoInteger\(_Symbol,SYMBOL_SPREAD\)\*(\d+(?:\.\d+)?);"
                       r"return\w+\*_Point;", gm)
        if not mx or "SYMBOL_TRADE_STOPS_LEVEL" not in gm:
            return None, ["SL/TP khoang cach: khoang toi thieu chua hieu"], None
        min_x = float(mx.group(1))
    ms = re.search(rf"{_DAU}(\w+)=(?:NormalizePrice\()?{gia}-{dr}\*{p_sl}\)?;", g)
    mt = re.search(rf"{_DAU}(\w+)=(?:NormalizePrice\()?{gia}\+{dr}\*{p_tp}\)?;", g)
    if not ms or not mt:
        return None, ["SL/TP khoang cach: sl/tp khong dang gia -+ dir*kc"], None
    sl, tp = ms.group(1), mt.group(1)
    mo = re.findall(rf"\.(?:Buy|Sell)\((\w+),_Symbol,0,{sl},{tp}\)", g)
    if not mo:
        return None, ["SL/TP khoang cach: lenh Buy/Sell khong dung sl/tp nay"], None
    lot = mo[0]
    rui_ro, ghi = None, []
    mr = re.search(rf"{_DAU}{lot}=(\w+)\({p_sl}\);", g)
    if mr:
        tr = than_ham(vb, mr.group(1))
        gr = _gon(vb[tr[0]:tr[1]]) if tr else ""
        mk = re.search(r"AccountInfoDouble\(ACCOUNT_EQUITY\)\*(\w+(?:\.\d+)?)/100(?:\.0)?;", gr)
        if mk and re.search(r"/\w+\)\*\w+;", gr) and "riskMoney/" in gr.replace("(", ""):
            v = _gia_tri(mk.group(1), hang)
            if v is not None and v > 0:
                rui_ro = v / 100.0
    if rui_ro is None:
        ghi.append("khoi luong lenh khong doc duoc theo rui ro -> trong so 1 (gia dinh)")
    # loi goi: F(sig>0 ? BUY : SELL, atr*A, atr*B)
    atr = n_atr = he_sl = he_tp = None
    for mc in re.finditer(rf"\b{re.escape(ten_f)}\s*\(", vb):
        if vb[:mc.start()].rstrip().endswith(("bool", "void", "int", "double")):
            continue
        k = _dong(vb, mc.end() - 1)
        ds = [_gon(x) for x in _tach_doi(vb[mc.end():k])]
        if len(ds) != 3:
            continue
        a1 = re.fullmatch(r"(\w+)\*(\w+(?:\.\d+)?)", ds[1])
        a2 = re.fullmatch(r"(\w+)\*(\w+(?:\.\d+)?)", ds[2])
        if not a1 or not a2 or a1.group(1) != a2.group(1):
            continue
        av = a1.group(1)
        # trong ham goi: av = GetATR();
        goi = None
        for mh in re.finditer(r"^[ \t]*\w+[ \t]+(\w+)[ \t]*\([^)]*\)\s*\{", vb, re.M):
            if mh.start() < mc.start():
                goi = mh
        if not goi:
            continue
        mg = re.search(rf"{_DAU}{av}=(\w+)\(\);", _gon(vb[goi.end():mc.start()]))
        if not mg:
            continue
        ta = than_ham(vb, mg.group(1))
        ga = _gon(vb[ta[0]:ta[1]]) if ta else ""
        mb = re.search(r"CopyBuffer\(([\w.]+),0,1,1,(\w+)\)", ga)
        if not mb or not re.search(rf"return{mb.group(2)}\[0\];", ga):
            continue
        mi = re.search(rf"{re.escape(mb.group(1))}=iATR\(_Symbol,(?:PERIOD_CURRENT|_Period|0),"
                       r"(\w+)\);", _gon(vb))
        if not mi:
            continue
        n_atr = _gia_tri(mi.group(1), hang)
        he_sl, he_tp = _gia_tri(a1.group(2), hang), _gia_tri(a2.group(2), hang)
        atr = av
        break
    if atr is None or n_atr is None or not he_sl or not he_tp or he_sl <= 0 or he_tp <= 0:
        return None, ["SL/TP khoang cach: khong truy duoc ATR*he so o loi goi"], None
    t_atr = {"chi_bao": "atr", "n": int(n_atr), "kieu": "sma"}
    khoi = {"sl": None, "tp": None, "keo": None,
            "sl_kc": {"chi_bao": "tuyen_tinh", "toan_hang": [t_atr], "he_so": [he_sl]},
            "tp_kc": {"chi_bao": "tuyen_tinh", "toan_hang": [dict(t_atr)], "he_so": [he_tp]},
            "sl_kc_min_spread": min_x, "rui_ro": rui_ro}
    ghi.insert(0, f"SL = gia_vao -+ max({he_sl:g}*ATR({int(n_atr)}) bar vua dong"
               + (f", {min_x:g}*spread" if min_x else "") + f"); TP = gia_vao +- {he_tp:g}*ATR"
               + (f"; khoi luong theo rui ro {rui_ro*100:g}% von/SL" if rui_ro else ""))
    if min_x:
        ghi.append("khoang SL toi thieu: gia dinh SYMBOL_TRADE_STOPS_LEVEL = FREEZE_LEVEL = 0 "
                   f"(-> {min_x:g} x spread)")
    ghi.append("ATR cua MT5 = trung binh cong TR (iATR), khong phai Wilder")
    # bo loc spread o OnTick: if(!SpreadOK()) return; SpreadOK: spread <= X
    sm = None
    tk = than_ham(vb, "OnTick")
    if tk:
        for mf in re.finditer(r"if\(!(\w+)\(\)\)return;", _gon(vb[tk[0]:tk[1]])):
            tf = than_ham(vb, mf.group(1))
            if tf:
                mx = re.fullmatch(r"returnSymbolInfoInteger\(_Symbol,SYMBOL_SPREAD\)<=(\w+);",
                                  _gon(vb[tf[0]:tf[1]]))
                if mx:
                    sm = _gia_tri(mx.group(1), hang)
    if sm is not None:
        ghi.append(f"bo lenh khi spread > {sm:g} point (spread do theo gio cua mo hinh chi phi)")
    return khoi, ghi, sm
