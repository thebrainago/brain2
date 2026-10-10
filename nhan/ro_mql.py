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
            het_than = j                      # cuoi nhanh then (truoc `else`)
            khac = None
            m2 = re.match(r"\s*else\b", s[j:])
            if m2:
                khac, j = _mot_than(s, j + m2.end())
            ra.append({"loai": "if", "dk": dk, "than": than, "khac": khac,
                       "a": goc + i, "b": goc + j, "het_than": goc + het_than})
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
        # `if(IsTRadeOpen()) dong(); else mo();` voi ham co-vi-the loc theo magic
        m = re.search(r"if\((\w+)\(\)\)\{?(\w+)\(\);\}?else\{?(\w+)\(\);\}?", g)
        if not m or not _co_ham_dem(vb, m.group(1), "co"):
            return None
        return m.group(2), m.group(3)
    return m.group(1), m.group(2)


def _ham_tong_loi(vb: str, ten: str) -> bool:
    t = than_ham(vb, ten)
    if not t:
        return False
    g = _bo_loc_magic(_gon(vb[t[0]:t[1]]))
    return ("PositionsTotal()" in g and "+=PositionGetDouble(POSITION_PROFIT)" in g
            and "-=" not in g
            and "MAGIC" not in g and "PositionClose" not in g and "PositionOpen" not in g)


def _ham_dong_het(vb: str, ten: str) -> bool:
    t = than_ham(vb, ten)
    if not t:
        return False
    g = _bo_loc_magic(_gon(vb[t[0]:t[1]]))
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
    hang = dict(hang)
    than_d = _gon(vb[td[0]:td[1]])
    cong = None                       # (curTime, prevTime) khi da qua cong bar
    khoi_luoi: list[dict] = []
    magic = False
    for c in ds:
        g = _gon(c["than"]).rstrip(";")
        if cong is not None:
            # SAU cong bar: chi chap nhan khoi luoi + `prevTime=curTime` cuoi cung
            if c["loai"] == "don" and g == f"{cong[1]}={cong[0]}" and c is ds[-1]:
                continue
            if c["loai"] == "don" and any(re.fullmatch(p, g) for p in _BO_QUA):
                continue
            if c["loai"] == "if" and "PositionOpen(" in c["than"] and not khoi_luoi:
                khoi_luoi.append(c)
                continue
            ra["ly_do"] = f"cau lenh sau cong bar chua hieu trong {ten_dong}: `{g[:60]}`"
            return ra
        if c["loai"] == "if" and _gon(c["than"]).rstrip(";") == "return" and c["khac"] is None:
            # cong bar: if(curTime==prevTime) return;  (prevTime static, gan cuoi ham)
            mg = re.fullmatch(r"(\w+)==(\w+)", _gon(c["dk"]))
            if mg and re.search(rf"(?:^|;)datetime{mg.group(1)}=getCurrentTime\(\);", than_d) and \
                    re.search(rf"(?:^|;)staticdatetime{mg.group(2)};", than_d) and \
                    len(re.findall(rf"(?<![\w.]){mg.group(2)}=(?!=)", than_d)) == 1 and \
                    _gon(ds[-1]["than"]).rstrip(";") == f"{mg.group(2)}={mg.group(1)}":
                cong = (mg.group(1), mg.group(2))
                continue
        if c["loai"] == "don":
            m = re.fullmatch(r"(?:int)?(\w+)=(\w+)\(\)", g)
            if m and _co_ham_dem(vb, m.group(2), "dem"):
                bien_so = m.group(1)              # PosTotal() loc magic
                magic = True
                continue
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
            # hang cuc bo chi tu input: `double expectation=takeprofit*GetStartVolume();`
            m = re.fullmatch(r"(?:double|int)(\w+)=(.+)", c["than"].strip().rstrip(";").strip()
                             .replace(" ", "").replace("\t", ""))
            if m and len(re.findall(rf"(?<![\w.]){m.group(1)}\s*(?:=(?!=)|\+=|-=|\+\+|--)",
                                    vb[td[0]:td[1]])) == 1:
                v = gia_tri_thuan(c["than"].split("=", 1)[1].strip().rstrip(";"), vb, khai)
                if v is not None:
                    hang[m.group(1)] = v
                    ra["ghi"].append(f"{m.group(1)} = {v:g} (tinh tu input)")
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
        m = re.fullmatch(rf"\(?(\w+)>=({_SO}|\w+)\)?and\(?(\w+)(<=?)\(?\1\*({_SO}|\w+)\)?\)?", dk)
        if m and bien_dinh == m.group(1) and m.group(3) == bien_loi:
            hm_ = re.fullmatch(r"(\w+)\(\)", than)
            a, b = _gia_tri(m.group(2), hang), _gia_tri(m.group(5), hang)
            if hm_ and _ham_dong_het(vb, hm_.group(1)) and a is not None and b is not None:
                dinh.update(moc=a, ti_le=b)
                if m.group(4) == "<=":
                    dinh["phep"] = "<="
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
    vol = re.findall(r"(?:^|[;{}])volume=([^;=][^;]*);", gm[:po])
    lot0 = gia_tri_thuan(vol[-1], vb, khai) if vol else None
    if lot0 is None and vol and re.fullmatch(_SO, vol[-1]):
        lot0 = float(vol[-1])
    if lot0 is None or lot0 <= 0:
        ra["ly_do"] = "khoi luong lenh dau khong phai hang so"
        return ra
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
    # --- luoi martingale (sau cong bar) ---
    luoi = None
    if khoi_luoi:
        c = khoi_luoi[0]
        try:
            luoi, ly, else_chet = doc_luoi(c, vb, vb[tm[0]:tm[1]], khai, bien_so, bien_dinh)
        except (_Kh, ValueError, RecursionError) as e:
            luoi, ly, else_chet = None, f"loi doc luoi: {e}", False
        if luoi is None:
            ra["ly_do"] = f"khoi luoi: {ly}"
            return ra
        if abs(luoi["lot_dau"] - lot0) > 1e-12:
            ra["ly_do"] = "khoi luoi: lot dau khong khop"
            return ra
        if bien_dinh and luoi["reset_dinh"] is False:
            ra["ly_do"] = "khoi luoi: dinh khong ve 0 khi them lenh (chua ho tro)"
            return ra
        ra["khoi"].append({"a": c["a"], "b": c["het_than"], "khi_so_lenh": 0, "dich": True,
                           "toi_duoc": True, "luoi": True})
        if c["khac"] is not None:
            ra["khoi"].append({"a": c["het_than"], "b": c["b"], "khi_so_lenh": 0, "dich": False,
                               "toi_duoc": not else_chet, "luoi": True,
                               "ly_do": "nhanh else cua khoi luoi khong toi duoc voi input "
                                        "mac dinh (dieu kien khoi luoi luon dung)"})
            if not else_chet:
                ra["ly_do"] = "khoi luoi: nhanh else co the chay (chua dich)"
                return ra
            ra["ghi"].append("nhanh `else` cua khoi luoi (vd hedge vung `zonesequence`) KHONG "
                             "toi duoc voi input mac dinh -> ma chet")
        del luoi["lot_dau"]
        if hedge:
            ra["ly_do"] = "luoi + hedge trong cung ham dong: chua ho tro"
            return ra
    if cong is not None and luoi is None:
        ra["ly_do"] = "co cong bar trong ham dong nhung khong co khoi luoi"
        return ra
    # cong mo lenh mot lan / bar: `if(curTime==prevTime[&&startmanual==0]) return;` o
    # dau ham mo + `prevTime=curTime;` cuoi ham (chi khi mo lenh thanh cong)
    cong_mo = False
    mg = re.match(r"datetime(\w+)=getCurrentTime\(\);staticdatetime(\w+);if\(\1==\2"
                  r"(?:and(\w+)==0)?\)\{?return;\}?", gm)
    if mg and gm.endswith(f"{mg.group(2)}={mg.group(1)};") and \
            len(re.findall(rf"(?<![\w.]){mg.group(2)}=(?!=)", gm)) == 1:
        if mg.group(3) is None or re.search(
                rf"\b{ten_mo}\s*\([^)]*\b{mg.group(3)}\s*=\s*0\s*\)", vb):
            cong_mo = True
    ro = {"lot_dau": lot0, "hop_dong": 100000.0,
          "dinh": dinh or None, "cat_lo": cat_lo, "hedge": hedge}
    if luoi is not None:
        ro["luoi"] = luoi
        ro["cong_mo_bar"] = cong_mo
    if magic:
        ra["ghi"].append("loc magic number: gia dinh tai khoan chi co EA nay")
    ra["ro"] = ro
    mo_ta = [f"dong theo TONG loi lo ca ro (tien, `{bien_loi}`), lenh dau {lot0:g} lot"]
    if dinh:
        mo_ta.append(f"chot dinh: dinh>={dinh['moc']:g} va loi{dinh.get('phep', '<')}"
                     f"dinh*{dinh['ti_le']:g} -> dong het"
                     + (" (dinh ve 0 khi loi<=0)" if dinh["reset_am"] else "")
                     + (" (dinh ve 0 khi vao lenh)" if reset_vao else ""))
    if cat_lo is not None:
        mo_ta.append(f"cat lo ro: loi<={cat_lo:g} -> dong het")
    for h in hedge:
        mo_ta.append(f"hedge NGUOC chieu {h['lot']:g} lot khi so lenh=={h['khi_so_lenh']} va "
                     + (f"gia cham gia_vao -+ {h['khoang_diem']:g} point" if h["kich"] == "diem"
                        else f"loi<={h['nguong']:g}")
                     + (" (dinh ve 0)" if h["reset_dinh"] else ""))
    if luoi is not None:
        L = luoi["lot"]
        mo_ta.append(
            f"luoi martingale CUNG chieu: moi bar (lan goi dau) neu gia <= S (mua) / >= S (ban) "
            f"-> them lenh, S moi = {luoi['buoc']['mua'][0]}{luoi['buoc']['mua'][1]:+g} point (mua)"
            f" / {luoi['buoc']['ban'][0]}{luoi['buoc']['ban'][1]:+g} point (ban); lot "
            + ", ".join(f"{x:g}" for x in L[:6]) + f", ... (khong gioi han so lenh)"
            + (" (dinh ve 0)" if luoi["reset_dinh"] else ""))
        if cong_mo:
            mo_ta.append("mo lenh dau toi da mot lan moi bar (cong prevTime cua ham mo)")
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


# ---------------------------------------------------------------------------
# LUOI MARTINGALE (Breakout5 / Breakout5-2-2) - them 10/10/2026 toi
#
# Ham dong cua hai EA nay (sau phan chot dinh) co CONG BAR:
#     if(curTime==prevTime) return;      // prevTime static, gan = curTime cuoi ham
#     if(postotal>0 | hedgeatlevel==0 || ...) {
#        up = Tradesinfo.initup && gia <= Tradesinfo.S;  down = !initup && gia >= S;
#        if(up||down) { peakwin=0; type/price theo up/down; S = BID -+ R*_Point;
#                       volume = round2(lastvolume*volumefactor); lastvolume=volume;
#                       trade.PositionOpen(_Symbol,type,volume,price,NULL,NULL); } }
# -> them lenh CUNG chieu lenh dau, KHONG gioi han so lenh, moi bar toi da mot lan
# (lan goi ham dong DAU TIEN cua bar). Khoi luong: chuoi nhan tung buoc, lam tron.
#
# Khong viet regex cho tung dong: khoi lenh duoc CHAY THU bang mot trinh thong dich
# MQL nho (`_ThongDich`) tren hai truong hop (lenh dau mua / ban). Moi thu nam ngoai
# tap con hieu duoc (ham la, bien khong ro, dieu kien phu thuoc so lenh ngoai `>0`)
# -> `_Kh` -> KHONG dich (tra None + ly do). Khoi luong lay bang cach chay that
# chuoi gan `lastvolume` -> danh sach lot cu the (khong doan cong thuc).
# ---------------------------------------------------------------------------
class _Kh(Exception):
    """Khong hieu / khong chac -> khong dich."""


class _KhBien(_Kh):
    """Bien khong ro gia tri (khong phai cau truc la)."""


class _Unk:
    def __repr__(self) -> str:
        return "UNK"


UNK = _Unk()


class Gia:
    """Gia tuyen tinh: goc (BID | ASK | None) + diem * _Point."""
    __slots__ = ("goc", "diem")

    def __init__(self, goc, diem: float):
        self.goc, self.diem = goc, float(diem)

    def __add__(self, o):
        if isinstance(o, Gia) and (self.goc is None or o.goc is None):
            return Gia(self.goc or o.goc, self.diem + o.diem)
        raise _Kh("cong hai gia co goc")

    def __sub__(self, o):
        if isinstance(o, Gia) and o.goc is None:
            return Gia(self.goc, self.diem - o.diem)
        raise _Kh("tru gia")

    def nhan(self, k: float):
        if self.goc is not None:
            raise _Kh("nhan gia co goc")
        return Gia(None, self.diem * k)

    def __eq__(self, o):
        return isinstance(o, Gia) and o.goc == self.goc and abs(o.diem - self.diem) < 1e-9

    def __hash__(self):
        return hash((self.goc, round(self.diem, 9)))

    def __repr__(self) -> str:
        return f"Gia({self.goc},{self.diem:g})"


class SoLenh:
    """`postotal` trong ham dong: luon >= 1 (ham dong chi chay khi co vi the)."""


_TOK = re.compile(r"\s*(?:(\d+\.\d*|\.\d+|\d+)|([A-Za-z_]\w*(?:\.\w+)*)|"
                  r"(==|!=|<=|>=|&&|\|\||\+\+|--|[-+*/<>!(),\[\]]))")
_KIEU = r"(?:double|int|long|ulong|bool|datetime|ENUM_ORDER_TYPE|CTrade|MqlRates|MqlDateTime|string)"
_ENUM = {"ORDER_TYPE_BUY", "ORDER_TYPE_SELL", "SYMBOL_BID", "SYMBOL_ASK", "_Symbol", "_Period"}


def _token(s: str) -> list[str]:
    ra, i = [], 0
    s = s.strip()
    while i < len(s):
        m = _TOK.match(s, i)
        if not m or m.end() == i:
            raise _Kh(f"ky tu la `{s[i:i + 10]}`")
        ra.append(m.group(1) or m.group(2) or m.group(3))
        i = m.end()
        while i < len(s) and s[i].isspace():
            i += 1
    return ra


def _lam_tron(x: float, d: int = 0) -> float:
    """MathRound / NormalizeDouble: lam tron NUA XA 0 (khong phai banker)."""
    k = 10.0 ** d
    v = abs(x) * k
    r = float(int(v + 0.5 + 1e-9)) / k
    return r if x >= 0 else -r


class _ThongDich:
    """Thong dich mot tap con MQL5 (khoi lenh, khong vong lap)."""

    def __init__(self, vb: str, nhap: dict, sau: int = 0):
        self.vb, self.nhap, self.sau = vb, nhap, sau
        self.env: dict = {}
        self.lenh_mo: list[dict] = []
        self.loi_ham = 0

    # ---------------- bieu thuc
    def bt(self, s: str):
        self._t = _token(s)
        self._i = 0
        nut = self._or()
        if self._i != len(self._t):
            raise _Kh(f"thua token `{self._t[self._i]}`")
        return nut

    def _nhin(self):
        return self._t[self._i] if self._i < len(self._t) else None

    def _an(self, x=None):
        t = self._nhin()
        if x is not None and t != x:
            raise _Kh(f"can `{x}`, gap `{t}`")
        self._i += 1
        return t

    def _or(self):
        a = self._and()
        while self._nhin() in ("or", "||"):
            self._an()
            b = self._and()
            a = ("or", a, b)
        return a

    def _and(self):
        a = self._ss()
        while self._nhin() in ("and", "&&"):
            self._an()
            b = self._ss()
            a = ("and", a, b)
        return a

    def _ss(self):
        a = self._cong()
        while self._nhin() in ("==", "!=", "<", ">", "<=", ">="):
            op = self._an()
            a = ("ss", op, a, self._cong())
        return a

    def _cong(self):
        a = self._nhan()
        while self._nhin() in ("+", "-"):
            op = self._an()
            a = ("bin", op, a, self._nhan())
        return a

    def _nhan(self):
        a = self._mot()
        while self._nhin() in ("*", "/"):
            op = self._an()
            a = ("bin", op, a, self._mot())
        return a

    def _mot(self):
        t = self._nhin()
        if t in ("!", "not"):
            self._an()
            return ("not", self._mot())
        if t == "-":
            self._an()
            return ("bin", "-", ("so", 0.0), self._mot())
        if t == "(":
            # ep kieu `(long)x`
            if self._i + 2 < len(self._t) and re.fullmatch(_KIEU, self._t[self._i + 1] or "") \
                    and self._t[self._i + 2] == ")":
                self._i += 3
                return ("ep", self._mot())
            self._an("(")
            a = self._or()
            self._an(")")
            return a
        return self._goc()

    def _goc(self):
        t = self._an()
        if t is None:
            raise _Kh("het bieu thuc")
        if re.fullmatch(r"\d+\.\d*|\.\d+|\d+", t):
            return ("so", float(t))
        if not re.fullmatch(r"[A-Za-z_]\w*(?:\.\w+)*", t):
            raise _Kh(f"token la `{t}`")
        if self._nhin() == "(":
            self._an("(")
            ds = []
            if self._nhin() != ")":
                ds.append(self._or())
                while self._nhin() == ",":
                    self._an(",")
                    ds.append(self._or())
            self._an(")")
            return ("goi", t, ds)
        if self._nhin() == "[":
            raise _Kh("mang")
        return ("ten", t)

    def gt(self, nut):
        k = nut[0]
        if k == "so":
            return nut[1]
        if k == "ten":
            return self._ten(nut[1])
        if k == "ep":
            v = self.gt(nut[1])
            return v if isinstance(v, (int, float)) and not isinstance(v, bool) else UNK
        if k == "not":
            v = self._bool(self.gt(nut[1]))
            return not v
        if k == "and":
            return self._bool(self.gt(nut[1])) and self._bool(self.gt(nut[2]))
        if k == "or":
            return self._bool(self.gt(nut[1])) or self._bool(self.gt(nut[2]))
        if k == "ss":
            return self._ss_gt(nut[1], self.gt(nut[2]), self.gt(nut[3]))
        if k == "bin":
            return self._bin(nut[1], self.gt(nut[2]), self.gt(nut[3]))
        if k == "goi":
            return self._goi(nut[1], nut[2])
        raise _Kh(f"nut la {k}")

    def _bool(self, v) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return v != 0
        raise _Kh(f"dieu kien khong ro ({v!r})")

    def _ten(self, t: str):
        if t in self.env:
            v = self.env[t]
            if v is UNK:
                raise _KhBien(f"bien `{t}` khong ro")
            return v
        if t in ("true", "false"):
            return t == "true"
        if t == "NULL":
            return None
        if t == "_Point":
            return Gia(None, 1.0)
        if t in _ENUM:
            return t
        if t in self.nhap:
            return float(self.nhap[t])
        raise _KhBien(f"bien `{t}` khong ro")

    def _ss_gt(self, op, a, b):
        if isinstance(a, SoLenh) or isinstance(b, SoLenh):
            if isinstance(b, SoLenh):
                a, b = b, a
                op = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}.get(op, op)
            if isinstance(b, (int, float)) and not isinstance(b, bool):
                if (op == ">" and b < 1) or (op == ">=" and b <= 1):
                    return True
                if (op == "<" and b <= 1) or (op == "<=" and b < 1) or (op == "==" and b < 1):
                    return False
            raise _Kh("dieu kien phu thuoc so lenh")
        if isinstance(a, str) or isinstance(b, str):
            if op == "==":
                return a == b
            if op == "!=":
                return a != b
            raise _Kh("so sanh chuoi")
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)):
            raise _Kh(f"so sanh khong ro ({a!r} {op} {b!r})")
        return {"==": a == b, "!=": a != b, "<": a < b, ">": a > b,
                "<=": a <= b, ">=": a >= b}[op]

    def _bin(self, op, a, b):
        so = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)  # noqa: E731
        if so(a) and so(b):
            if op == "/" and b == 0:
                raise _Kh("chia 0")
            return {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else 0}[op]
        if isinstance(a, Gia) or isinstance(b, Gia):
            if op == "+" and isinstance(a, Gia) and isinstance(b, Gia):
                return a + b
            if op == "-" and isinstance(a, Gia) and isinstance(b, Gia):
                return a - b
            if op == "*" and isinstance(a, Gia) and so(b):
                return a.nhan(b)
            if op == "*" and isinstance(b, Gia) and so(a):
                return b.nhan(a)
        raise _Kh(f"phep {op} khong ro")

    def _goi(self, ten: str, ds: list):
        if ten == "SymbolInfoDouble" and len(ds) == 2:
            a, b = self.gt(ds[0]), self.gt(ds[1])
            if a == "_Symbol" and b in ("SYMBOL_BID", "SYMBOL_ASK"):
                return Gia(b[7:], 0.0)
            raise _Kh("SymbolInfoDouble la")
        if ten in ("NormalizeDouble", "MathRound"):
            x = self.gt(ds[0])
            d = int(self.gt(ds[1])) if ten == "NormalizeDouble" and len(ds) == 2 else 0
            if isinstance(x, Gia):
                return x                   # chuan hoa gia: khong doi muc
            if isinstance(x, (int, float)) and not isinstance(x, bool):
                return _lam_tron(float(x), d)
            raise _Kh("lam tron gia tri khong ro")
        if ten in ("MathMax", "MathMin") and len(ds) == 2:
            a, b = self.gt(ds[0]), self.gt(ds[1])
            if all(isinstance(x, (int, float)) for x in (a, b)):
                return max(a, b) if ten == "MathMax" else min(a, b)
            raise _Kh("MathMax/Min khong ro")
        if not ds and self.sau < 3:
            t = than_ham(self.vb, ten)
            if t is not None:
                return _ThongDich(self.vb, self.nhap, self.sau + 1).ham_thuan(
                    self.vb[t[0]:t[1]])
        raise _Kh(f"ham `{ten}` khong ro")

    # ---------------- cau lenh
    def ham_thuan(self, than: str):
        """Ham khong doi so, chi tinh tu input -> gia tri `return`."""
        try:
            self.chay(than)
        except _TraVe as r:
            return r.v
        raise _Kh("ham khong return")

    def chay(self, than: str, long_leo: bool = False) -> None:
        for c in cau_lenh(than):
            if c["loai"] == "khoi":
                self.chay(c["than"], long_leo)
                continue
            if c["loai"] == "if":
                dk = c["dk"]
                if "PositionOpen(" in dk:
                    m = re.fullmatch(r"\s*!\s*(\w+\.PositionOpen\(.*\))\s*", dk, re.S)
                    if not m:
                        raise _Kh("PositionOpen trong dieu kien la")
                    self._mo(m.group(1))
                    di = False                  # gia dinh lenh vao thanh cong
                else:
                    try:
                        di = self._bool(self.gt(self.bt(dk)))
                    except _Kh:
                        if long_leo:
                            continue           # bo qua (che do quet bien cuc bo)
                        raise
                if di:
                    self.chay(c["than"], long_leo)
                elif c["khac"] is not None:
                    self.chay(c["khac"], long_leo)
                continue
            self._don(c["than"].strip().rstrip(";").strip(), long_leo)

    def _don(self, t: str, long_leo: bool) -> None:
        if not t:
            return
        m = re.fullmatch(r"return\s*(.*)", t, re.S)
        if m:
            if long_leo:
                return
            raise _TraVe(self.gt(self.bt(m.group(1))) if m.group(1).strip() else None)
        m = re.fullmatch(rf"(?:static\s+)?(?:const\s+)?{_KIEU}\s+(.+)", t, re.S)
        if m:
            for p in _tach_doi(m.group(1)):
                p = p.strip()
                mm = re.fullmatch(r"(\w+)\s*(?:\[\s*\d*\s*\])?\s*(?:=\s*(.+))?", p, re.S)
                if not mm:
                    raise _Kh(f"khai bao la `{p[:30]}`")
                self._gan(mm.group(1), mm.group(2), long_leo)
            return
        m = re.fullmatch(r"([A-Za-z_][\w.]*)\s*(=|\+=|-=)\s*(.+)", t, re.S)
        if m and not m.group(3).startswith("="):
            ten, op, ve = m.groups()
            if op == "=":
                self._gan(ten, ve, long_leo)
            else:
                try:
                    v = self._bin(op[0], self._ten(ten), self.gt(self.bt(ve)))
                except _KhBien:
                    v = UNK                    # van chua ro - chi loi neu ve sau DUNG no
                except _Kh:
                    if not long_leo:
                        raise
                    v = UNK
                self.env[ten] = v
            return
        m = re.fullmatch(r"(\w+)\.(\w+)\((.*)\)", t, re.S)
        if m:
            if m.group(2) == "PositionOpen":
                self._mo(t)
                return
            if m.group(2) == "SetExpertMagicNumber":
                return
        if re.fullmatch(r"Print\(.*\)", t, re.S):
            return
        if long_leo:
            return
        raise _Kh(f"cau lenh la `{t[:40]}`")

    def _gan(self, ten: str, ve: str | None, long_leo: bool) -> None:
        if ve is None:
            self.env[ten] = UNK
            return
        try:
            self.env[ten] = self.gt(self.bt(ve))
        except _KhBien:
            self.env[ten] = UNK                # chua ro; chi loi neu ve sau DUNG no
        except _Kh:
            if not long_leo:
                raise
            self.env[ten] = UNK

    def _mo(self, t: str) -> None:
        m = re.fullmatch(r"\s*\w+\.PositionOpen\((.*)\)\s*", t, re.S)
        ds = [x.strip() for x in _tach_doi(m.group(1))] if m else []
        if len(ds) != 6 or ds[0] != "_Symbol" or ds[4] not in ("NULL", "0") or \
                ds[5] not in ("NULL", "0"):
            raise _Kh("PositionOpen khong o dang (_Symbol,type,volume,price,NULL,NULL)")
        self.lenh_mo.append({"type": self.gt(self.bt(ds[1])),
                             "volume": self.gt(self.bt(ds[2])),
                             "price": self.gt(self.bt(ds[3]))})


class _TraVe(Exception):
    def __init__(self, v):
        self.v = v


def _nhap_cua(khai: dict | None) -> dict:
    return {k: v["gia_tri"] for k, v in (khai or {}).items()
            if isinstance(v, dict) and isinstance(v.get("gia_tri"), (int, float))}


def gia_tri_thuan(bt: str, vb: str, khai: dict | None) -> float | None:
    """Bieu thuc chi phu thuoc input (va ham thuan) -> so; khong chac -> None."""
    try:
        v = _ThongDich(vb, _nhap_cua(khai)).gt(_ThongDich(vb, {}).bt(bt))
    except (_Kh, _TraVe, ValueError, ZeroDivisionError, RecursionError):
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return float(v)


def _co_ham_dem(vb: str, ten: str, kieu: str) -> bool:
    """Ham dem / co vi the loc theo magic: `kieu` = "dem" (X++) | "co" (X=true)."""
    t = than_ham(vb, ten)
    if not t:
        return False
    g = _gon(vb[t[0]:t[1]])
    if kieu == "dem":
        m = re.fullmatch(r"int(\w+)=0;inti=PositionsTotal\(\)-1;while\(i>=0\)\{PositionGetSymbol"
                         r"\(i\);long(\w+)=PositionGetInteger\(POSITION_MAGIC\);if\(\2==magicnumber"
                         r"\)\1\+\+;i--;\}return\1;", g)
    else:
        m = re.fullmatch(r"bool(\w+)=false;inti=PositionsTotal\(\)-1;while\(i>=0\)\{PositionGetSymbol"
                         r"\(i\);long(\w+)=PositionGetInteger\(POSITION_MAGIC\);if\(\2==magicnumber"
                         r"\)\1=true;i--;\}return\1;", g)
    return m is not None


def _bo_loc_magic(g: str) -> str:
    """Bo loc `posmagic==magicnumber` (gia dinh tai khoan chi co EA nay)."""
    m = re.search(r"long(\w+)=PositionGetInteger\(POSITION_MAGIC\);", g)
    if not m:
        return g
    v = m.group(1)
    g = g.replace(m.group(0), "")
    g = re.sub(rf"if\({v}==magicnumber\)\{{(.*?)\}}", r"\1", g)
    g = re.sub(rf"if\({v}==magicnumber\)", "", g)
    g = g.replace("trade.SetExpertMagicNumber(magicnumber);", "")
    if v in g or "MAGIC" in g:
        return "MAGIC?"
    return g


def doc_luoi(c: dict, vb: str, gm: str, khai: dict | None,
             bien_so: str | None, bien_dinh: str | None) -> tuple[dict | None, str, bool]:
    """Khoi `if(COND){ up=..; down=..; if(up||down){...} }` cua ham dong (sau cong bar).

    Tra (luoi | None, ly do, else_chet). `gm` = than ham mo (van ban THO, da chuan hoa)."""
    nhap = _nhap_cua(khai)
    td = _ThongDich(vb, nhap)
    if bien_so:
        td.env[bien_so] = SoLenh()
    try:
        luon = td._bool(td.gt(td.bt(c["dk"])))
    except _Kh as e:
        return None, f"dieu kien khoi luoi khong chac: {e}", False
    if not luon:
        return None, "khoi luoi khong bao gio chay", False
    ds = cau_lenh(c["than"])
    ds = [x for x in ds if not (x["loai"] == "don" and re.fullmatch(
        rf"{_KIEU}\s+\w+(?:\s*,\s*\w+)*", x["than"].strip().rstrip(";").strip()))]
    if len(ds) != 3 or ds[0]["loai"] != "don" or ds[1]["loai"] != "don" or ds[2]["loai"] != "if":
        return None, "khoi luoi khong o dang `up=..; down=..; if(up||down){..}`", False
    g0, g1 = _gon(ds[0]["than"]).rstrip(";"), _gon(ds[1]["than"]).rstrip(";")
    m1 = re.fullmatch(r"(\w+)=Tradesinfo\.initupand_gia0_<=Tradesinfo\.(\w+)", g0)
    m2 = re.fullmatch(r"(\w+)=!Tradesinfo\.initupand_gia0_>=Tradesinfo\.(\w+)", g1)
    if not (m1 and m2) or m1.group(2) != m2.group(2):
        return None, "dieu kien them lenh khong o dang `initup && gia<=S` / `!initup && gia>=S`", False
    xu, xd, S = m1.group(1), m2.group(1), m2.group(2)
    if _gon(ds[2]["dk"]) not in (f"{xu}or{xd}", f"{xd}or{xu}") or ds[2]["khac"] is not None:
        return None, "khong thay `if(up||down)`", False
    trong = ds[2]["than"]
    # --- muc dau (ham mo): chay khoi `if(up||down){...}` cua ham mo cho 2 truong hop
    tmo = cau_lenh(gm)
    khoi_mo = [x for x in tmo if x["loai"] == "if" and "PositionOpen(" in x["than"]]
    if len(khoi_mo) != 1:
        return None, "ham mo khong co dung mot khoi chua PositionOpen", False
    km = khoi_mo[0]
    hh = _tach_hoac(km["dk"])
    if len(hh) != 2:
        return None, "lenh dau khong o dang `if(up||down)`", False
    ket = {}
    for ca in ((True, False), (False, True)):
        # quet bien cuc bo truoc khoi (vd `int steprange=StepRange;`)
        t0 = _ThongDich(vb, nhap)
        t0.chay(gm[:km["a"]], long_leo=True)
        t0.env[hh[0]], t0.env[hh[1]] = ca
        t0.env["Tradesinfo.lastvolume"] = UNK
        try:
            _chay_mo(t0, km["than"])
        except _Kh as e:
            return None, f"lenh dau: {e}", False
        if len(t0.lenh_mo) != 1:
            return None, "lenh dau: khong dung mot PositionOpen", False
        lm = t0.lenh_mo[0]
        if lm["type"] not in ("ORDER_TYPE_BUY", "ORDER_TYPE_SELL"):
            return None, "lenh dau: chieu khong ro", False
        chieu = 1 if lm["type"] == "ORDER_TYPE_BUY" else -1
        if chieu in ket:
            return None, "lenh dau: hai nhanh cung chieu", False
        if t0.env.get("Tradesinfo.initup") is not (chieu > 0):
            return None, "lenh dau: initup khong khop chieu", False
        s0 = t0.env.get(f"Tradesinfo.{S}")
        lot0 = t0.env.get("Tradesinfo.lastvolume")
        if not isinstance(s0, Gia) or s0.goc not in ("BID", "ASK"):
            return None, f"lenh dau: Tradesinfo.{S} khong phai gia BID/ASK -+ k*_Point", False
        if not isinstance(lot0, (int, float)) or lot0 != lm["volume"]:
            return None, "lenh dau: lastvolume != volume", False
        if bien_dinh and t0.env.get(bien_dinh) != 0:
            return None, "lenh dau: khong dat lai dinh", False
        # --- lenh them: chay `trong` voi up/down
        lots, muc, lenh = [], None, None
        lv = float(lot0)
        for buoc in range(60):
            t1 = _ThongDich(vb, nhap)
            if bien_so:
                t1.env[bien_so] = SoLenh()
            t1.env[xu], t1.env[xd] = (chieu > 0), (chieu < 0)
            t1.env["Tradesinfo.initup"] = (chieu > 0)
            t1.env["Tradesinfo.lastvolume"] = lv
            t1.env["Tradesinfo.totalvolume"] = UNK
            t1.env["Tradesinfo.initprice"] = UNK
            if bien_dinh:
                t1.env[bien_dinh] = UNK
            try:
                t1.chay(trong)
            except _Kh as e:
                return None, f"lenh them: {e}", False
            except _TraVe:
                return None, "lenh them: return giua khoi", False
            if len(t1.lenh_mo) != 1:
                return None, "lenh them: khong dung mot PositionOpen", False
            lm1 = t1.lenh_mo[0]
            v = lm1["volume"]
            if not isinstance(v, (int, float)) or v <= 0:
                return None, "lenh them: khoi luong khong ro", False
            if t1.env.get("Tradesinfo.lastvolume") != v:
                return None, "lenh them: lastvolume != volume", False
            m_ = t1.env.get(f"Tradesinfo.{S}")
            if not isinstance(m_, Gia) or m_.goc not in ("BID", "ASK"):
                return None, f"lenh them: Tradesinfo.{S} moi khong ro", False
            dd = (lm1["type"], lm1["price"], m_)
            if lenh is None:
                lenh = dd
            elif dd != lenh:
                return None, "lenh them: hanh vi doi theo buoc (khong dich)", False
            if bien_dinh and t1.env.get(bien_dinh) != 0:
                return None, "lenh them: dinh khong ve 0 (chua ho tro)", False
            lots.append(round(float(v), 8))
            lv = float(v)
            if lv > 1e7:
                break
        ty, pr, mm = lenh
        ch_them = 1 if ty == "ORDER_TYPE_BUY" else -1
        if not isinstance(pr, Gia) or pr.diem != 0 or pr.goc != ("ASK" if ch_them > 0 else "BID"):
            return None, "lenh them: gia vao khong phai ASK (mua) / BID (ban)", False
        ket[chieu] = {"muc_dau": [s0.goc, s0.diem], "buoc": [mm.goc, mm.diem],
                      "chieu_them": ch_them * chieu, "lot": lots, "lot_dau": float(lot0)}
    a, b = ket[1], ket[-1]
    if a["lot"] != b["lot"] or a["chieu_them"] != b["chieu_them"] or a["lot_dau"] != b["lot_dau"]:
        return None, "luoi mua/ban khong doi xung", False
    luoi = {"cong_bar": True, "cung_chieu": a["chieu_them"] == 1,
            "phep": {"mua": "<=", "ban": ">="},
            "muc_dau": {"mua": a["muc_dau"], "ban": b["muc_dau"]},
            "buoc": {"mua": a["buoc"], "ban": b["buoc"]},
            "lot": a["lot"], "reset_dinh": bool(bien_dinh), "lot_dau": a["lot_dau"]}
    return luoi, "", c["khac"] is not None


def _chay_mo(t0: "_ThongDich", than: str) -> None:
    """Chay khoi lenh dau: bien khong ro (stopLevel, tp...) duoc phep neu khong dung."""
    for c in cau_lenh(than):
        if c["loai"] == "if" and "PositionOpen(" not in c["dk"] and "PositionOpen(" not in c["than"]:
            di = t0._bool(t0.gt(t0.bt(c["dk"])))
            if di:
                _chay_mo(t0, c["than"])
            elif c["khac"] is not None:
                _chay_mo(t0, c["khac"])
            continue
        if c["loai"] == "if":
            t0.chay(f"if({c['dk']}){{{c['than']}}}" + (
                f"else{{{c['khac']}}}" if c["khac"] is not None else ""))
            continue
        if c["loai"] == "khoi":
            _chay_mo(t0, c["than"])
            continue
        t0._don(c["than"].strip().rstrip(";").strip(), long_leo=True)


def _tach_hoac(dk: str) -> list[str]:
    p = [x.strip() for x in re.split(r"\s+or\s+|\|\|", dk.strip())]
    return p if len(p) == 2 and all(re.fullmatch(r"\w+", x) for x in p) else []
