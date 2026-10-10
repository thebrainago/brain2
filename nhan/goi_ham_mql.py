# -*- coding: utf-8 -*-
"""GOI HAM MQL5 - lenh vao nam trong HAM PHU, dieu kien vao o CHO GOI (them 11/10/2026).

Do that tren 160 EA MQL5 Code Base (`reports/CAU_KHO_MA.md`): loi so 1 la
"khong tim duoc guard cua lenh vao" (63 lan) - EA viet

    void OnTick(){ ... if(rsi < 30) OpenBuy(); ... }
    void OpenBuy(){ ... trade.Buy(Lots, _Symbol, ...); }

nen lenh vao (`trade.Buy`) khong co `if` nao bao trong ham cua no. Bo doc cu chi
xem `if` trong CUNG ham -> bo qua. File nay NANG vi tri lenh vao len CHO GOI ham
phu va doc dieu kien o do - CHI KHI do thi goi nho va giai duoc tron ven, khong
doan. Thieu mot dieu -> tu choi CO LY DO (giong `chot_mql`, `fss_mql`).

Dieu kien nhan (moi dieu deu kiem tren ma):
  1. ham chua lenh vao F la ham TU DO (khong nam trong class/struct), than ham
     xac dinh bang ngoac (khong dung `_KHAI_HAM` vi no bo sot kieu tra ve `ulong`,
     `ENUM_*`...), dinh nghia DUNG MOT lan (khong overload), khong la ham su kien;
  2. trong F, lenh vao o muc than ham (khong trong for/while/switch/else) va moi
     `return` truoc lenh vao la thoat som CHAC CHAN (`_thoat_som`), khong co
     return long co dieu kien (`_return_long`);
  3. F duoc goi tu DUNG MOT cho (khong goi qua `.F(` / `->F(` / con tro ham), cho
     goi la mot LENH don: `F(..);`, `x = F(..);`, `return F(..);`, `if(F(..))`,
     `if(!F(..))`, co the dung sau cac `if(dk)` cung dong - khong nam trong bieu
     thuc `?:`, `and`/`or` hay doi so cua ham khac (khi do dieu kien bi rut gon);
  4. lap lai 1-3 di len (toi da 4 tang) toi `OnTick`; chuoi KHONG toi `OnTick`
     (vd chi tu `OnChartEvent` = bam nut tay, `OnTimer`, `OnTrade`) -> tu choi;
  5. TANG DIEU KIEN = tang DUY NHAT co dieu kien khong phai quan tri (`if` bao
     cho goi HOAC thoat som `if(dk) return;` truoc no); chi tang do duoc dich
     (cung vi tri nhu bo doc cu). Moi `if`/thoat som o tang KHAC phai la quan
     tri / kiem loi API (ghi `bo_qua_quan_tri`) - hai tang co dieu kien -> tu
     choi, vi bien cuc bo cua tang nay khong giai duoc o vi tri tang kia;
  6. khong co `else` o bat ky tang nao (nhanh else = dieu kien phu dinh chua dich).

Ket qua dung lai nguyen duong dich guard cua `doc_ma` (no_dieu_kien, phu_dinh,
mau_thuan...). Ham nay chi tim VI TRI va DIEU KIEN, khong dich.
"""
from __future__ import annotations

import re

_TEN = r"[A-Za-z_][A-Za-z0-9_]*"
_SU_KIEN = {"OnTick", "OnTimer", "OnInit", "OnDeinit", "OnChartEvent", "OnTrade",
            "OnTradeTransaction", "OnBookEvent", "OnTester", "OnTesterInit",
            "OnTesterPass", "OnTesterDeinit", "OnStart", "OnCalculate"}
_TU_KHOA = {"if", "for", "while", "switch", "return", "sizeof", "do", "else", "case",
            "new", "delete"}
TANG_TOI_DA = 4


def _D():
    from nhan import doc_ma as D                  # tre: tranh vong import
    return D


def mat_na(vb: str) -> str:
    """Ban CUNG DO DAI voi chuoi, ky tu va chu thich khoi bi thay bang khoang trang
    (de dem ngoac / tim loi goi khong vap `"{"` hay `"OpenBuy("` trong Print)."""
    ra = list(vb)
    i, n = 0, len(vb)
    while i < n:
        c = vb[i]
        if c == '"' or c == "'":
            j = i + 1
            while j < n and vb[j] != c and vb[j] != "\n":
                j += 2 if vb[j] == "\\" else 1
            for k in range(i + 1, min(j, n)):
                ra[k] = " "
            i = j + 1
            continue
        if vb.startswith("/*", i):
            j = vb.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if ra[k] != "\n":
                    ra[k] = " "
            i = j
            continue
        if vb.startswith("//", i):
            j = vb.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                ra[k] = " "
            i = j
            continue
        i += 1
    return "".join(ra)


def _khoi_cap_cao(mn: str) -> list[tuple[int, int]]:
    """Moi khoi `{...}` o muc 0 cua file: (mo, dong). Ngoac lech -> []."""
    ra, muc, mo = [], 0, -1
    for i, c in enumerate(mn):
        if c == "{":
            if muc == 0:
                mo = i
            muc += 1
        elif c == "}":
            muc -= 1
            if muc < 0:
                return []
            if muc == 0:
                ra.append((mo, i))
    return ra if muc == 0 else []


def _dau_khoi(mn: str, mo: int) -> str:
    """Van ban dau khoi (tu het lenh/khoi truoc toi `{`)."""
    j, sau = mo - 1, 0
    while j >= 0:
        c = mn[j]
        if c == ")":
            sau += 1
        elif c == "(":
            sau -= 1
        elif sau == 0 and c in ";}{":
            break
        j -= 1
    return mn[j + 1:mo].strip()


def ham_tu_do(mn: str) -> dict[str, list[dict]]:
    """Ten ham tu do -> [{mo, dong, tham_so}] (nhieu phan tu = overload/trung ten).
    Khoi cap cao khong phai ham (class/struct/enum/namespace) bi bo qua."""
    ra: dict[str, list[dict]] = {}
    for mo, dong in _khoi_cap_cao(mn):
        dau = re.sub(r"\s+", " ", _dau_khoi(mn, mo))
        if re.match(r"(?:class|struct|enum|union|namespace|interface)\b", dau) or \
                re.search(r"\b(?:class|struct|enum|union)\s+\w+[^()]*$", dau):
            continue
        m = re.search(rf"(?:^|[\s\*&>])({_TEN})\s*\((.*)\)\s*(?:const\s*)?$", dau)
        if not m or m.group(1) in _TU_KHOA or "::" in dau[:m.start(1)][-3:]:
            continue
        if "::" in dau:                            # phuong thuc lop dinh nghia ngoai lop
            continue
        ra.setdefault(m.group(1), []).append(
            {"mo": mo, "dong": dong, "tham_so": m.group(2)})
    return ra


def _ham_chua(bang: dict, vi: int) -> tuple[str, dict] | None:
    for ten, ds in bang.items():
        for h in ds:
            if h["mo"] < vi < h["dong"]:
                return ten, h
    return None


def _khoi_bao(mn: str, mo: int, vi: int) -> list[tuple[int, str]]:
    """Cac khoi con mo tai `vi` (trong than ham `mo`): (vi tri `{`, dau khoi)."""
    ra, muc = [], 0
    for i in range(vi - 1, mo, -1):
        c = mn[i]
        if c == "}":
            muc += 1
        elif c == "{":
            if muc == 0:
                ra.append((i, _dau_khoi(mn, i)))
            else:
                muc -= 1
    return ra


def _loai_khoi(dau: str) -> str:
    d = dau.strip()
    if re.match(r"(?:else\s+)?if\s*\(", d) and d.endswith(")"):
        return "else" if d.startswith("else") else "if"
    if re.fullmatch(r"else", d):
        return "else"
    if d == "":
        return "khoi"
    k = re.match(r"(\w+)", d)
    return k.group(1) if k else "khac"


def _cau_lenh_dau(mn: str, vi: int) -> int:
    """Vi tri bat dau cau lenh chua `vi` (sau `;`, `{`, `}` gan nhat)."""
    j = vi - 1
    while j >= 0 and mn[j] not in ";{}":
        j -= 1
    return j + 1


_TIEN_TO_DON = re.compile(
    rf"^(?:(?:(?:const\s+)?\w+\s+)?{_TEN}(?:\[[^\]]*\])?\s*=\s*|return\s*\(?\s*"
    rf"|if\s*\(\s*!?\s*\(?\s*)?$")


def _cho_goi_don(mn: str, ten: str, ham: dict) -> tuple[list[int], str | None]:
    """Moi cho goi `ten(` ngoai than chinh no. Tra (ds vi tri, ly do tu choi)."""
    ra = []
    for m in re.finditer(rf"(?<![\w.>:&])({re.escape(ten)})\s*\(", mn):
        p = m.start(1)
        if ham["mo"] - 400 < p < ham["mo"] and not mn[p:ham["mo"]].count(";"):
            continue                                # chinh dau khai bao
        truoc = mn[max(0, p - 120):p]
        if re.search(r"(?:\w|\*|&|>)\s+$", truoc) and \
                re.search(r"\b(?:void|bool|int|uint|long|ulong|double|float|string|"
                          r"datetime|ENUM_\w+|\w+_t|static|virtual)\s*[\*&]?\s*$", truoc):
            continue                                # khai bao truoc (prototype)
        ra.append(p)
    for m in re.finditer(rf"(?:\.|->|::|&)\s*{re.escape(ten)}\b", mn):
        return [], f"ham {ten} duoc tham chieu qua doi tuong/con tro (khong giai duoc do thi goi)"
    for m in re.finditer(rf"(?<![\w.])({re.escape(ten)})\b(?!\s*\()", mn):
        if not (ham["mo"] - 400 < m.start() < ham["mo"]):
            return [], f"ham {ten} dung lam gia tri (con tro ham) - khong giai duoc"
    trong = [p for p in ra if ham["mo"] < p < ham["dong"]]
    if trong:
        return [], f"ham {ten} de quy"
    return ra, None


def _hop_le_cho_goi(mn: str, p: int, ten: str) -> str | None:
    """Cho goi la mot LENH DON (xem dieu 3). None = hop le, chuoi = ly do."""
    a = _cau_lenh_dau(mn, p)
    tien = mn[a:p].strip()
    if re.match(r"else\b", tien):
        return f"loi goi {ten} nam trong nhanh else"
    # bo cac `if(dk)` dung truoc tren cung cau lenh (dk do `_cac_if_bao` doc)
    while True:
        m = re.match(r"if\s*\(", tien)
        if not m:
            break
        k = _D()._dong_ngoac(tien, m.end() - 1)
        if k < 0:
            break                                   # `if(` chua dong: F nam TRONG dieu kien
        tien = tien[k + 1:].strip()
        if re.match(r"else\b", tien):
            return f"loi goi {ten} nam trong nhanh else"
    if not _TIEN_TO_DON.match(tien):
        return f"loi goi {ten} nam trong bieu thuc phuc tap: `{tien[-40:]}`"
    k = _D()._dong_ngoac(mn, mn.find("(", p))
    if k < 0:
        return f"loi goi {ten}: ngoac lech"
    sau = mn[k + 1:k + 80]
    if tien.startswith("if"):
        # `if(F(..)) ...` / `if(!F(..)) ...`: chi duoc dong ngoac, khong noi tiep dk
        if not re.match(r"\s*\)?\s*\)", sau):
            return f"loi goi {ten} nam trong dieu kien ghep"
    elif not re.match(r"\s*\)?\s*;", sau):
        return f"loi goi {ten} nam trong bieu thuc phuc tap"
    if re.search(r"\?|\band\b|\bor\b", mn[a:p]) and not tien.startswith("if"):
        return f"loi goi {ten} sau toan tu dieu kien"
    return None


def _phan_quan_tri(ds: list[str]) -> tuple[list[str], list[str]]:
    """Tach dieu kien thanh (quan tri / kiem loi -> bo qua co ghi, con lai)."""
    D = _D()
    qt, con = [], []
    for g in ds:
        b = D._boc_ngoac(g)
        if D._LA_KIEM_LOI.search(g) or D._la_quan_tri(b) or \
                all(D._la_kiem_loi_du_lieu(x) for x in D._tach_va(b)) or \
                re.search(r"new_?bar|IsNewBar", g, re.I):
            qt.append(g.strip()[:60])
        else:
            con.append(g.strip())
    return qt, con


def nang_cho_goi(vb: str, vi_lenh: int) -> dict:
    """Nang lenh vao tai `vi_lenh` (khong co `if` bao trong ham cua no) len tang dieu kien.

    Tra {"loi": ly_do} hoac {"guards": [(vi, dk)], "vi": vi tri if ngoai cung (hoac
    `den` khi khong co if), "den": cho goi/lenh vao o tang dieu kien, "qt": [quan
    tri bo qua], "tang": [ten ham tu duoi len], "ham": ten tang dieu kien}.
    TANG DIEU KIEN = tang DUY NHAT co dieu kien khong phai quan tri (trong `if` bao
    HOAC thoat som `if(dk) return;` truoc cho goi); `guards` co the rong khi dieu
    kien chi nam o thoat som. Hai tang cung co dieu kien -> tu choi. Khong tang nao
    co -> tu choi (khong co dieu kien vao de dich).
    """
    D = _D()
    mn = mat_na(vb)
    bang = ham_tu_do(mn)
    if not bang:
        return {"loi": "goi ham: khong tach duoc than ham (ngoac lech)"}
    vi, tang, qt = vi_lenh, [], []
    guard = None
    for buoc in range(TANG_TOI_DA + 1):
        hc = _ham_chua(bang, vi)
        if hc is None:
            return {"loi": "goi ham: lenh vao nam trong lop/struct (phuong thuc) - chua giai"}
        ten, ham = hc
        tang.append(ten)
        if len(bang[ten]) > 1:
            return {"loi": f"goi ham: {ten} dinh nghia {len(bang[ten])} lan (overload)"}
        khoi = _khoi_bao(mn, ham["mo"], vi)
        loai = [_loai_khoi(d) for _, d in khoi]
        if "else" in loai:
            return {"loi": f"goi ham: {'lenh vao' if buoc == 0 else 'loi goi'} trong nhanh else ({ten})"}
        xau = [x for x in loai if x not in ("if", "khoi")]
        if xau:
            return {"loi": f"goi ham: {'lenh vao' if buoc == 0 else 'loi goi'} trong khoi "
                           f"{xau[0]} ({ten}) - lap/re nhanh chua dich"}
        ifs, gap_else = D._cac_if_bao(vb, vi)
        if gap_else:
            return {"loi": f"goi ham: nhanh else ({ten})"}
        ifs = [(p, g) for p, g in ifs if ham["mo"] < p < ham["dong"]
               and not D._LA_KIEM_LOI.search(g)
               and not (buoc > 0 and re.search(rf"\b{re.escape(tang[-2])}\s*\(", g))]
        thoat = D._thoat_som(vb, ham["mo"], vi)
        rl = D._return_long(vb, ham["mo"], vi)
        if rl:
            return {"loi": f"goi ham: return long co dieu kien trong {ten}: {rl[0][:40]}"}
        q, con = _phan_quan_tri([g for _, g in ifs] + thoat)
        if con:
            if guard is not None:
                return {"loi": f"goi ham: dieu kien vao o HAI tang ({guard['ham']} va {ten}) - "
                               f"chua dich: {con[0][:40]}"}
            # TANG DIEU KIEN: dich o day (if bao + thoat som tu dau ham toi `vi`)
            guard = {"guards": ifs,
                     "vi": min(p for p, _ in ifs) if ifs else vi, "den": vi, "ham": ten}
        else:
            qt += q
        if ten == "OnTick":
            break
        if ten in _SU_KIEN:
            return {"loi": f"goi ham: chuoi goi toi {ten}, khong toi OnTick "
                           "(lenh tay/timer - khong mo phong theo bar)"}
        if buoc == TANG_TOI_DA:
            return {"loi": f"goi ham: chuoi goi qua {TANG_TOI_DA} tang"}
        ds, ly = _cho_goi_don(mn, ten, ham)
        if ly:
            return {"loi": "goi ham: " + ly}
        if not ds:
            return {"loi": f"goi ham: {ten} khong duoc goi o dau"}
        if len(ds) > 1:
            return {"loi": f"goi ham: {ten} goi tu {len(ds)} cho (OR nhieu dieu kien - chua dich)"}
        ly = _hop_le_cho_goi(mn, ds[0], ten)
        if ly:
            return {"loi": "goi ham: " + ly}
        vi = ds[0]
    if guard is None:
        return {"loi": "goi ham: chuoi toi OnTick khong co dieu kien vao (chi quan tri)"}
    guard["qt"] = qt
    guard["tang"] = tang
    return guard


def goc_ham(vb: str, vi: int) -> int:
    """Vi tri `{` mo than ham tu do chua `vi` (theo ngoac, khong theo `_KHAI_HAM`)."""
    hc = _ham_chua(ham_tu_do(mat_na(vb)), vi)
    return hc[1]["mo"] if hc else 0
