# -*- coding: utf-8 -*-
"""doc_ma.py - DOC MA NGUON THANH NHIEU KHAI BAO CO CHE.

VI SAO CO FILE NAY (chu du an chot 01/09/2026).

Do phieu chuyen doi ngay 01/09 cho thay cho sup khong nam o khau doc ma o khau
BIEN DICH:

    1.905 ban doc -> 376 ung vien -> 460 viec, nhung chi **43 mau rieng biet**
    -> 3 gia thuyet truy nguyen duoc ve tai lieu.

Ba nguyen nhan, deu do duoc:

  1. `bien_dich_ung_vien.do_khop` la bo NHAN DIEN tu khoa, khong phai bo TRICH
     XUAT. Mot tai lieu chi thanh ung vien bang cach goi ten mot mau DA CO trong
     thu vien; theo cau tao no khong bao gio them duoc mot kieu danh moi.
     375/376 ung vien tro vao mau da ton tai.
  2. `TRAN_MOI_TAI_LIEU = 2` - tran cung 2 mau moi tai lieu.
  3. Duong trich co che bi TAT cho ma nguon:
     `if che_do == "van_xuoi" and loai_ban_doc not in ("ma_nguon", ...)`.
     Tuc 247 ban doc MA NGUON - EA MQL5 va Pine, nguon dac nhat, suat ra ung
     vien cao nhat (20,2% so voi 11,9% cua bai bao) - chi duoc so khop tu khoa.

Muc 3 duoc tat ngay 23/08 vi mot ly do DUNG: chu thich markdown trong repo de ra
hai co che sai (`mua_rsi30_tren_70`, `mua_rsi14_tren_30`). Nhung cai duoc tat la
bo doc VAN XUOI; con chinh doan MA thi chua ai doc. Hai thu khac han nhau: van
xuoi noi "mua khi RSI thap" (mo ho o dung cho quan trong nhat), con ma viet
`rsi(close,14) < 30` (khong mo ho gi).

File nay la bo doc MA. No khong doan nghia tu tieng nguoi - no doc ky hieu:

    ma89 = ema(close, 89)        -> bang ky hieu: ma89 = {chi_bao ema, n 89}
    longCond = close > ma89      -> dieu kien: gia.close > ema(89)
    -> khai bao co che day du theo `nhan/ngu_phap.py`

Va no tra ve NHIEU khai bao cho MOT file, dung nhu chu du an noi: mot EA hay mot
Pine script tuong duong nhieu kieu danh. Moi dieu kien so sanh doc lap la mot
kieu danh rieng, de cong tu cham diem tung cai - thay vi gop ca file thanh mot
cai nhan `rsi_dao_chieu` roi chay lai dung luoi tham so cu.

RANH GIOI KHONG DOI (giong `ma_nguon.py` va `thu_hoi_thanh_phan.py`):
**khong bao gio chay ma tai ve**. O day chi doc van ban bang bieu thuc chinh
quy. Dau ra la DU LIEU (khai bao theo ngu phap da kiem duyet), khong phai ma.
Quyen nhan hay tu choi van thuoc `ngu_phap.them_co_che` - no chay ty le kich
hoat va phep cat nhin truoc truoc khi cho vao kho.
"""
from __future__ import annotations

import json
import re

from nhan import thu_hoi_thanh_phan as TP

#: Phep so sanh trong ma -> phep cua ngu phap.
_PHEP = {">": ">", ">=": ">=", "<": "<", "<=": "<="}

#: Ho co che suy tu chi bao. Khong doan duoc thi `khac` - cong van xet binh
#: thuong, chi la khong duoc gom nhom cung ho.
_HO = {
    "rsi": "quay_ve_trung_binh", "ibs": "quay_ve_trung_binh",
    "zscore": "quay_ve_trung_binh", "phan_vi": "quay_ve_trung_binh",
    "ema": "xu_huong", "sma": "xu_huong", "tb": "xu_huong",
    "cao_nhat": "pha_vo", "thap_nhat": "pha_vo",
    "cao_trong_gio": "pha_vo", "thap_trong_gio": "pha_vo",
    "atr": "bien_dong", "do_lech": "bien_dong", "bien_do": "bien_dong",
    "gio": "phien", "ngay_trong_tuan": "lich", "ngay_trong_thang": "lich",
    "thang": "lich", "khoi_luong": "dong_tien",
}

#: Ten cot gia viet trong ma -> toan hang gia cua ngu phap.
_GIA = {"close": "close", "open": "open", "high": "high", "low": "low",
        # --- MQL5 (them 05/09) ---
        "bid": "close", "ask": "close",
        "iclose": "close", "iopen": "open", "ihigh": "high", "ilow": "low",
        "close[0]": "close", "price": "close", "last": "close",
        "currentprice": "close", "gia": "close"}

#: HAM CHI BAO cua MQL5 -> chi bao DSL. `iMA(sym,tf,n,shift,method,price)`:
#: doi so 5 la phuong phap (MODE_SMA=0, MODE_EMA=1) - lay `n` o doi so 3.
_HAM_MQL5 = {
    "irsi": ("rsi", 2), "iatr": ("atr", 2), "icci": ("cci", 2),
    "iadx": ("adx", 2), "imomentum": ("dong_luong", 2),
    "istdev": ("do_lech", 2), "ihighest": ("cao_nhat", 3),
    "ilowest": ("thap_nhat", 3), "ibands": ("bollinger", 2),
    "imacd": ("macd", 2), "istochastic": ("stochastic", 2),
    "iobv": ("obv", None), "ima": ("sma", 2), "iema": ("ema", 2),
}
#: `iMA(...)` voi MODE_EMA o doi so phuong phap -> ema thay vi sma.
_RX_HAM_MQL5 = re.compile(r"^(i[A-Za-z]+)[ \t]*\((.*)\)$", re.S)


def _tu_ham_mql5(tu: str) -> dict | None:
    """`iRSI(_Symbol,PERIOD_H1,14,PRICE_CLOSE)` -> {chi_bao: rsi, n: 14}."""
    m = _RX_HAM_MQL5.match(tu.strip())
    if not m:
        return None
    ten = m.group(1).lower()
    if ten not in _HAM_MQL5:
        return None
    cb, vt_n = _HAM_MQL5[ten]
    doi = [d.strip() for d in m.group(2).split(",")]
    if cb == "sma" and any("MODE_EMA" in d or "MODE_SMMA" in d for d in doi):
        cb = "ema"
    if vt_n is None:
        return {"chi_bao": cb}
    n = None
    if vt_n < len(doi):
        try:
            n = int(float(doi[vt_n]))
        except ValueError:
            n = None
    if n is None or n <= 0:
        return None                 # chu ky la BIEN -> khong chot duoc, bo
    ra = {"chi_bao": cb, "n": n}
    if cb in ("cao_nhat", "thap_nhat"):
        ra["cua"] = {"chi_bao": "gia",
                     "cot": "high" if cb == "cao_nhat" else "low"}
    return ra

#: Toan tu CUA SO: tinh tren mot toan hang khac, bat buoc co truong `cua`.
_CAN_CUA = {"cao_nhat", "thap_nhat", "tb", "do_lech", "zscore", "phan_vi",
            "doi", "doi_pct", "tre", "tuyet_doi"}
_CUA_MAC_DINH = {"cao_nhat": "high", "thap_nhat": "low"}

#: Chi bao co THANG DO BI CHAN (0-100, 0-1, gio, thang...) - so sanh voi mot
#: hang so la co nghia.
_CO_CHAN = {"rsi", "ibs", "phan_vi", "zscore", "gio", "ngay_trong_tuan",
            "ngay_trong_thang", "thang", "doi_pct"}

#: Chi bao o THANG DO GIA - so sanh voi mot hang so tran la vo nghia: `input(1.5)`
#: cua mot he so nhan bi doc thanh nguong gia. Do that tren Sonic R: sinh ra
#: `open < 2` va `ema34_high < 1.5`, ca hai kich hoat 100% so bar.
_THANG_GIA = {"gia", "ema", "sma", "cao_nhat", "thap_nhat",
              "cao_trong_gio", "thap_trong_gio", "tuyen_tinh", "atr", "do_lech",
              "bien_do", "than_nen", "tb", "khoi_luong"}

_TEN = r"[A-Za-z_][A-Za-z0-9_]*"
_SO = r"[-+]?\d+(?:\.\d+)?"

#: `ten = <loi goi chi bao>` - bat ca Pine (`ema(close,89)`, `ta.ema(...)`) lan
#: MQL (`iMA(...)`, `iRSI(...)`).
_GAN_CB = re.compile(
    rf"^[ \t]*({_TEN})[ \t]*=[ \t]*((?:ta\.)?{_TEN}[ \t]*\([^\n]*)", re.M)

#: So sanh hai ve. Chan `==` va `!=` (khong phai phep cua ngu phap) va chan `=>`.
_SS = re.compile(
    rf"({_TEN}(?:\[\d+\])?|{_SO})[ \t]*(>=|<=|>|<)[ \t]*({_TEN}(?:\[\d+\])?|{_SO})")

#: `crossover(a, b)` / `crossunder(a, b)` cua Pine, va ban `ta.` cua v5.
_CHEO = re.compile(rf"(?:ta\.)?(crossover|crossunder)[ \t]*\(([^,]+),([^)]+)\)")


#: Khai bao input CUA TAC GIA. Pine: `n = input(34, minval=2, maxval=200)`.
#: MQL5: `input int InpPeriod = 14; // mo ta`.
_INPUT_PINE = re.compile(
    rf"^[ \t]*({_TEN})[ \t]*=[ \t]*"
    rf"input(?:\.[a-z]+)?[ \t]*\(([^)\n]*)\)", re.M)
_INPUT_MQL = re.compile(
    rf"^[ \t]*(?:extern|input)[ \t]+[A-Za-z_]\w*[ \t]+({_TEN})"
    rf"[ \t]*=[ \t]*({_SO})[ \t]*;", re.M)
_MINMAX = re.compile(rf"(minval|maxval|step)[ \t]*=[ \t]*({_SO})")


def _chuan_hoa(vb: str) -> str:
    """Chuan hoa xuong dong ve LF va bo chu thich duoi dong.

    Vi sao can, va no la mot LOP loi chu khong phai mot cho: file Pine tai ve
    dung CRLF, nen moi bieu thuc chinh quy ket bang [ tab]*$ deu truot -
    `price = close<CR>` khong khop `(open|high|low|close)[ tab]*$`. Ca mot
    chien luoc Bollinger + RSI rot chi vi mot ky tu CR, va trieu chung nhin tu
    ngoai chi la "khong dich duoc crossover(source, BBlower)".

    Chu thich duoi dong cung phai bo truoc khi phan tich so hoc:
    `BBmult = 2 // input(2.0, ...)` co dau `//` ma bo tach hang tu se doc nham
    thanh phep chia.
    """
    vb = (vb or '').replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))
    return re.sub(r'[ \t]*//[^\n]*', '', vb)


def rut_input(vb: str) -> dict:
    """Ten bien -> {gia_tri, min, max} theo dung khai bao cua TAC GIA.

    Vi sao dang gia: chinh nguoi viet bot da noi bien nay chay trong khoang nao.
    Do la mot mien quet CO NGUON GOC, khac han mot luoi ta tu bia ra - va lay no
    khong phai chay mot dong ma nao cua ho.
    """
    vb = _chuan_hoa(vb)

    ra: dict[str, dict] = {}
    for m in _INPUT_PINE.finditer(vb):
        doi = m.group(2)
        so = re.search(rf"(?:defval[ \t]*=[ \t]*)?({_SO})", doi)
        if not so:
            continue
        d = {"gia_tri": float(so.group(1))}
        for mm in _MINMAX.finditer(doi):
            d[{"minval": "min", "maxval": "max",
               "step": "buoc"}[mm.group(1)]] = float(mm.group(2))
        ra[m.group(1)] = d
    for m in _INPUT_MQL.finditer(vb):
        ra.setdefault(m.group(1), {"gia_tri": float(m.group(2))})
    return ra


def _luoi_quanh(n: float, khai: dict | None) -> list[int]:
    """Ba diem quanh gia tri tac gia dung, chan trong mien tac gia khai.

    Ba chu khong nhieu hon: moi diem them la mot suat FDR. Muc dich khong phai
    do tim gia tri tot nhat - do la viec cua tang kham pha - ma la biet hinh
    dang quanh diem tac gia chon (cao nguyen hay cai gai).
    """
    khai = khai or {}
    lo = khai.get("min", 2.0)
    hi = khai.get("max", 1e9)
    ra = []
    for x in (n / 2.0, n, n * 2.0):
        v = int(round(max(lo, min(hi, x))))
        if v >= 2 and v not in ra:
            ra.append(v)
    return sorted(ra)


def _tach_tam_nguyen(bt: str) -> list[tuple[str, str]]:
    """`a ? b : c ? d : e` -> [(a,b), (c,d), ("", e)]. Tach o MUC NGOAI CUNG."""
    ra, con = [], bt.strip()
    while True:
        muc, vt = 0, -1
        for i, c in enumerate(con):
            if c in "([":
                muc += 1
            elif c in ")]":
                muc -= 1
            elif c == "?" and muc == 0:
                vt = i
                break
        if vt < 0:
            ra.append(("", con.strip()))
            return ra
        dk = con[:vt]
        # tim dau `:` NGANG CAP voi dau `?` nay
        muc, vt2 = 0, -1
        for i in range(vt + 1, len(con)):
            c = con[i]
            if c in "([":
                muc += 1
            elif c in ")]":
                muc -= 1
            elif c == ":" and muc == 0:
                vt2 = i
                break
        if vt2 < 0:
            ra.append((dk.strip(), con[vt + 1:].strip()))
            return ra
        ra.append((dk.strip(), con[vt + 1:vt2].strip()))
        con = con[vt2 + 1:]


def _bo_tu_tham_chieu(dk: str, ten: str) -> str:
    """Bo cac ve `ten[1] > 0` khoi dieu kien - chung la GUARD TRANG THAI.

    `crossunder(fast, slow) and direction[1] > 0 ? -1` nghia la "lat xuong khi co
    crossunder, va luc do dang len". `trang_thai_lat` da GIU trang thai san nen
    ve `direction[1] > 0` la thua; giu no lai thi khong dich duoc (mot toan hang
    tu tham chieu) va ca bien mat.
    """
    giu = [v for v in _tach_va(dk)
           if not re.search(rf"\b{re.escape(ten)}\s*\[", v)]
    return " and ".join(giu)


def _trang_thai_tu_tam_nguyen(ten: str, bt: str, vi_tri: int, bang: list,
                              bang_bt: list) -> dict | None:
    """Bien TU THAM CHIEU viet bang tam nguyen long -> toan hang `trang_thai_lat`.

    Dang that trong ma (do 01/09 tren kho Pine, 12 bien co dang nay):

        direction = na(direction[1]) ? 1
                  : crossunder(fast, slow) and direction[1] > 0 ? -1
                  : crossover(fast, slow) and direction[1] < 0 ? 1
                  : direction[1]

    Day chinh la `trang_thai_lat`: nhanh cho ra +1 la dieu kien LEN, nhanh cho ra
    -1 la dieu kien XUONG, nhanh `x[1]` la "giu nguyen". Bo doc chi can nhan ra
    hinh dang do - toan tu da co tu truoc.
    """
    if not re.search(rf"\b{re.escape(ten)}\s*\[", bt):
        return None                       # khong tu tham chieu -> khong co nho
    len_dk, xuong_dk = None, None
    for dk, gt in _tach_tam_nguyen(bt):
        g = gt.strip()
        if not dk or f"{ten}[" in g:
            continue                      # nhanh mac dinh / giu nguyen
        if re.search(rf"\bna\s*\(\s*{re.escape(ten)}\s*\[", dk):
            continue                      # nhanh khoi tao
        sach = _bo_tu_tham_chieu(dk, ten)
        if not sach:
            continue
        if re.fullmatch(r"[+]?1(?:\.0+)?", g) and len_dk is None:
            len_dk = sach
        elif re.fullmatch(r"-1(?:\.0+)?", g) and xuong_dk is None:
            xuong_dk = sach
    if not len_dk or not xuong_dk:
        return None
    a, ha = _no_dieu_kien(len_dk, vi_tri, bang, bang_bt)
    b, hb = _no_dieu_kien(xuong_dk, vi_tri, bang, bang_bt)
    if ha or hb or len(a) != 1 or len(b) != 1:
        return None                       # dich duoc CA HAI thi moi nhan
    return {"chi_bao": "trang_thai_lat", "len": a[0], "xuong": b[0]}


def _chon_nhanh_cau_hinh(bt: str, vi_tri: int, bang_bt: list) -> str | None:
    """`x = co_bat ? A : B` voi `co_bat = input(true)` -> tra ve `A`.

    Day KHONG phai tin hieu ma la mot cong tac cau hinh cua tac gia: 59/71 bieu
    thuc tam nguyen trong kho Pine thuoc dang nay (`use_longer_average`,
    `no_repainting`, `show_highlight`). Giu nguyen ca bieu thuc thi khong dich
    duoc; chon dung nhanh ung voi gia tri MAC DINH cua ho thi doc tiep duoc, va
    do dung la cau hinh ho phat hanh.
    """
    nhanh = _tach_tam_nguyen(bt)
    if len(nhanh) != 2 or not nhanh[0][0]:
        return None
    dk = nhanh[0][0].strip()
    if not re.fullmatch(_TEN, dk):
        return None
    gt = None
    for pos, ten, bt2 in bang_bt:
        if pos >= vi_tri:
            break
        if ten == dk:
            gt = bt2
    if gt is None:
        return None
    m = re.match(r"input(?:\.bool)?\s*\(\s*(true|false)\b", gt.strip(), re.I)
    if not m:
        return None
    return nhanh[0][1] if m.group(1).lower() == "true" else nhanh[1][1]


def _bang_ky_hieu(vb: str) -> list[tuple[int, str, dict]]:
    """(vi tri, ten bien, toan hang) cho moi bien duoc gan bang mot chi bao.

    Theo VI TRI chu khong phai tu dien phang, cung ly do nhu `_bang_bien` cua
    `thu_hoi_thanh_phan`: mot file tai ve thuong ghep nhieu script, va cung mot
    ten bien mang y nghia khac nhau o moi ban.
    """
    bang_so = TP._bang_bien(vb)
    ra = []
    for m in _GAN_CB.finditer(vb):
        ten, biu = m.group(1), m.group(2)
        # Rut dung mot loi goi chi bao tu ve phai, dung chinh bo rut da co.
        con = TP.rut_pine(biu[:400]) or TP.rut_mql(biu[:400])
        if not con:
            continue
        t = con[0]
        if not t.get("tham_so"):
            # Chu ky co the la bien khai o cho khac trong file.
            ds = TP._tach_doi_so(TP._khoi_ngoac(biu, biu.index("(")))
            t = dict(t, tham_so=TP._so_dau(ds, 1, m.start(), bang_so))
        ra.append((m.start(), ten, t))
    # HAI DANG BIEN RAT PHO BIEN ma ban dau bo doc bo qua - va bo qua chung thi
    # moi dieu kien dang `crossover(vrsi, RSIoverSold)` deu rot:
    #   1. BIEN SO   : `RSIoverSold = input(30)`  -> mot hang so
    #   2. BI DANH GIA: `source = close`          -> chinh cot gia do
    da = {t[1] for t in ra}
    for pos, ten, v in bang_so:
        if ten not in da:
            ra.append((pos, ten, {"hang": float(v), "_thang": 1}))
    for m in re.finditer(rf"^[ 	]*({_TEN})[ 	]*=[ 	]*(open|high|low|close)[ 	]*$",
                         vb, re.M):
        if m.group(1) not in da:
            ra.append((m.start(), m.group(1),
                       {"chi_bao": "gia", "cot": m.group(2), "_thang": 1}))
    ra.sort(key=lambda x: x[0])
    return ra


def _tach_cong_tru(bt: str) -> list[tuple[float, str]]:
    """Tach mot bieu thuc theo `+`/`-` o MUC NGOAI CUNG. Tra (dau, hang tu).

    Bo qua dau o vi tri MO DAU (do la dau am cua so hang dau) va dau ngay sau
    mot toan tu khac (`a * -2`), de khong cat nham thanh hai hang tu.
    """
    ra, sau, muc, dau = [], 0, 0, 1.0
    for i, c in enumerate(bt):
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        elif muc == 0 and c in "+-" and i > 0:
            truoc = bt[:i].rstrip()
            if truoc and truoc[-1] not in "+-*/(,<>=":
                ra.append((dau, bt[sau:i]))
                dau = 1.0 if c == "+" else -1.0
                sau = i + 1
    ra.append((dau, bt[sau:]))
    return [(d, t.strip()) for d, t in ra if t.strip()]


def _hang_tu(bt: str, vi_tri: int, bang: list, bang_bt: list,
             sau: int) -> tuple[float, dict] | None:
    """Mot hang tu -> (he so, toan hang). Chi chap nhan dang TUYEN TINH.

    `2 * dev`, `dev * 2`, `dev / 2`, `dev` deu duoc; `a * b` voi ca hai la chuoi
    gia tri thi KHONG - do la phep nhan hai chuoi, khong con tuyen tinh va khong
    dien dat duoc bang `tuyen_tinh`.

    He so co the la mot BIEN (`mult = input(2.0)`), khong chi mot so tho. Bang
    ky hieu da chua san bien so duoi dang `{"hang": v}` nen chi can hoi no.
    """
    he_so, toan = 1.0, None
    phan = re.split(r"([*/])", bt)
    dau_chia = False
    for k, p in enumerate(phan):
        p = p.strip()
        if p in ("*", "/"):
            dau_chia = (p == "/")
            continue
        p = _boc_ngoac(p)
        if not p:
            continue
        t = _toan_hang(p, vi_tri, bang, bang_bt, sau + 1)
        if t is None and re.match(rf"^(?:ta[.])?{_TEN}[ 	]*[(]", p):
            # LOI GOI VIET THANG trong bieu thuc: `mult * stdev(source, length)`.
            # Khong xu ly thi moi ban Bollinger deu rot, vi `dev` luon duoc viet
            # dang nay chu khong gan qua mot bien chi bao rieng.
            con = TP.rut_pine(p) or TP.rut_mql(p)
            if con:
                c0 = con[0]
                if not c0.get("tham_so"):
                    # Chu ky la mot BIEN (`stdev(source, length)` voi
                    # `length = input(20)`). Bo rut chi nhin trong dung chuoi loi
                    # goi nen khong thay; giai bang BANG KY HIEU - noi da co san
                    # bien so duoi dang {"hang": v}.
                    ds2 = TP._tach_doi_so(TP._khoi_ngoac(p, p.index("(")))
                    for a in ds2:
                        ta = _toan_hang(a.strip(), vi_tri, bang, bang_bt, sau + 1)
                        if ta and "hang" in ta and float(ta["hang"]) >= 1:
                            c0 = dict(c0, tham_so=[float(ta["hang"])])
                            break
                t = _tu_thanh_phan(c0)
        if t is None and _CHE_DO_MQL and len(_tach_cong_tru(p)) > 1:
            # `(highrange-lowrange)/2`: hang tu la mot bieu thuc tuyen tinh long
            t = _tuyen_tinh(p, vi_tri, bang, bang_bt, sau + 1)
        if t is None:
            return None
        if "hang" in t:                       # la mot HE SO, khong phai chuoi
            v = float(t["hang"])
            if dau_chia and v == 0:
                return None
            he_so = he_so / v if dau_chia else he_so * v
            continue
        if toan is not None:
            return None                       # nhan hai chuoi -> khong tuyen tinh
        toan = t
    if toan is None:
        return None
    return he_so, toan


def _tuyen_tinh(bt: str, vi_tri: int, bang: list, bang_bt: list,
                sau: int) -> dict | None:
    """Bieu thuc so hoc -> toan hang `tuyen_tinh` cua ngu phap.

    Vi sao can: chien luoc Pine that gan nhu luon so gia voi mot MUC DUOC TINH
    RA - `BBlower = basis - mult * dev`, kenh Keltner, pivot. Khong dich duoc
    dang nay thi 17/18 chien luoc trong kho deu rot o buoc dich, va do dung la
    cho bo doc dung lai truoc khi co ham nay.
    """
    hang = _tach_cong_tru(bt)
    # Mot hang tu VAN hop le neu no co he so (`mult * stdev(...)`) - do la dang
    # `dev` cua moi ban Bollinger. Chi bo khi ca bieu thuc la mot dinh danh tran,
    # vi luc do duong khac da lo roi va vao day se de quy vo tan.
    if len(hang) == 1 and re.fullmatch(_TEN, bt.strip()):
        return None
    ds, hs, cong = [], [], 0.0
    for dau, ht in hang:
        p = _boc_ngoac(ht)
        if re.fullmatch(_SO, p):
            cong += dau * float(p)
            continue
        r = _hang_tu(p, vi_tri, bang, bang_bt, sau)
        if r is None:
            return None                 # mot hang tu khong dich duoc -> bo CA
        h, t = r
        if _CHE_DO_MQL and t.get("chi_bao") == "tuyen_tinh":
            # `(a+b+c)/3` -> PHANG ra 3 hang tu he so 1/3, khong long tuyen_tinh
            # trong tuyen_tinh. Cung nghia. Chi o che do MQL5: Pine giu dang
            # long (`basis - dev` voi `dev = mult*stdev`) de `mult` con la mot
            # tham so rieng cua tac gia.
            ds += t["toan_hang"]
            hs += [dau * h * float(x) for x in t["he_so"]]
            cong += dau * h * float(t.get("cong_them", 0.0))
            continue
        ds.append(t)
        hs.append(dau * h)
    if not ds:
        return None
    d = {"chi_bao": "tuyen_tinh", "toan_hang": ds, "he_so": hs}
    if cong:
        d["cong_them"] = cong
    return d


def _toan_hang(tu: str, vi_tri: int, bang: list,
               bang_bt: list | None = None, sau: int = 0) -> dict | None:
    """Mot ve cua phep so sanh -> toan hang ngu phap, hoac None neu khong dich duoc."""
    tu = (tu or "").strip()
    # `x[k]` la NHIN LUI k bar. Ban dau ham nay CAT BO hau to do, va do la mot
    # loi lam hong nghia: `close > highest(high,34)` (khong co do tre) khong bao
    # gio dung, vi `highest` gom ca nen hien tai - cong bao "kich hoat 0,000%".
    # Ma pha vo that luon viet `highest(high,34)[1]`. Cung ho loi voi quy tac
    # `Open[i+1]` cua du an: mat do tre la doi hoan toan y nghia.
    tre = 0
    m_tre = re.search(r"\[(\d+)\]$", tu)
    if m_tre:
        tre = int(m_tre.group(1))
        tu = tu[:m_tre.start()]
    if not tu:
        return None
    goc = _toan_hang_goc(tu, vi_tri, bang, bang_bt, sau)
    if goc is None or tre <= 0:
        return goc
    if "hang" in goc:
        return goc                             # hang so tre van la chinh no
    return {"chi_bao": "tre", "cua": goc, "n": tre}


def _toan_hang_goc(tu: str, vi_tri: int, bang: list,
                   bang_bt: list | None = None, sau: int = 0) -> dict | None:
    if re.fullmatch(_SO, tu):
        return {"hang": float(tu)}
    k = tu.lower()
    if tu == _GIA0:
        return {"chi_bao": "gia", "cot": "close", "_bar0": 1}
    if k in _GIA:
        return {"chi_bao": "gia", "cot": _GIA[k]}
    # ham chi bao MQL5 viet thang trong dieu kien
    hm = _tu_ham_mql5(tu)
    if hm is not None:
        return hm
    # bien tro toi mot chi bao: lay lan gan GAN NHAT TRUOC vi tri dung
    gt = None
    for pos, ten, t in bang:
        if pos >= vi_tri:
            break
        if ten == tu:
            gt = t
    if gt is None:
        # Bien co the duoc gan bang mot BIEU THUC SO HOC (`BBlower = basis -
        # mult * dev`). Truoc khi bo cuoc, thu no bieu thuc do ra toan hang
        # `tuyen_tinh`. Gioi han do sau de mot file co vong tham chieu khong
        # lam treo bo doc.
        if bang_bt and sau < 5:
            dn = None
            for pos, ten, bt2 in bang_bt:
                if pos >= vi_tri:
                    break
                if ten == tu:
                    dn = (pos, bt2)
            if dn is not None:
                # THU TU QUAN TRONG: trang thai co nho truoc, vi mot bieu thuc
                # tam nguyen tu tham chieu cung "trong nhu" mot to hop tuyen
                # tinh neu chi nhin dau `+`/`-`.
                t = _trang_thai_tu_tam_nguyen(tu, dn[1], dn[0], bang, bang_bt)
                if t is not None:
                    return t
                # CONG TAC CAU HINH: `x = co_bat ? A : B` voi `co_bat =
                # input(true)`. Do la mot lua chon cua tac gia, khong phai tin
                # hieu - chon dung nhanh ho de mac dinh roi doc tiep.
                nhanh = _chon_nhanh_cau_hinh(dn[1], dn[0], bang_bt)
                if nhanh is not None and nhanh != dn[1]:
                    t = _toan_hang(nhanh, dn[0], bang, bang_bt, sau + 1)
                    if t is not None:
                        return t
                if dn[1].strip() == _GIA0:
                    return {"chi_bao": "gia", "cot": "close", "_bar0": 1}
                if dn[1].strip().lower() in _GIA:
                    # bi danh cot gia tran: `double c1 = iClose(_Symbol,_Period,1);`
                    # -> `c1 = close` sau quy uoc chi so bar MQL5 (bar 1 = bar i)
                    return {"chi_bao": "gia", "cot": _GIA[dn[1].strip().lower()]}
                t = _tuyen_tinh(dn[1], dn[0], bang, bang_bt, sau + 1)
                if t is not None:
                    return t
        return None
    return _tu_thanh_phan(gt)


def _tu_thanh_phan(gt: dict) -> dict | None:
    """Mot thanh phan cua `thu_hoi_thanh_phan` -> toan hang ngu phap."""
    if "hang" in gt or gt.get("_thang"):
        return {k: v for k, v in gt.items() if not k.startswith("_")}
    ok, _ = TP.dien_dat_duoc(gt)
    if not ok:
        return None
    d = {"chi_bao": gt["chi_bao"]}
    if gt.get("tham_so"):
        d["n"] = int(gt["tham_so"][0])
    elif gt["chi_bao"] not in ("ibs", "bien_do", "than_nen", "khoi_luong"):
        return None                            # thieu chu ky -> khong dung duoc
    if gt.get("cot") and gt["chi_bao"] in ("ema", "sma", "gia"):
        d["cot"] = gt["cot"]
    if gt["chi_bao"] in _CAN_CUA:
        # `cao_nhat`/`thap_nhat`/`tb`/... la toan tu CUA SO: chung tinh tren mot
        # toan hang khac chu khong tu co chuoi gia tri. Thieu `cua` thi ngu phap
        # nem `KeyError: chi bao 'cao_nhat' khong biet, va khong co truong 'cua'`
        # - da sap that khi doc Donchian cua Sonic R.
        d["cua"] = {"chi_bao": "gia",
                    "cot": gt.get("cot") or _CUA_MAC_DINH.get(gt["chi_bao"], "close")}
    return d


def _ho_cua(dk: dict) -> str:
    """Ho cua mot dieu kien, NHIN XUYEN qua cac toan tu boc ngoai.

    `tre` (va cac toan tu cua so khac) chi la lop boc: ho thuc su nam o toan
    hang ben trong. Khong boc thi `close > cao_nhat(55) tre 1` - dieu kien pha
    vo dien hinh - bi xep ho `khac` roi bi loai, tuc bo doc vut dung cai no vua
    cong suc giu lai do tre cho.
    """
    for ben in ("trai", "phai"):
        for cb in _cac_chi_bao(dk.get(ben) or {}):
            if cb in _HO:
                return _HO[cb]
    return "khac"


def _cac_chi_bao(t: dict, sau: int = 0) -> list[str]:
    """Moi ten chi bao xuat hien trong mot toan hang, ke ca long ben trong.

    Phai nhin XUYEN QUA `tuyen_tinh` va `cua`: mot dai Bollinger duoc viet
    `tuyen_tinh([tb, do_lech])`, va neu chi doc `chi_bao` o lop ngoai thi ho ra
    `khac` - ma `khac` khong khai duoc pham vi nen khong vao duoc thu vien. Tuc
    dung cai co che ta vua cong suc dich ra lai bi bo o cua cuoi.
    """
    if not isinstance(t, dict) or sau > 6:
        return []
    ra = []
    cb = t.get("chi_bao")
    if cb and cb not in ("tuyen_tinh", "tre", "tuyet_doi"):
        ra.append(cb)
    for x in (t.get("toan_hang") or []):
        ra += _cac_chi_bao(x, sau + 1)
    if isinstance(t.get("cua"), dict):
        ra += _cac_chi_bao(t["cua"], sau + 1)
    # Toan tu CO NHO giu chi bao trong hai DIEU KIEN con (`len`/`xuong`/`khi`),
    # khong phai trong `toan_hang` hay `cua`. Khong nhin vao day thi mot co che
    # supertrend ra ho `khac` - ma `khac` khong khai duoc pham vi nen bi bo o cua
    # cuoi. Cung ho loi da sap voi `tuyen_tinh`: dich ra duoc roi lai vut di.
    for khoa in ("len", "xuong", "khi"):
        d = t.get(khoa)
        if isinstance(d, dict):
            for ben in ("trai", "phai"):
                if isinstance(d.get(ben), dict):
                    ra += _cac_chi_bao(d[ben], sau + 1)
    return ra


def _ten_toan_hang(t: dict) -> str:
    if t.get("chi_bao") == "tre":
        return _ten_toan_hang(t.get("cua") or {}) + f"_tre{int(t.get('n', 1))}"
    if "hang" in t:
        s = f"{t['hang']:g}".replace("-", "am").replace(".", "_")
        return s
    cb = t.get("chi_bao", "x")
    if cb == "gia":
        return t.get("cot", "close")
    p = cb + (str(int(t["n"])) if t.get("n") else "")
    return p + (("_" + t["cot"]) if t.get("cot") else "")


_TEN_PHEP = {">": "tren", ">=": "tren", "<": "duoi", "<=": "duoi",
             "cheo_len": "cheo_len", "cheo_xuong": "cheo_xuong"}


def _hop_thang_do(trai: dict, phai: dict) -> bool:
    """Hai ve co cung thang do khong.

    Hai hang so: vo nghia. Mot hang so doi voi mot chi bao o THANG DO GIA: cung
    vo nghia, va day la nguon rac chinh - `input(1.5)` cua mot he so nhan bi doc
    thanh nguong gia. Chi bao co thang do bi chan (rsi 0-100, gio 0-23...) thi
    so voi hang so la dung.
    """
    ch = [t for t in (trai, phai) if "hang" in t]
    if len(ch) == 2:
        return False
    if not ch:
        return True
    kia = phai if "hang" in trai else trai
    while kia.get("chi_bao") == "tre":
        kia = kia.get("cua") or {}
    return kia.get("chi_bao") not in _THANG_GIA


def _dieu_kien(vb: str, bang: list) -> list[dict]:
    """Moi so sanh dich duoc = MOT dieu kien vao. Gop trung."""
    ra, da = [], set()
    for m in _SS.finditer(vb):
        trai = _toan_hang(m.group(1), m.start(), bang)
        phai = _toan_hang(m.group(3), m.start(), bang)
        if not trai or not phai:
            continue
        if not _hop_thang_do(trai, phai):
            continue
        d = {"trai": trai, "phep": _PHEP[m.group(2)], "phai": phai}
        khoa = repr(sorted(d.items(), key=str))
        if khoa in da:
            continue
        da.add(khoa)
        ra.append(dict(d, _trich=m.group(0)[:80]))
    for m in _CHEO.finditer(vb):
        trai = _toan_hang(m.group(2), m.start(), bang)
        phai = _toan_hang(m.group(3), m.start(), bang)
        if not trai or not phai:
            continue
        phep = "cheo_len" if m.group(1) == "crossover" else "cheo_xuong"
        d = {"trai": trai, "phep": phep, "phai": phai}
        khoa = repr(sorted(d.items(), key=str))
        if khoa in da:
            continue
        da.add(khoa)
        ra.append(dict(d, _trich=m.group(0)[:80]))
    return ra


def _luoi_tu_dieu_kien(dk: dict, khai: dict) -> dict:
    """Chu ky trong dieu kien -> luoi quet, chan theo minval/maxval cua tac gia."""
    ra = {}
    for ben in ("trai", "phai"):
        t = dk.get(ben) or {}
        while isinstance(t, dict) and t.get("chi_bao") in ("tre", "tuyet_doi"):
            t = t.get("cua") or {}
        n = (t or {}).get("n")
        if not n:
            continue
        # Khai bao nao co gia tri dung bang `n` thi mien cua no ap cho `n`.
        k = next((v for v in khai.values() if v.get("gia_tri") == float(n)), None)
        # Khoa theo VE, khong theo ten chi bao: mot dieu kien nhu
        # `ema34_low < ema89_close` co hai ve CUNG la `ema`, va khoa theo ten thi
        # chu ky 34 bi 89 ghi de - mat dung mot nua dieu kien.
        ra[f"{ben}_{t.get('chi_bao')}"] = _luoi_quanh(float(n), k)
    return ra


#: `strategy.entry(..., strategy.long)` / `... , true)` / `..., when = <dk>`.
_VAO_LENH = re.compile(
    r"strategy\.(?P<pine>entry|order)[ \t]*\((?P<doi_p>[^\n]*)"
    r"|(?P<obj>\w+)\.(?P<mql>Buy|Sell)[ \t]*\((?P<doi_m>[^\n]*)"
    r"|(?P<ham>OrderSend|PositionOpen)[ \t]*\((?P<doi_o>[^\n]*)", re.M)
#: Guard chi noi DANG DI NHANH NAO, khong noi vi sao vao lenh. Do 05/09:
#: `type == ORDER_TYPE_BUY` (7 file) · `type==POSITION_TYPE_BUY` (6) ·
#: `orderType == ORDER_TYPE_BUY` (4) · `direction>0` (3) · `isBuy` (3).
_LA_PHAN_NHANH = re.compile(
    r"ORDER_TYPE_(BUY|SELL)|POSITION_TYPE_(BUY|SELL)|\bis[_]?Buy\b|\bis[_]?Sell\b"
    r"|\bdirection\s*[<>=]|\bdir\s*[<>=]|\btype\s*==|\bcmd\s*==",
    re.I)

#: Khai bao ham kieu C: `void Ten(...)` / `bool Ten(...)` / `void Ten(...) {`.
_KHAI_HAM = re.compile(
    r"^[ \t]*(?:static[ \t]+)?(?:void|bool|int|double|long|string|datetime)"
    r"[ \t]+(\w+)[ \t]*\(", re.M)


def _ham_bao(vb: str, vi_tri: int) -> str | None:
    """Ten ham chua vi tri `vi_tri`. Lay khai bao ham GAN NHAT phia tren."""
    ten = None
    for m in _KHAI_HAM.finditer(vb):
        if m.start() > vi_tri:
            break
        ten = m.group(1)
    return ten


def _cho_goi(vb: str, ten_ham: str, tru_vi_tri: int) -> list[int]:
    """Vi tri cac cho GOI `ten_ham(` - tru chinh cho khai bao."""
    ra = []
    for m in re.finditer(r"\b" + re.escape(ten_ham) + r"[ \t]*\(", vb):
        if abs(m.start() - tru_vi_tri) < 4:
            continue
        dong = vb[max(0, m.start() - 200):m.start()]
        if re.search(r"(?:void|bool|int|double|long|string|datetime)[ \t]+$", dong):
            continue                      # do la khai bao, khong phai loi goi
        ra.append(m.start())
    return ra


#: `if` la KIEM LOI cua chinh lenh vao, khong phai dieu kien vao.
_LA_KIEM_LOI = re.compile(
    r"OrderSend|PositionOpen|\.(Buy|Sell)[ \t]*\(|GetLastError|ResultRetcode"
    r"|IsStopped|!\s*\w+\.(Buy|Sell)")

#: Gan mot bien BOOL: `ten = <bieu thuc co so sanh hoac ket noi>`.
_GAN_BOOL = re.compile(
    rf"^[ \t]*(?:bool|int|double|long|datetime)?[ \t]*({_TEN})[ \t]*=[ \t]*([^;\n]+)",
    re.M)


def _bang_bool(vb: str) -> list[tuple[int, str, str]]:
    """(vi tri, ten, bieu thuc) cho moi bien duoc gan mot bieu thuc."""
    return [(m.start(), m.group(1), m.group(2).strip())
            for m in _GAN_BOOL.finditer(vb)]


def _tach_va(bt: str) -> list[str]:
    """Tach mot bieu thuc theo `and` o MUC NGOAI CUNG."""
    ra, sau, muc = [], 0, 0
    i = 0
    while i < len(bt):
        c = bt[i]
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        elif muc == 0 and bt.startswith("and", i) and \
                (i == 0 or not bt[i - 1].isalnum()) and \
                (i + 3 >= len(bt) or not bt[i + 3].isalnum()):
            ra.append(bt[sau:i])
            sau = i + 3
            i += 2
        i += 1
    ra.append(bt[sau:])
    return [_boc_ngoac(x.strip()) for x in ra if x.strip()]


def _boc_ngoac(s: str) -> str:
    """Bo cap ngoac BAO NGOAI, va chi khi no that su bao ngoai.

    `.strip("()")` mu lam hong lay: no cat dau `)` cuoi cua
    `crossover(source, BBlower)` thanh `crossover(source, BBlower`, va sau do
    khong regex nao khop duoc nua. Do that: moi dieu kien crossover trong kho
    Pine deu rot o day.
    """
    s = s.strip()
    while len(s) > 1 and s[0] == "(" and s[-1] == ")":
        muc = 0
        for i, c in enumerate(s):
            if c == "(":
                muc += 1
            elif c == ")":
                muc -= 1
                if muc == 0 and i < len(s) - 1:
                    return s          # ngoac dau dong lai giua chung -> khong bao ngoai
        s = s[1:-1].strip()
    return s


def _no_dieu_kien(bt: str, vi_tri: int, bang_cb: list, bang_bl: list,
                  sau: int = 0) -> tuple[list[dict], list[str]]:
    """Bieu thuc guard -> danh sach dieu kien DSL. Tra (dieu kien, phan khong dich duoc).

    De quy: mot ve co the la mot BIEN tro toi mot bieu thuc khac
    (`trade_entry = fractal_trend and fractal_breakout`), nen phai no ra toi khi
    cham day la mot phep so sanh.
    """
    if sau > 5:
        return [], [bt[:60]]
    dk, ho = [], []
    for ve in _tach_va(bt):
        if " or " in f" {ve} ":
            ho.append(ve[:60])          # `or` khong dien dat duoc bang danh sach VA
            continue
        if _CHE_DO_MQL:
            if re.search(r"[<>]|==|!=", ve):
                d = _so_sanh_tong_quat(ve, vi_tri, bang_cb, bang_bl)
                if d is not None:
                    dk.append(d)
                else:
                    ho.append(ve[:60])
                continue
            mn = re.fullmatch(rf"!\s*({_TEN})", ve)
            if mn:
                pd_ = None
                for pos, ten, bt2 in bang_bl:
                    if pos >= vi_tri:
                        break
                    if ten == mn.group(1):
                        pd_ = (pos, bt2)
                ds = _phu_dinh(pd_[1], pd_[0], bang_cb, bang_bl) if pd_ else None
                if ds:
                    dk += ds
                else:
                    ho.append(ve[:60])
                continue
        m = _SS.fullmatch(ve) or _SS.search(ve)
        if m and m.group(0).strip() == ve:
            trai = _toan_hang(m.group(1), vi_tri, bang_cb, bang_bl)
            phai = _toan_hang(m.group(3), vi_tri, bang_cb, bang_bl)
            if trai and phai and _hop_thang_do(trai, phai):
                dk.append({"trai": trai, "phep": _PHEP[m.group(2)], "phai": phai})
            else:
                ho.append(ve[:60])
            continue
        mc = _CHEO.fullmatch(ve) or _CHEO.search(ve)
        if mc and mc.group(0).strip() == ve:
            trai = _toan_hang(mc.group(2), vi_tri, bang_cb, bang_bl)
            phai = _toan_hang(mc.group(3), vi_tri, bang_cb, bang_bl)
            if trai and phai:
                dk.append({"trai": trai,
                           "phep": "cheo_len" if mc.group(1) == "crossover"
                                   else "cheo_xuong", "phai": phai})
            else:
                ho.append(ve[:60])
            continue
        # mot BIEN -> tim dinh nghia gan nhat TRUOC vi tri dung
        if re.fullmatch(_TEN, ve):
            dn = None
            for pos, ten, bt2 in bang_bl:
                if pos >= vi_tri:
                    break
                if ten == ve:
                    dn = (pos, bt2)
            if dn is not None:
                d2, h2 = _no_dieu_kien(dn[1], dn[0], bang_cb, bang_bl, sau + 1)
                dk += d2
                ho += h2
                continue
        ho.append(ve[:60])
    return dk, ho



# =====================================================================
# LOP DOC MQL5 (them 10/10/2026)
#
# Vi sao tach rieng: do bang `mau_thu/do_moc.py` thay bo mau 10 file .mq5 ra
# 0 co che, va ly do KHONG nam o ngu phap ma o cach doc MQL5:
#   1. `&&`/`||` khong duoc hieu (chi biet `and`/`or` cua Pine).
#   2. Thanh nen viet qua mang: `current[0].close` sau `CopyRates(...,0,1,current)`,
#      `MaValues[0]` sau `CopyBuffer(MaHandle,0,0,10,MaValues)` - ma mang KHONG
#      dao chieu (khong ArraySetAsSeries) thi phan tu 0 la bar CU NHAT.
#   3. Bien phien: `highs[ArrayMaximum(highs)]` sau CopyHigh theo khung gio.
#   4. Guard tim bang "dong `if` gan nhat phia tren" - sai voi khoi `{}`: no
#      vo phai `if(downbreakout){...}` DA DONG truoc lenh vao.
#   5. Bo loc "thoat som" (`if(dt.hour<9||dt.hour>17) return;`) bi bo qua, nen
#      co che rut ra LONG hon ban goc.
#
# NGUYEN TAC GIU NGUYEN: mot ve khong dich duoc thi BO CA co che. Chi nhung
# dieu kien QUAN TRI LENH (mot lenh/ngay, da co vi the, sao chep du lieu loi,
# gia tri <= 0) duoc bo qua - va duoc ghi ro o `bo_qua_quan_tri` - vi ngu phap
# mo ta TIN HIEU, khong mo ta quan ly vi the. Dieu kien phu thuoc GIA VAO LENH
# (hedge/luoi theo `Tradesinfo.*`) va ham tu viet trong file include khong co
# ma thi khong dich, giu o `chua_dien_dat_duoc`.
# =====================================================================

_CHE_DO_MQL = False

_RX_LA_MQL = re.compile(r"\bOn(?:Tick|Init|Deinit|Start)[ \t]*\(|#property\b"
                        r"|#include[ \t]*<Trade")

_COT_MANG = {"high": "high", "low": "low", "close": "close", "open": "open"}
_HAM_CB_MOT_BUFFER = {"ima", "irsi", "iatr", "icci", "imomentum", "istddev",
                      "istdev"}


def _la_mql(vb: str) -> bool:
    return bool(_RX_LA_MQL.search(vb or ""))


def _dong_ngoac(s: str, i: int) -> int:
    """Vi tri `)` dong cap voi `(` tai `i`; -1 neu khong co."""
    muc = 0
    for k in range(i, len(s)):
        if s[k] == "(":
            muc += 1
        elif s[k] == ")":
            muc -= 1
            if muc == 0:
                return k
    return -1


def _hang_mql(vb: str) -> dict:
    """Ten -> hang so: input cua tac gia va gan don `int x=Y;` / `x=5;`."""
    ra = {k: v["gia_tri"] for k, v in rut_input(vb).items()}
    for _ in range(3):
        for m in re.finditer(r"(?:\b(?:int|double|long)[ \t]+)?\b([A-Za-z_]\w*)"
                             r"[ \t]*=[ \t]*([A-Za-z_]\w*|[-+]?\d+(?:\.\d+)?)[ \t]*;",
                             vb):
            ten, v = m.group(1), m.group(2)
            if re.fullmatch(_SO, v):
                ra.setdefault(ten, float(v))
            elif v in ra:
                ra.setdefault(ten, ra[v])
    return ra


_RX_INPUT_HANG = re.compile(
    r"^[ \t]*input[ \t]+(?:bool|int|long|double|uint|ulong)[ \t]+"
    r"([A-Za-z_]\w*)[ \t]*=[ \t]*(true|false|[-+]?\d+(?:\.\d+)?)[ \t]*;", re.M)
_RX_KHAI_HAM_DU = re.compile(
    r"^[ \t]*(?:static[ \t]+)?(?:void|bool|int|double|long|string|datetime)"
    r"[ \t]+(\w+)[ \t]*\(([^()]*)\)\s*\{", re.M)


def _gia_tri_hang(x: str) -> float | None:
    x = x.strip()
    if x in ("true", "false"):
        return 1.0 if x == "true" else 0.0
    return float(x) if re.fullmatch(_SO, x) else None


def _danh_gia_hang(bt: str, hang: dict) -> bool | None:
    """Mot ve chi gom HANG cau hinh/so -> True/False; con bien that -> None."""
    ve = _boc_ngoac(bt)
    neg = False
    while ve.startswith("!") and not ve.startswith("!="):
        neg, ve = not neg, _boc_ngoac(ve[1:])
    m = re.fullmatch(r"([\w.]+)[ \t]*(==|!=|<=|>=|<|>)[ \t]*([\w.+-]+)", ve)
    if m:
        a = hang.get(m.group(1), _gia_tri_hang(m.group(1)))
        b = hang.get(m.group(3), _gia_tri_hang(m.group(3)))
        if a is None or b is None:
            return None
        kq = {"==": a == b, "!=": a != b, "<=": a <= b, ">=": a >= b,
              "<": a < b, ">": a > b}[m.group(2)]
    else:
        v = hang.get(ve, _gia_tri_hang(ve)) if re.fullmatch(r"[\w.]+", ve) else None
        if v is None:
            return None
        kq = v != 0
    return (not kq) if neg else kq


def _gap_hang_cau_hinh(vb: str) -> str:
    """GAP cac `if` chi phu thuoc CAU HINH (them 10/10/2026). Khong doi nghia.

    `if(ReverseEntry) up=!up;` voi `input bool ReverseEntry=false` khong bao
    gio chay o cau hinh cua tac gia; `if(startmanual!=0){...}` trong
    `checkForOpen(int startmanual=0)` chi chay khi NGUOI bam phim (goi tu
    `OnChartEvent`). De nguyen thi bang bien bool lay phep gan CUOI CUNG theo
    van ban - ma do la phep gan nam trong nhanh khong bao gio chay (`up=true`)
    -> dich sai. O day:
      - ve sai chac chan -> bo ca `if` (va than); co `else` thi giu than else;
      - ve dung chac chan -> bo `if(...)`, giu than;
      - dieu kien `and` lan bien that -> bo cac ve hang dung (`StartAtFullHourOnly
        and dt.min!=0 and startmanual==0` -> `dt.min!=0`).
    Chi `input` (MQL5: hang chi doc) - KHONG `extern` (MQL4 gan lai duoc).
    Tham so mac dinh cua ham chi duoc coi la hang khi MOI loi goi CO doi so
    nam trong `OnChartEvent` (thao tac tay) va co it nhat mot loi goi tu dong
    khong doi so. Dieu kien co `or` lan bien that thi de nguyen.
    """
    hang_chung = {m.group(1): _gia_tri_hang(m.group(2))
                  for m in _RX_INPUT_HANG.finditer(vb)}
    # pham vi ham + tham so mac dinh dung duoc nhu hang
    pham_vi = []                                  # (dau, cuoi, {ten: gia tri})
    for m in _RX_KHAI_HAM_DU.finditer(vb):
        ten_f, doi = m.group(1), m.group(2)
        a = m.end() - 1
        muc, b = 0, a
        for b in range(a, len(vb)):
            if vb[b] == "{":
                muc += 1
            elif vb[b] == "}":
                muc -= 1
                if muc == 0:
                    break
        pham_vi.append((a, b, ten_f, doi, m.start()))
    hang_ham = {}
    for a, b, ten_f, doi, d_khai in pham_vi:
        md = {}
        for d in doi.split(","):
            mm = re.fullmatch(r"\s*(?:const\s+)?\w+\s+(\w+)\s*=\s*(\S+)\s*", d)
            if mm and _gia_tri_hang(mm.group(2)) is not None and not re.search(
                    rf"\b{mm.group(1)}[ \t]*(?:[-+*/]?=(?!=)|\+\+|--)", vb[a:b]):
                # tham so bi GAN LAI trong than ham thi khong con la hang
                md[mm.group(1)] = _gia_tri_hang(mm.group(2))
        if not md:
            continue
        tu_dong = co_doi_tay = False
        hop_le = True
        for x in re.finditer(rf"\b{re.escape(ten_f)}[ \t]*\(", vb):
            if d_khai <= x.start() < a:
                continue                           # chinh khai bao
            k = _dong_ngoac(vb, x.end() - 1)
            if k < 0:
                continue
            noi = vb[x.end():k].strip()
            ham_goi = next((t for (aa, bb, t, _, _) in pham_vi
                            if aa < x.start() < bb), None)
            if not noi:
                tu_dong = True
            elif ham_goi == "OnChartEvent":
                co_doi_tay = True
            else:
                hop_le = False
        if hop_le and tu_dong:
            hang_ham[(a, b)] = md

    def _hang_tai(vt):
        h = dict(hang_chung)
        for (a, b), md in hang_ham.items():
            if a < vt < b:
                h.update(md)
        return h

    dau = [m.start() for m in re.finditer(r"\bif[ \t]*\(", vb)]
    for d0 in reversed(dau):
        if vb[d0 - 5:d0].rstrip().endswith("else"):
            continue                               # `else if` - de nguyen
        mo = vb.find("(", d0)
        k = _dong_ngoac(vb, mo)
        if k < 0:
            continue
        dk = vb[mo + 1:k]
        h = _hang_tai(d0)
        if not h:
            continue
        hh = _tach_hoac(_boc_ngoac(dk))
        if len(hh) > 1:
            kq = [_danh_gia_hang(x, h) for x in hh]
            if any(x is True for x in kq):
                tong = True
            elif all(x is False for x in kq):
                tong = False
            else:
                continue
            con = []
        else:
            ve = _tach_va(dk)
            kq = [_danh_gia_hang(x, h) for x in ve]
            if all(x is None for x in kq):
                continue
            if any(x is False for x in kq):
                tong = False
            else:
                con = [x for x, r in zip(ve, kq) if r is None]
                tong = True if not con else None
        if tong is None:
            vb = vb[:mo + 1] + " and ".join(con) + vb[k:]
            continue
        # than cua `if`: khoi `{...}` hoac mot cau lenh toi `;`
        j = k + 1
        while j < len(vb) and vb[j] in " \t\n":
            j += 1
        if j < len(vb) and vb[j] == "{":
            muc, e = 0, j
            for e in range(j, len(vb)):
                if vb[e] == "{":
                    muc += 1
                elif vb[e] == "}":
                    muc -= 1
                    if muc == 0:
                        break
            het = e + 1
        else:
            if re.match(r"(?:if|for|while|switch)\b", vb[j:]):
                continue                           # than la cau lenh long - de nguyen
            het = vb.find(";", j)
            if het < 0:
                continue
            het += 1
        me = re.match(r"\s*else\b", vb[het:])
        if tong:
            if me:
                continue                           # dung + co else: de nguyen
            vb = vb[:d0] + vb[j:het] + vb[het:]
        else:
            if me:
                vb = vb[:d0] + vb[het + me.end():]
            else:
                vb = vb[:d0] + vb[het:]
    return vb


#: QUY UOC CHI SO BAR MQL5 -> DSL (them 10/10/2026 toi, sua lech mot bar).
#:
#: Mo phong (`mo_phong.chay`) quyet dinh tai DONG bar i va vao lenh tai OPEN
#: bar i+1. EA MQL5 thi chay o TICK DAU cua bar moi (cong `IsNewBar`,
#: `curTime!=prevTime`, `dt.min==0`), tuc dung luc mo bar i+1. Luc do, theo
#: chi so MQL5:
#:   - bar k >= 1 (da dong) = bar i-(k-1) cua mo phong -> DSL `tre k-1`
#:     (`iClose(...,1)` = close bar vua dong = `close`; `iClose(...,2)` =
#:     `close tre 1`). Ban cu anh xa k -> tre k: tre THUA mot bar.
#:   - bar k = 0 (dang hinh thanh, moi co MOT tick): open = high = low =
#:     close = gia tick dau ~ close bar i (FX: gap giua hai bar H1 ~ 0). Nen
#:     `current[0].high/.low/.close/.open` -> `close` (tre 0). Chi bao doc o
#:     bar 0 (`MaValues` phan tu moi nhat) tinh voi gia tick dau ~ close bar i
#:     -> `tre 0`.
#:   - gio/thu cua EA (`TimeToStruct(curTime)`) la luc MO bar i+1 = luc DONG
#:     bar i -> toan hang lich mang `"luc": "dong"` (xem `ngu_phap._luc_dong`).
#: Khong nhin truoc: moi thu chi dung bar <= i. EA nao kiem lai o MOI tick
#: (khong co cong bar moi co hieu luc) thi thuc chat la lenh dung trong bar:
#: `_kiem_moi_tick` phat hien va gan khoi `trong_bar` (xem phan KIEM LAI MOI
#: TICK); gia bar 0 di qua token `_GIA0` de biet dieu kien nao la kich hoat.
_COT_GIA = {"close", "open", "high", "low"}


def _ten_bar_mql(goc: str, k: int) -> str:
    """Ten DSL cho `goc` o chi so bar MQL5 `k` (quy uoc o tren)."""
    if k <= 0:
        return "close" if goc in _COT_GIA else goc
    return goc + (f"[{k - 1}]" if k > 1 else "")


#: Token cho GIA SONG cua bar 0 (`current[0].high`, `iClose(..,0)`). Nghia DSL
#: van la `close` (tick dau ~ close bar i), nhung giu dau vet de biet dieu kien
#: nao doi theo tung tick - xem `_kiem_moi_tick` / khoi `trong_bar`.
_GIA0 = "_gia0_"


def _ten_bar_mql_song(goc: str, k: int) -> str:
    """Nhu `_ten_bar_mql` nhung gia bar 0 -> token `_GIA0` (danh dau gia song)."""
    if k <= 0 and goc in _COT_GIA:
        return _GIA0
    return _ten_bar_mql(goc, k)


def _chuan_hoa_mql5(vb: str) -> str:
    """Viet lai CU PHAP MQL5 ve dang bo doc da hieu. Khong doi nghia."""
    vb = vb.replace("&&", " and ").replace("||", " or ")
    vb = _gap_hang_cau_hinh(vb)
    # iClose(_Symbol,_Period,k) -> close[k-1]  (khung hien tai, quy uoc o tren)
    vb = re.sub(r"\bi(Close|Open|High|Low)[ \t]*\([ \t]*[^,()]+,[ \t]*"
                r"(?:_Period|0|PERIOD_CURRENT|Period\(\))[ \t]*,[ \t]*(\d+)[ \t]*\)",
                lambda m: _ten_bar_mql_song(m.group(1).lower(), int(m.group(2))), vb)
    # `_Point*x` voi x = 0 theo mac dinh cua tac gia -> 0
    hs = _hang_mql(vb)

    def _diem(m):
        x = m.group(1)
        v = float(x) if re.fullmatch(_SO, x) else hs.get(x)
        return "0" if v == 0 else m.group(0)
    vb = re.sub(r"\([ \t]*_Point[ \t]*\*[ \t]*(\w+)[ \t]*\)", _diem, vb)
    vb = re.sub(r"\([ \t]*(\w+)[ \t]*\*[ \t]*_Point[ \t]*\)", _diem, vb)

    # Mang du lieu: Copy*(sym, tf, start, count, arr) voi start/count la so
    series = set(re.findall(r"ArraySetAsSeries[ \t]*\([ \t]*([\w.]+)[ \t]*,[ \t]*true",
                            vb))
    mang = {}
    for m in re.finditer(r"\bCopy(Rates|High|Low|Close|Open)[ \t]*\([^,()]+,[^,()]+,"
                         r"[ \t]*(\d+)[ \t]*,[ \t]*(\d+)[ \t]*,[ \t]*(\w+)[ \t]*\)", vb):
        mang[m.group(4)] = (m.group(1).lower(), int(m.group(2)), int(m.group(3)))
    han = {}
    for m in re.finditer(r"([\w.]+)[ \t]*=[ \t]*(i[A-Za-z]+[ \t]*\([^;\n]*\))[ \t]*;", vb):
        ten_ham = m.group(2).split("(")[0].strip().lower()
        if ten_ham in _HAM_CB_MOT_BUFFER:
            han[m.group(1)] = m.group(2).replace(" ", "")
    for m in re.finditer(r"\bCopyBuffer[ \t]*\([ \t]*([\w.]+)[ \t]*,[ \t]*0[ \t]*,"
                         r"[ \t]*(\d+)[ \t]*,[ \t]*(\d+)[ \t]*,[ \t]*(\w+)[ \t]*\)", vb):
        if m.group(1) in han:
            mang[m.group(4)] = ("buf:" + han[m.group(1)], int(m.group(2)),
                                int(m.group(3)))

    def _lech(arr, k):
        loai, s, c = mang[arr]
        if not 0 <= k < c:
            return None
        return s + k if (arr in series or c == 1) else s + c - 1 - k

    def _ten(goc, sh):
        return _ten_bar_mql_song(goc, sh)     # sh = chi so bar MQL5 (0 = dang chay)

    def _rates(m):
        arr, k, cot = m.group(1), int(m.group(2)), m.group(3).lower()
        if arr not in mang or mang[arr][0] != "rates" or cot not in _COT_MANG:
            return m.group(0)
        sh = _lech(arr, k)
        return m.group(0) if sh is None else _ten(_COT_MANG[cot], sh)
    vb = re.sub(r"\b(\w+)\[(\d+)\]\.(high|low|close|open)\b", _rates, vb)

    def _don(m):
        arr, k = m.group(1), int(m.group(2))
        if arr not in mang or mang[arr][0] == "rates":
            return m.group(0)
        sh = _lech(arr, k)
        if sh is None:
            return m.group(0)
        loai = mang[arr][0]
        goc = loai[4:] if loai.startswith("buf:") else loai
        return _ten(goc, sh)
    vb = re.sub(r"(?<![\w.])(\w+)\[(\d+)\](?!\.)", _don, vb)

    # dt.hour trong PHEP SO SANH -> gio (chi khi dt la MqlDateTime)
    for dt in re.findall(r"\bMqlDateTime[ \t]+(\w+)", vb):
        vb = re.sub(rf"\b{dt}\.hour(?=[ \t]*(?:[<>]|==|!=))", "_gio_", vb)
        vb = re.sub(rf"\b{dt}\.day_of_week(?=[ \t]*(?:[<>]|==|!=))", "_thu_", vb)
    return _pivot_gio(vb)


#: Loai pivot co CUNG muc P = (H+L+C)/3 trong `MultiPivots.mqh`
#: (peterthomet/MetaTrader-5-and-4-Tools, Include/MultiPivots.mqh,
#: `PivotsCalculatePivots`). WOODIES/DEMARK/CAMARILLA tinh P khac -> khong dich.
_PIVOT_P_CHUAN = {"PIVOT_TRADITIONAL", "PIVOT_CLASSIC", "PIVOT_FIBONACCI"}


def _pivot_gio(vb: str) -> str:
    """`PivotsIsAbovePivot(x, pd.PivotsHour, "P")` -> `(x >= (high+low+close)/3)`.

    Dich theo MA THAT cua `MultiPivots.mqh` (doc 10/10/2026):
      - `PivotsIsAbovePivot(price, pivots, level)` = `price >= level`.
      - PivotsHour = PivotsHourList[1] = offset 0: khoang thoi gian la thanh H1
        DA DONG ngay truoc thanh H1 hien tai; H/L/C lay tren PERIOD_H1.
      - TRADITIONAL/CLASSIC/FIBONACCI: P = (Close+High+Low)/3.
    Chi dich khi file THAT SU bat pivot gio loai do (`Settings.PivotTypeHour=`)
    va co goi `.Calculate(` - khong thi struct de nguyen 0 va dich la noi doi.
    GIA DINH duy nhat: chay tren du lieu H1 (vong thu nghiem dung H1), luc do
    thanh H1 da dong ngay truoc (MQL5 bar 1) chinh la bar i cua mo phong
    (quy uoc `_ten_bar_mql`) -> H/L/C tre 0. Ghi o `gia_dinh`.
    PivotsDay / R1 / S1 / PivotsIsPivotRange (+-5*_Point, phu thuoc symbol)
    KHONG dich o day.
    """
    for m in re.finditer(r"\bTypePivotsData[ \t]+(\w+)[ \t]*;", vb):
        pd_ = m.group(1)
        mt = re.search(rf"\b{pd_}\.Settings\.PivotTypeHour[ \t]*=[ \t]*(\w+)[ \t]*;", vb)
        if not mt or mt.group(1) not in _PIVOT_P_CHUAN:
            continue
        if not re.search(rf"\b{pd_}\.Calculate[ \t]*\(", vb):
            continue
        vb = re.sub(
            rf"\bPivotsIsAbovePivot[ \t]*\([ \t]*([\w.\[\]]+)[ \t]*,[ \t]*{pd_}"
            rf"\.PivotsHour[ \t]*,[ \t]*\"P\"[ \t]*\)",
            lambda x: f"({x.group(1)} >= ((high+low+close)/3))", vb)
    return vb


def _giay_trong_ngay(ten: str, vi_tri: int, vb: str, sau: int = 0) -> int | None:
    """Gia tri giay-trong-ngay cua mot bien datetime xay tu `dt.hour=H`."""
    if sau > 4:
        return None
    gan = None
    for m in re.finditer(rf"(?:\bdatetime[ \t]+)?\b{re.escape(ten)}[ \t]*=[ \t]*([^;\n]+);",
                         vb[:vi_tri]):
        gan = (m.start(), m.group(1).strip())
    if gan is None:
        return None
    pos, bt = gan
    m = re.fullmatch(r"StructToTime[ \t]*\([ \t]*(\w+)[ \t]*\)", bt)
    if m:
        dt = m.group(1)
        h = mi = None
        for x in re.finditer(rf"\b{dt}\.(hour|min)[ \t]*=[ \t]*(\d+)[ \t]*;", vb[:pos]):
            if x.group(1) == "hour":
                h = int(x.group(2))
            else:
                mi = int(x.group(2))
        if h is None:
            return None
        return h * 3600 + (mi or 0) * 60
    m = re.fullmatch(r"(\w+)[ \t]*([+-])[ \t]*(\d+)", bt)
    if m:
        goc = _giay_trong_ngay(m.group(1), pos if m.group(1) == ten else pos,
                               vb, sau + 1)
        if goc is None:
            return None
        return goc + (int(m.group(3)) if m.group(2) == "+" else -int(m.group(3)))
    return None


def _bang_mql(vb: str) -> list[tuple[int, str, dict]]:
    """Bien MQL5 ma bang ky hieu chung khong thay: bien phien, gio, thu."""
    ra = []
    # Moi mang co the duoc Copy* nhieu lan o nhieu ham (Breakout1: `highs`/`lows`
    # o checkForClose la 3 bar da dong, o checkForOpen la khung phien 5-8h).
    # Truoc 10/10/2026 (dem) dict giu lan Copy CUOI trong file -> `lowrange` cua
    # checkForClose bi dich thanh day phien. Gio lay lan Copy GAN NHAT TRUOC phep gan.
    copy: dict = {}
    for m in re.finditer(r"\bCopy(High|Low)[ \t]*\([^,()]+,[^,()]+,[ \t]*(\w+)[ \t]*,"
                         r"[ \t]*(\w+)[ \t]*,[ \t]*(\w+)[ \t]*\)", vb):
        copy.setdefault(m.group(4), []).append(
            (m.start(), m.group(1).lower(), m.group(2), m.group(3)))
    for m in re.finditer(r"(?:\bdouble[ \t]+)?\b(\w+)[ \t]*=[ \t]*(\w+)\[[ \t]*Array"
                         r"(Maximum|Minimum)[ \t]*\([ \t]*\2[ \t]*\)[ \t]*\][ \t]*;", vb):
        ten, arr, mm = m.group(1), m.group(2), m.group(3)
        truoc = [x for x in copy.get(arr, []) if x[0] < m.start()]
        if not truoc:
            continue
        vt, cot, a, b = truoc[-1]
        if (cot == "high") != (mm == "Maximum"):
            continue
        if a.isdigit() and b.isdigit():
            # Bar MQL5 a..a+b-1 -> DSL tre a-1..a+b-2 (quy uoc o `_ten_bar_mql`).
            # a = 0: bar dang chay chi co gia tick dau ~ close bar i <= high bar
            # i (co trong cua so khi b >= 2) -> bo no, con b-1 bar.
            n, tre = int(b), int(a) - 1
            if tre < 0:
                n, tre = n - 1, 0
            if n < 1:
                continue
            t = {"chi_bao": "cao_nhat" if cot == "high" else "thap_nhat",
                 "n": n, "cua": {"chi_bao": "gia", "cot": cot}}
            if tre:
                t = {"chi_bao": "tre", "cua": t, "n": tre}
        else:
            s0 = _giay_trong_ngay(a, vt, vb)
            s1 = _giay_trong_ngay(b, vt, vb)
            if s0 is None or s1 is None or s0 < 0 or s1 >= 86400 or s1 < s0:
                continue
            gt, gd = -(-s0 // 3600), s1 // 3600
            if gd < gt:
                continue
            t = {"chi_bao": "cao_trong_gio" if cot == "high" else "thap_trong_gio",
                 "gio_tu": int(gt), "gio_den": int(gd), "luc": "dong"}
        ra.append((m.start(), ten, dict(t, _thang=1)))
    # gio/thu EA doc o tick dau bar i+1 = luc DONG bar i (quy uoc chi so bar)
    ra.append((0, "_gio_", {"chi_bao": "gio", "luc": "dong", "_thang": 1}))
    ra.append((0, "_thu_", {"chi_bao": "ngay_trong_tuan", "luc": "dong", "_thang": 1}))
    return ra


_PHEP_DAO = {">": "<=", ">=": "<", "<": ">=", "<=": ">", "==": "!=", "!=": "=="}


def _so_sanh_tong_quat(ve: str, vi_tri: int, bang_cb: list,
                       bang_bl: list) -> dict | None:
    """`a + b*2 < c` - so sanh co VE la bieu thuc so hoc (chi che do MQL5)."""
    muc, cho = 0, []
    i = 0
    while i < len(ve):
        c = ve[i]
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        elif muc == 0 and c in "<>=!":
            op = ve[i:i + 2] if ve[i:i + 2] in (">=", "<=", "==", "!=") else c
            if op in (">", "<", ">=", "<=", "==", "!="):
                cho.append((i, op))
                i += len(op)
                continue
        i += 1
    if len(cho) != 1:
        return None
    i, op = cho[0]
    a, b = ve[:i].strip(), ve[i + len(op):].strip()

    def _ve(x):
        x = _boc_ngoac(x)
        t = _toan_hang(x, vi_tri, bang_cb, bang_bl)
        if t is None:
            t = _tuyen_tinh(x, vi_tri, bang_cb, bang_bl, 0)
        if t and t.get("chi_bao") == "tuyen_tinh" and len(t["toan_hang"]) == 1 \
                and t["he_so"] == [1.0] and not t.get("cong_them"):
            t = t["toan_hang"][0]           # `c1` = close[1]: khong boc thua
        return t
    trai, phai = _ve(a), _ve(b)
    if not trai or not phai or not _hop_thang_do(trai, phai):
        return None
    if op in ("==", "!="):
        kia = phai if "hang" in trai else trai
        if not (("hang" in trai) ^ ("hang" in phai)) or \
                kia.get("chi_bao") not in ("gio", "ngay_trong_tuan"):
            return None
    return {"trai": trai, "phep": op, "phai": phai}


#: Dieu kien QUAN TRI LENH / KIEM DU LIEU - khong phai tin hieu.
_RX_QUAN_TRI = re.compile(
    r"\bCopy\w+|\bPosition\w*|\bOrders?Total|\bPositionsTotal|\bCountMy\w*"
    r"|\bprevTime\b|\bcurTime\b|\blast\w*day\b|\.day\b|\bIsNewBar\b|Spread"
    r"|INVALID_HANDLE|\bstartmanual\b|\.min\b|StartAtFullHourOnly|IsStopped"
    r"|\bInpMagic\b|\bmagic", re.I)
_RX_GIA_TRI_HONG = re.compile(r"^\s*!?\s*[\w.\[\]]+\s*(?:<=|==)\s*0(?:\.0*)?\s*$")


def _la_quan_tri(bt: str) -> bool:
    phan = [p.strip() for p in re.split(r"\bor\b|\band\b", bt) if p.strip()]
    return bool(phan) and all(_RX_QUAN_TRI.search(p) or _RX_GIA_TRI_HONG.match(p)
                              for p in phan)


def _phu_dinh(bt: str, vi_tri: int, bang_cb: list, bang_bl: list
              ) -> list[dict] | None:
    """NOT(bt) -> danh sach VA. `a or b` -> not a VA not b; mot so sanh -> dao phep."""
    ds = []
    for p in _tach_hoac(bt):
        p = _boc_ngoac(p)
        if _tach_va(p) != [p]:
            return None                 # NOT(a and b) = HOAC -> khong dien dat duoc
        dk, ho = _no_dieu_kien(p, vi_tri, bang_cb, bang_bl)
        if ho or len(dk) != 1 or dk[0].get("phep") not in _PHEP_DAO:
            return None
        ds.append(dict(dk[0], phep=_PHEP_DAO[dk[0]["phep"]]))
    return ds


def _tach_hoac(bt: str) -> list[str]:
    ra, sau, muc = [], 0, 0
    for i, c in enumerate(bt):
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        elif muc == 0 and bt.startswith("or", i) and \
                (i == 0 or not (bt[i - 1].isalnum() or bt[i - 1] == "_")) and \
                (i + 2 >= len(bt) or not (bt[i + 2].isalnum() or bt[i + 2] == "_")):
            ra.append(bt[sau:i])
            sau = i + 2
    ra.append(bt[sau:])
    return [x.strip() for x in ra if x.strip()]


def _dau_ham(vb: str, vi_tri: int) -> tuple[int, str | None]:
    """(vi tri `{` mo than ham, ten ham) chua `vi_tri`."""
    goc, ten = 0, None
    for m in _KHAI_HAM.finditer(vb):
        if m.start() > vi_tri:
            break
        k = vb.find("{", m.end())
        if 0 <= k < vi_tri:
            goc, ten = k, m.group(1)
    return goc, ten


def _cac_if_bao(vb: str, vi_tri: int) -> tuple[list[tuple[int, str]], bool]:
    """Moi `if(...)` co KHOI chua `vi_tri` (trong cung ham). Tra (ds, gap_else)."""
    goc, _ = _dau_ham(vb, vi_tri)
    ra, gap_else = [], False
    # `if(dk) lenh;` tren CUNG dong, hoac dong ngay truoc khong co `{`
    dong_dau = vb.rfind("\n", 0, vi_tri) + 1
    truoc = vb[dong_dau:vi_tri]
    for doan, moc in ((truoc, dong_dau),):
        m = re.search(r"\bif[ \t]*\(", doan)
        if m:
            k = _dong_ngoac(doan, m.end() - 1)
            if k > 0 and not doan[k + 1:].strip().startswith("{") and \
                    "{" not in doan[k + 1:]:
                ra.append((moc + m.start(), doan[m.end():k]))
    if not ra and dong_dau > 0:
        d0 = vb.rfind("\n", 0, dong_dau - 1) + 1
        dong_truoc = vb[d0:dong_dau - 1]
        m = re.match(r"^[ \t]*(?:else[ \t]+)?if[ \t]*\(", dong_truoc)
        if m and not truoc.strip().startswith("{"):
            k = _dong_ngoac(dong_truoc, m.end() - 1)
            if k > 0 and not dong_truoc[k + 1:].strip():
                ra.append((d0 + m.start(), dong_truoc[m.end():k]))
    muc = 0
    i = vi_tri - 1
    while i > goc:
        c = vb[i]
        if c == "}":
            muc += 1
        elif c == "{":
            if muc == 0:
                dau = vb[max(goc, i - 400):i].rstrip()
                if dau.endswith(")"):
                    # lui tim `(` mo cap
                    j, sau = len(dau) - 1, 0
                    while j >= 0:
                        if dau[j] == ")":
                            sau += 1
                        elif dau[j] == "(":
                            sau -= 1
                            if sau == 0:
                                break
                        j -= 1
                    tu = re.search(r"(\w+)[ \t]*$", dau[:j])
                    if tu and tu.group(1) == "if":
                        ra.append((i - len(dau) + j, dau[j + 1:-1]))
                        if re.search(r"\belse[ \t]*$", dau[:tu.start()]):
                            gap_else = True
                elif re.search(r"\belse$", dau):
                    gap_else = True
            else:
                muc -= 1
        i -= 1
    return ra, gap_else


def _thoat_som(vb: str, tu: int, den: int) -> list[str]:
    """`if(dk) return;` o MUC THAN HAM giua `tu` va `den`."""
    ra = []
    for m in re.finditer(r"\bif[ \t]*\(", vb[tu:den]):
        a = tu + m.end() - 1
        k = _dong_ngoac(vb, a)
        if k < 0 or k > den:
            continue
        sau = vb[k + 1:den]
        if not re.match(r"\s*return\b[^;]*;", sau):
            continue
        # chi lay o muc than ham (khong nam trong khoi con)
        doan = vb[tu + 1:tu + m.start()]
        if doan.count("{") - doan.count("}") != 0:
            continue
        ra.append(vb[a + 1:k].strip())
    return ra


def _chieu_nhanh(vb: str, tu: int, den: int, co: str) -> int | None:
    """Trong khoi tu `tu` den `den`: `if(co){ ... type = ORDER_TYPE_X ... }`."""
    for m in re.finditer(rf"\bif[ \t]*\([ \t]*{re.escape(co)}[ \t]*\)\s*\{{", vb[tu:den]):
        a = tu + m.end()
        k = vb.find("}", a)
        than = vb[a:k if k > 0 else den]
        if "{" in than:
            continue
        mm = re.findall(r"=[ \t]*ORDER_TYPE_(BUY|SELL)\b", than)
        if len(set(mm)) == 1:
            return 1 if mm[0] == "BUY" else -1
    return None


def _ham_tin_hieu(vb: str, ten_ham_lenh: str, chieu: int, tru: int
                  ) -> tuple[str, int, list[str]] | None:
    """`OpenTrade(sig > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, ...)` voi
    `sig = GetSignal()` va `if(dk) return 1;` -> (dk cua chieu, vi tri, thoat som)."""
    for vt in _cho_goi(vb, ten_ham_lenh, tru)[:4]:
        k = _dong_ngoac(vb, vb.find("(", vt))
        loi_goi = vb[vt:k]
        m = re.search(r"\(\s*(\w+)\s*(>|==)\s*(0|1)\s*\?\s*ORDER_TYPE_BUY\s*:\s*"
                      r"ORDER_TYPE_SELL", loi_goi)
        if not m or (m.group(2) == "==" and m.group(3) != "1") or \
                (m.group(2) == ">" and m.group(3) != "0"):
            continue
        bien = m.group(1)
        goc, _ = _dau_ham(vb, vt)
        mg = None
        for x in re.finditer(rf"\b{bien}[ \t]*=[ \t]*(\w+)[ \t]*\([ \t]*\)[ \t]*;",
                             vb[goc:vt]):
            mg = x
        if not mg:
            continue
        ten_f = mg.group(1)
        thoat = _thoat_som(vb, goc, vt)
        mk = re.search(rf"^[ \t]*(?:int|double|long)[ \t]+{ten_f}[ \t]*\([^)]*\)\s*\{{",
                       vb, re.M)
        if not mk:
            continue
        a = mk.end() - 1
        muc, b = 0, a
        for b in range(a, len(vb)):
            if vb[b] == "{":
                muc += 1
            elif vb[b] == "}":
                muc -= 1
                if muc == 0:
                    break
        than = vb[a:b]
        dich = r"\+?1" if chieu == 1 else r"-1"
        for x in re.finditer(r"\bif[ \t]*\(", than):
            kk = _dong_ngoac(than, x.end() - 1)
            if kk > 0 and re.match(rf"\s*return[ \t]*\(?[ \t]*{dich}[ \t]*\)?[ \t]*;",
                                   than[kk + 1:]):
                thoat += _thoat_som(vb, a, a + x.start())
                return than[x.end():kk].strip(), a + x.start(), thoat
    return None


def _tre_gia(t: dict) -> int | None:
    """Do tre (bar) neu `t` CHI la gia tho: `close` -> 0, `close tre 2` -> 2."""
    if not isinstance(t, dict):
        return None
    if t.get("chi_bao") == "gia":
        return 0
    if t.get("chi_bao") == "tre" and (t.get("cua") or {}).get("chi_bao") == "gia":
        return int(t.get("n", 1))
    return None


def _tre_nho_nhat_cua_moc(t: dict) -> int | None:
    """Moc tinh TOAN tu gia tho (gia/tre/tuyen_tinh cua chung): do tre NHO nhat."""
    k = _tre_gia(t)
    if k is not None:
        return k
    if isinstance(t, dict) and t.get("chi_bao") == "tuyen_tinh" and t.get("toan_hang"):
        ds = [_tre_nho_nhat_cua_moc(x) for x in t["toan_hang"]]
        if all(x is not None for x in ds):
            return min(ds)
    return None


def _ho_gia_thuan(dk: list[dict], chieu: int) -> str | None:
    """Ho cho co che CHI so gia voi moc gia cu hon (them 10/10/2026).

    `close[1] > close[2]` hay `close < (H1+L1+C1)/3` khong co chi bao nao nen
    `_ho_cua` ra `khac` -> kho tu choi. Nhung kinh te hoc cua chung RO:
      - Mua khi gia moi TREN moc cu (ban khi DUOI) = theo dong luong -> `xu_huong`.
      - Mua khi gia moi DUOI moc cu (ban khi TREN) = cuoc hoi ve -> `quay_ve_trung_binh`.
    Chi gan khi MOI dieu kien la gia tho ve trai, moc tinh hoan toan tu gia
    CU HON ve phai, va moi dieu kien cung mot huong. Khac di thi tra None
    (giu `khac`, khong xep bua).
    """
    huong = set()
    for d in dk:
        a = _tre_gia(d.get("trai"))
        b = _tre_nho_nhat_cua_moc(d.get("phai"))
        if a is None or b is None or d.get("phep") not in _PHEP:
            return None
        # Moc phai CU HON gia ben trai; hoac CUNG bar nhung la to hop cua
        # NHIEU cot (pivot (H+L+C)/3 cua bar vua dong so voi gia tick dau bar
        # moi, sau khi sua lech mot bar 10/10 toi) - van la "gia so voi moc".
        cung_bar_to_hop = (b == a and (d.get("phai") or {}).get("chi_bao") == "tuyen_tinh"
                           and len((d.get("phai") or {}).get("toan_hang") or []) >= 2)
        if b < a or (b == a and not cung_bar_to_hop):
            return None
        tren = d["phep"] in (">", ">=")
        huong.add("xu_huong" if tren == (chieu == 1) else "quay_ve_trung_binh")
    return huong.pop() if len(huong) == 1 else None


def _bo_trung_dieu_kien(dk: list[dict]) -> list[dict]:
    """Bo dieu kien TRUNG LAP hoac BI KEO THEO (cung hai ve: `<` keo theo `<=`).

    `if(c1>c2) return 1; if(c1<c2) return -1;` -> nhanh ban ra
    `c1<c2 va c1<=c2 va c1<=c2` (phu dinh cac `return` truoc). Dung nghia nhung
    thua; bo di khong doi tap bar kich hoat.
    """
    ra: list[dict] = []
    for d in dk:
        if any(d == x for x in ra):
            continue
        ra.append(d)
    giu = []
    for d in ra:
        chat = {"<=": "<", ">=": ">"}.get(d.get("phep"))
        if chat and any(x.get("phep") == chat and x.get("trai") == d.get("trai")
                        and x.get("phai") == d.get("phai") for x in ra):
            continue
        giu.append(d)
    return giu


_MOC_PIVOT_GIO = {"chi_bao": "tuyen_tinh", "toan_hang": [
    {"chi_bao": "gia", "cot": c} for c in ("high", "low", "close")]}


def _co_pivot_gio(t) -> bool:
    if isinstance(t, dict):
        if t.get("chi_bao") == "tuyen_tinh" and \
                t.get("toan_hang") == _MOC_PIVOT_GIO["toan_hang"]:
            return True
        return any(_co_pivot_gio(v) for v in t.values())
    if isinstance(t, list):
        return any(_co_pivot_gio(v) for v in t)
    return False


def _ma_chet(vb: str, vi_tri: int) -> bool:
    """Lenh vao nam SAU mot `return;` VO DIEU KIEN o muc than ham -> khong bao gio chay.

    Do that 10/10/2026: `Pivots1.mq5` dat SellLimit tai R1 roi `return;` - toan
    bo khoi breakout + PositionOpen phia duoi la ma chet tac gia de lai. Dich
    khoi do ra co che la gan cho tac gia mot chien luoc ho KHONG chay.
    """
    goc, _ = _dau_ham(vb, vi_tri)
    if not goc:
        return False
    muc, i = 0, goc
    while i < vi_tri:
        c = vb[i]
        if c == "{":
            muc += 1
        elif c == "}":
            muc -= 1
        elif muc == 1 and vb.startswith("return", i) and \
                not (vb[i - 1].isalnum() or vb[i - 1] == "_") and \
                re.match(r"return\b[^;{}]*;", vb[i:]):
            # `return` o muc than ham: VO DIEU KIEN khi doan tu het cau lenh
            # truoc toi no khong co `if(`/`else`/`for(`/`while(`.
            if not re.search(r"\b(?:if|for|while)[ \t]*\(|\belse\b",
                             _dong_truoc_cau(vb, goc, i)):
                return True
        i += 1
    return False


def _dong_truoc_cau(vb: str, goc: int, i: int) -> str:
    """Doan tu het cau lenh truoc (`;`, `{`, `}`) toi vi tri `i`."""
    k = max(vb.rfind(";", goc, i), vb.rfind("{", goc, i), vb.rfind("}", goc, i))
    return vb[k + 1:i]


#: Bien TRANG THAI VI THE / LUOI: dieu kien phu thuoc gia vao lenh, so lenh dang
#: mo, loi lo dang chay - KHONG phai tin hieu tren thanh nen.
_RX_VI_THE = re.compile(
    r"\bTradesinfo\.|\bpostotal\b|\bPosTotal\b|\bprofits\b|\bpeakwin\b"
    r"|\bzonesequence\b|\bPositionsTotal\b|\bPOSITION_(?:PROFIT|PRICE_OPEN)\b"
    r"|\bIsTRadeOpen\b|\bhedgeatlevel\b", re.I)


def _phu_thuoc_vi_the(bt: str, vi_tri: int, bang_bl: list, sau: int = 0) -> bool:
    """Guard (no xuyen qua bien bool) co phu thuoc trang thai vi the khong."""
    if sau > 4:
        return False
    if _RX_VI_THE.search(bt):
        return True
    for ten in set(re.findall(_TEN, bt)):
        dn = None
        for pos, t, bt2 in bang_bl:
            if pos >= vi_tri:
                break
            if t == ten:
                dn = (pos, bt2)
        if dn and _phu_thuoc_vi_the(dn[1], dn[0], bang_bl, sau + 1):
            return True
    return False


# ---------------------------------------------------------------------
# KIEM LAI MOI TICK -> LENH DUNG TRONG BAR (them 10/10/2026)
#
# Quy uoc chi so bar (`_ten_bar_mql`) gia dinh EA chay o TICK DAU bar moi. Nhieu
# EA khong nhu vay: Breakout1 co cong `curTime==prevTime` nhung `prevTime` chi
# duoc gan SAU khi vao lenh (moi nhanh khong pha vo deu `return` truoc) ->
# cong khong bao gio dong khi chua co lenh; Breakout2/2-2/3 bo han cong. Khi
# do `current[0].high > highrange` duoc kiem o MOI tick = mot lenh dung cho
# san o highrange, khop GIUA bar.
#
# Cach lam: (1) `_kiem_moi_tick` doc chuoi goi tu ham chua lenh vao nguoc len
# `OnTick`, tim cong bar moi CO HIEU LUC; (2) moi dieu kien duoc phan loai theo
# gia song bar 0 (`_GIA0`): dieu kien KICH HOAT `gia_song ? muc` (muc co dinh
# trong bar) hay dieu kien CHO PHEP (khong dung gia song). Du dieu kien thi
# co che mang them khoi `trong_bar` (xem `ngu_phap.sinh_trong_bar`).
# ---------------------------------------------------------------------
_RX_CONG_NEWBAR = re.compile(
    r"\bif[ \t]*\([ \t]*![ \t]*\w*new_?bar\w*[ \t]*(?:\([^()]*\))?[ \t]*\)\s*\{?\s*return\b",
    re.I)


def _cuoi_khoi(vb: str, mo: int) -> int:
    """Vi tri `}` dong cap voi `{` tai `mo` (-1 neu khong co)."""
    muc = 0
    for k in range(mo, len(vb)):
        if vb[k] == "{":
            muc += 1
        elif vb[k] == "}":
            muc -= 1
            if muc == 0:
                return k
    return -1


def _cong_bar_moi(vb: str, goc: int, den: int) -> str | None:
    """Cong bar moi CO HIEU LUC o muc than ham, giua `{` tai `goc` va `den`.

    - `if(!IsNewBar()) return;`                            -> "IsNewBar"
    - `if(dt.min!=0) return;` (moi chay trong phut dau)     -> "phut_dau"
    - `if(curTime==prevTime) return;` CHI KHI phep gan
      `prevTime=curTime;` dung TRUOC moi `return` sau cong  -> "prevTime"
      (gan o cuoi ham, sau lenh vao, thi moi tick chua co lenh deu di qua cong).
    """
    doan = vb[goc:den]
    if _RX_CONG_NEWBAR.search(doan):
        return "IsNewBar"
    het_ham = _cuoi_khoi(vb, goc)
    het_ham = len(vb) if het_ham < 0 else het_ham
    for m in re.finditer(r"\bif[ \t]*\(", doan):
        a = goc + m.end() - 1
        k = _dong_ngoac(vb, a)
        if k < 0 or k > den:
            continue
        mr = re.match(r"\s*\{?\s*return\b[^;]*;\s*\}?", vb[k + 1:])
        if not mr:
            continue
        truoc = vb[goc + 1:goc + m.start()]
        if truoc.count("{") - truoc.count("}") != 0:
            continue                               # khong o muc than ham
        g = vb[a + 1:k]
        ve = _tach_va(g)
        if any(re.fullmatch(r"\w+\.min\s*(?:!=\s*0|>\s*0)", x) for x in ve):
            return "phut_dau"
        mm = next((re.fullmatch(r"(\w+)\s*==\s*(\w+)", x) for x in ve
                   if re.fullmatch(r"(\w+)\s*==\s*(\w+)", x)), None)
        if not mm:
            continue
        A, B = mm.group(1), mm.group(2)
        e = k + 1 + mr.end()
        sau = vb[e:het_ham]
        r = re.search(r"\breturn\b", sau)
        g_ = re.search(rf"\b(?:{A}\s*=\s*{B}|{B}\s*=\s*{A})\s*;", sau)
        if g_ and (r is None or g_.start() < r.start()):
            return "prevTime"
    return None


def _kiem_moi_tick(vb: str, vi_tri: int, sau: int = 0) -> bool | None:
    """Lenh vao o `vi_tri` co bi kiem lai o MOI tick khong.

    True  = co it nhat mot duong goi tu `OnTick` toi lenh vao KHONG qua cong bar
            moi co hieu luc. False = moi duong deu qua cong. None = khong ro
            (ham khong noi duoc ve `OnTick`, vd chi goi tu `OnChartEvent`).
    """
    goc, ten = _dau_ham(vb, vi_tri)
    if not ten:
        return None
    if _cong_bar_moi(vb, goc, vi_tri):
        return False
    if ten == "OnTick":
        return True
    if sau >= 4:
        return None
    kq = []
    for c in _cho_goi(vb, ten, goc):
        g2, t2 = _dau_ham(vb, c)
        if t2 == ten:
            continue                                # de quy / chinh khai bao
        ifs, _ = _cac_if_bao(vb, c)
        if any(re.search(r"new_?bar", g, re.I) for _, g in ifs):
            kq.append(False)
            continue
        kq.append(_kiem_moi_tick(vb, c, sau + 1))
    if any(x is True for x in kq):
        return True
    if kq and all(x is False for x in kq):
        return False
    return None


def _co_bar0(t) -> bool:
    if isinstance(t, dict):
        return bool(t.get("_bar0")) or any(_co_bar0(v) for v in t.values())
    if isinstance(t, list):
        return any(_co_bar0(v) for v in t)
    return False


def _bo_bar0(t):
    if isinstance(t, dict):
        return {k: _bo_bar0(v) for k, v in t.items() if k != "_bar0"}
    if isinstance(t, list):
        return [_bo_bar0(v) for v in t]
    return t


_DAO_VE = {">": "<", ">=": "<=", "<": ">", "<=": ">="}


def _loai_bar0(d: dict) -> str:
    """`khong` (co dinh trong bar) | `kich_trai`/`kich_phai` (gia song ? muc co
    dinh) | `phuc_tap` (gia song nam trong bieu thuc - khong dich duoc thanh muc)."""
    if "vung" in d:
        return "phuc_tap" if _co_bar0(d) else "khong"
    tr, ph = d.get("trai"), d.get("phai")
    a, b = _co_bar0(tr), _co_bar0(ph)
    if not a and not b:
        return "khong"
    if d.get("phep") not in _DAO_VE:
        return "phuc_tap"
    if a and not b and isinstance(tr, dict) and tr.get("_bar0"):
        return "kich_trai"
    if b and not a and isinstance(ph, dict) and ph.get("_bar0"):
        return "kich_phai"
    return "phuc_tap"


def _he_tuyen_tinh(t, he: float = 1.0, ra: dict | None = None) -> dict:
    """Toan hang -> {khoa toan hang: he so} (+ "__c") de so hai muc bang nhau."""
    ra = {} if ra is None else ra
    if isinstance(t, dict) and t.get("chi_bao") == "tuyen_tinh":
        for x, h in zip(t.get("toan_hang") or [], t.get("he_so") or []):
            _he_tuyen_tinh(x, he * float(h), ra)
        ra["__c"] = ra.get("__c", 0.0) + he * float(t.get("cong_them", 0.0) or 0.0)
        return ra
    if isinstance(t, dict) and "hang" in t:
        ra["__c"] = ra.get("__c", 0.0) + he * float(t["hang"])
        return ra
    k = json.dumps(t, sort_keys=True)
    ra[k] = ra.get(k, 0.0) + he
    return ra


def _muc_bang_nhau(a, b) -> bool:
    x, y = _he_tuyen_tinh(a), _he_tuyen_tinh(b)
    for k in set(x) | set(y):
        if abs(x.get(k, 0.0) - y.get(k, 0.0)) > 1e-9:
            return False
    return True


def _ap_moi_tick(cac: list[dict], moi_tick: bool | None) -> None:
    """Gan `trong_bar` / `gia_dinh` cho cac co che cua MOT lenh vao. Doi tai cho."""
    loai = [sp.pop("_loai_b0", None) or [] for sp in cac]
    locs = [sp.pop("_loc", None) or [] for sp in cac]
    if moi_tick is not True or not cac:
        return

    def _kich(sp, lb):
        ra = []
        for k, (d, x) in enumerate(zip(sp["vao"], lb)):
            if x == "kich_trai":
                ra.append((k, ">" if d["phep"] in (">", ">=") else "<", d["phai"]))
            elif x == "kich_phai":
                ra.append((k, ">" if _DAO_VE[d["phep"]] in (">", ">=") else "<", d["trai"]))
        return ra

    kich = [_kich(sp, lb) for sp, lb in zip(cac, loai)]
    # CAP BU NHAU: `if(up||down)` voi up = gia > M, down = gia < M (cung muc, cung
    # dieu kien cho phep) -> o TICK DAU luon co mot chieu kich hoat (tru khi gia
    # bang dung M), lenh vao chan chieu kia. Tick dau la DUNG, khong phai xap xi.
    if len(cac) == 2 and all(len(k) == 1 for k in kich) and \
            {kich[0][0][1], kich[1][0][1]} == {">", "<"} and \
            cac[0]["chieu"] != cac[1]["chieu"] and \
            _muc_bang_nhau(kich[0][0][2], kich[1][0][2]):
        con = [sorted(json.dumps(d, sort_keys=True) for j, d in enumerate(sp["vao"])
                      if j != kk[0][0]) for sp, kk in zip(cac, kich)]
        if con[0] == con[1]:
            for sp in cac:
                sp.setdefault("gia_dinh", []).append(
                    "EA kiem lai MOI tick nhung cap mua/ban bu nhau quanh cung muc: "
                    "tick dau bar luon kich hoat mot chieu -> dich theo tick dau la "
                    "dung (tru khi gia tick dau bang dung muc)")
                sp["kiem_moi_tick"] = "cap_bu_nhau"
            return
    for ii, (sp, lb, kk) in enumerate(zip(cac, loai, kich)):
        sp["kiem_moi_tick"] = True
        if "phuc_tap" in lb:
            sp.setdefault("gia_dinh", []).append(
                "EA kiem lai MOI tick; gia song nam trong bieu thuc khong dua duoc ve "
                "mot muc -> dich theo tick dau bar la XAP XI")
            continue
        if not kk:
            sp.setdefault("gia_dinh", []).append(
                "EA kiem lai MOI tick nhung moi dieu kien co dinh trong bar -> tick dau dung")
            continue
        huong = {h for _, h, _ in kk}
        if len(huong) != 1:
            sp.setdefault("gia_dinh", []).append(
                "EA kiem lai MOI tick; gia song bi kep hai phia -> tick dau la XAP XI")
            continue
        h = huong.pop()
        for k, x in enumerate(lb):
            if x == "kich_phai":                    # dua gia song ve ve trai
                d = sp["vao"][k]
                sp["vao"][k] = {"trai": d["phai"], "phep": _DAO_VE[d["phep"]],
                                "phai": d["trai"]}
        sp["trong_bar"] = {"huong": h, "kich": [k for k, _, _ in kk]}
        # CO vs LOC (10/10/2026 dem): `bool up = gia > M;` la CO cua nhanh (dung
        # cuc tri bar dang chay, bat len la giu suot bar); `if(up && gia < MA)
        # return;` la LOC gan voi co. LOC cua MOT co dang bat chan MOI lenh vao
        # trong nhom (return som) - `mo_phong.chay_he` dung de chan cheo.
        loc = [k for k, _, _ in kk if k in locs[ii]]
        if loc and len(loc) < len(kk):
            sp["trong_bar"]["loc"] = loc
        sp.setdefault("gia_dinh", []).append(
            "EA kiem lai MOI tick -> lenh DUNG khop trong bar khi gia "
            + ("vuot len" if h == ">" else "xuyen xuong")
            + " muc (khoi `trong_bar`); `vao` giu ban xap xi tick dau")


# ---------------------------------------------------------------------
# SL/TP + KEO SL + "MOT LENH MOT NGAY" (them 10/10/2026 dem)
#
# Truoc day moi co che chi giu `giu` bar roi dong - EA that (Breakout1) dat
# SL = bien doi dien cua khung phien, TP = gia_vao +/- (gia_vao - SL)*TPFactor,
# keo SL theo day/dinh 3 bar da dong (`checkForClose`), va CHAN moi lenh sau
# lenh dau trong ngay (`if(lastupday==dt.day || lastdownday==dt.day) return;`).
# Bo qua nhung thu do = mo phong mot he KHAC voi he tac gia chay.
# Khoi sinh ra (doc o `ngu_phap.sinh_chan` / `mo_phong.chay_he`):
#   "sltp": {"sl": toan_hang, "tp": he_so_R | None, "keo": toan_hang | None}
#   "mot_lenh_ngay": {"nhom": id lenh vao, "chan_boi": [bien...], "dat": [bien...]}
# Chi dich khi MOI mau deu doc duoc chac chan; khong thi de nguyen (`giu`) va
# ghi `gia_dinh` - khong doan.
# ---------------------------------------------------------------------
def _tach_doi_so(vb: str, mo: int) -> list[str] | None:
    """Doi so cap muc 0 cua loi goi co `(` tai `mo`."""
    k = _dong_ngoac(vb, mo)
    if k < 0:
        return None
    ra, muc, dau = [], 0, mo + 1
    for i in range(mo + 1, k):
        c = vb[i]
        if c in "([":
            muc += 1
        elif c in ")]":
            muc -= 1
        elif c == "," and muc == 0:
            ra.append(vb[dau:i].strip())
            dau = i + 1
    ra.append(vb[dau:k].strip())
    return ra


def _khoi_co(vb: str, tu: int, den: int, co: str) -> tuple[int, int] | None:
    """Khoi `if(co){ ... }` (khong long) giua `tu` va `den`."""
    for m in re.finditer(rf"\bif[ \t]*\([ \t]*{re.escape(co)}[ \t]*\)\s*\{{", vb[tu:den]):
        a = tu + m.end() - 1
        k = _cuoi_khoi(vb, a)
        if k > 0:
            return a, k
    return None


def _gan_cuoi(doan: str, ten: str) -> re.Match | None:
    ra = None
    for m in re.finditer(rf"(?<![\w.]){re.escape(ten)}[ \t]*=(?!=)[ \t]*([^;]+);", doan):
        ra = m
    return ra


def _muc_dong(t) -> bool:
    """Toan hang co dinh trong bar (khong dung gia song bar 0)."""
    return isinstance(t, dict) and not _co_bar0(t)


def _sltp_mql(vb: str, m, chieu: int, co: str | None, vi: int, bang_cb: list,
              bang_bl: list, hang: dict) -> tuple[dict | None, list[str]]:
    """Khoi `sltp` cho MOT nhanh cua lenh vao `m` (PositionOpen). (khoi, ghi_chu)."""
    if m.group("ham") != "PositionOpen":
        return None, []
    mo = vb.find("(", m.start())
    ds = _tach_doi_so(vb, mo)
    if not ds or len(ds) < 6:
        return None, []
    gia, sl, tp = ds[3], ds[4], ds[5]
    if sl in ("NULL", "0", "0.0") and tp in ("NULL", "0", "0.0"):
        return None, []
    ghi = []
    if not all(re.fullmatch(_TEN, x) for x in (gia, sl, tp)):
        return None, [f"SL/TP la bieu thuc truc tiep ({sl}, {tp}) - chua dich, van giu `giu`"]
    kh = _khoi_co(vb, vi, m.start(), co) if co else None
    a, b = kh if kh else (vi, m.start())
    doan = vb[a:b]
    mg = _gan_cuoi(doan, gia)
    if not mg or not re.fullmatch(
            r"SymbolInfoDouble\(\s*_Symbol\s*,\s*SYMBOL_(ASK|BID)\s*\)",
            mg.group(1).strip()):
        return None, ["gia vao lenh khong phai ASK/BID hien tai - SL/TP chua dich"]
    ms, mt = _gan_cuoi(doan, sl), _gan_cuoi(doan, tp)
    if not ms:
        return None, ["khong tim thay phep gan SL trong nhanh - SL/TP chua dich"]
    sl_bt = ms.group(1).strip()
    if not re.fullmatch(_TEN, sl_bt):
        return None, [f"SL `{sl_bt[:40]}` khong phai mot muc gia - chua dich"]
    t_sl = _toan_hang(sl_bt, a + ms.start(), bang_cb, bang_bl)
    if not _muc_dong(t_sl):
        return None, [f"SL `{sl_bt}` khong dich duoc thanh muc co dinh trong bar"]
    he_tp = None
    if mt:
        bt = re.sub(r"\s+", "", mt.group(1))
        g, x = re.escape(gia), re.escape(sl_bt)
        mm = re.fullmatch(rf"\(*{g}([+-])\(*\(({g}-{x}|{x}-{g})\)\*(\w+(?:\.\d+)?)\)*", bt)
        if not mm:
            return None, [f"TP `{mt.group(1).strip()[:50]}` khong dang gia+-(gia-SL)*k"]
        dau, hieu, k = mm.group(1), mm.group(2), mm.group(3)
        kv = float(k) if re.fullmatch(_SO, k) else hang.get(k)
        dung = (dau == "+" and hieu.startswith(gia)) if chieu > 0 else \
            (dau == "-" and hieu.startswith(sl_bt))
        if kv is None or not dung or kv <= 0:
            return None, [f"TP `{bt[:50]}` sai chieu hoac he so khong ro"]
        he_tp = float(kv)
    elif tp not in ("NULL", "0", "0.0"):
        return None, ["khong tim thay phep gan TP - SL/TP chua dich"]
    khoi = {"sl": t_sl, "tp": he_tp, "keo": None}
    keo = _keo_sl_mql(vb, chieu, bang_cb, bang_bl)
    if keo is not None:
        khoi["keo"] = keo
        ghi.append("keo SL moi bar theo `" + json.dumps(keo, ensure_ascii=False)[:80]
                   + "` (chi siet, bo neu SL moi vuot gia hien tai)")
    ghi.insert(0, f"SL = muc `{sl_bt}` luc vao; TP = "
               + (f"gia_vao {'+' if chieu > 0 else '-'} |gia_vao - SL| x {he_tp:g}"
                  if he_tp else "khong") + "; khong dong theo thoi gian (EA khong co)")
    return khoi, ghi


def _keo_sl_mql(vb: str, chieu: int, bang_cb: list, bang_bl: list) -> dict | None:
    """`sl = MathMax(sl, X); trade.PositionModify(_Symbol, sl, ...)` trong khoi
    `if(posType==POSITION_TYPE_BUY)` (MathMin cho SELL), voi `sl` doc tu
    POSITION_SL, trong ham duoc goi tu OnTick. X phai co dinh trong bar."""
    loai, ham = ("BUY", "MathMax") if chieu > 0 else ("SELL", "MathMin")
    for mk in re.finditer(r"\bPositionModify[ \t]*\(", vb):
        goc, ten = _dau_ham(vb, mk.start())
        if not ten or ten == "OnTick":
            continue
        ontick = re.search(r"\bvoid[ \t]+OnTick[ \t]*\([^)]*\)\s*\{", vb)
        if not ontick:
            return None
        het_tick = _cuoi_khoi(vb, ontick.end() - 1)
        if not re.search(rf"\b{re.escape(ten)}[ \t]*\(", vb[ontick.end():het_tick]):
            continue
        het = _cuoi_khoi(vb, goc)
        for mb in re.finditer(rf"\bif[ \t]*\([ \t]*\w+[ \t]*==[ \t]*POSITION_TYPE_{loai}"
                              r"[ \t]*\)\s*\{", vb[goc:het]):
            a = goc + mb.end() - 1
            b = _cuoi_khoi(vb, a)
            than = vb[a:b]
            mm = re.search(rf"\b(\w+)[ \t]*=[ \t]*{ham}[ \t]*\([ \t]*\1[ \t]*,[ \t]*(\w+)"
                           r"[ \t]*\)[ \t]*;", than)
            if not mm or not re.search(rf"PositionModify\([^,]+,[ \t]*{mm.group(1)}\b", than):
                continue
            sl = mm.group(1)
            if not re.search(rf"\b{sl}[ \t]*=[ \t]*PositionGetDouble\(\s*POSITION_SL\s*\)",
                             vb[goc:a]):
                continue
            t = _toan_hang(mm.group(2), a + mm.start(), bang_cb, bang_bl)
            if _muc_dong(t):
                return t
    return None


def _mot_lenh_ngay_mql(vb: str, m, co: str | None, thoat: list[str]) -> dict | None:
    """`if(a==dt.day or b==dt.day) return;` truoc lenh vao + `a=dt.day;` sau lenh
    vao (trong `if(co)` hoac khong dieu kien) -> khoi `mot_lenh_ngay`."""
    chan = None
    for t in thoat:
        ve = _tach_hoac(_boc_ngoac(t))
        mm = [re.fullmatch(r"(\w+)\s*==\s*(\w+)\.day", x.strip()) for x in ve]
        if mm and all(mm):
            chan = (t, [x.group(1) for x in mm], {x.group(2) for x in mm})
            break
    if chan is None:
        return None
    t, bien, dts = chan
    if len(dts) != 1:
        return None
    dt = dts.pop()
    goc, _ = _dau_ham(vb, m.start())
    het = _cuoi_khoi(vb, goc)
    sau = vb[m.end():het if het > 0 else len(vb)]
    dat = []
    for g in re.finditer(rf"(?:\bif[ \t]*\([ \t]*(\w+)[ \t]*\)\s*)?\b(\w+)[ \t]*=[ \t]*"
                         rf"{dt}\.day[ \t]*;", sau):
        if g.group(2) in bien and (g.group(1) is None or g.group(1) == co):
            dat.append(g.group(2))
    # `dat` co the rong: nhanh nay bi chan nhung khong tu chan ai (vd guard chi
    # co `lastupday==dt.day` -> lenh ban khong dat bien nao).
    return {"nhom": "", "chan_boi": bien, "dat": sorted(set(dat)), "_guard": t}


def _doc_chien_luoc_mql(vb: str, nguon: str, tien_to: str) -> dict:
    """Ban MQL5 cua `doc_chien_luoc` - xem chu thich dau lop."""
    global _CHE_DO_MQL
    vb = _chuan_hoa_mql5(vb)
    bang_cb = sorted(_bang_ky_hieu(vb) + _bang_mql(vb), key=lambda x: x[0])
    bang_bl = _bang_bool(vb)
    khai = rut_input(vb)
    hang = _hang_mql(vb)
    ra, ho, n, n_co = [], [], 0, 0
    loai = {"dich_duoc": 0, "ma_chet": 0, "quan_ly_vi_the": 0, "chua_dich": 0}
    cu = _CHE_DO_MQL
    _CHE_DO_MQL = True
    try:
        for m in _VAO_LENH.finditer(vb):
            if m.group("pine"):
                continue
            n += 1
            if _ma_chet(vb, m.start()):
                ho.append("lenh vao la ma chet (sau return vo dieu kien)")
                loai["ma_chet"] += 1
                continue
            doi = m.group("doi_m") or m.group("doi_o") or ""
            if m.group("mql"):
                chieu = -1 if m.group("mql") == "Sell" else 1
            elif re.search(r"ORDER_TYPE_SELL\b", doi):
                chieu = -1
            elif re.search(r"ORDER_TYPE_BUY\b", doi):
                chieu = 1
            else:
                chieu = 0                     # chieu nam o bien `type`
            ifs, gap_else = _cac_if_bao(vb, m.start())
            ifs = [(p, g) for p, g in ifs if not _LA_KIEM_LOI.search(g)]
            vi_the = any(_phu_thuoc_vi_the(g, p, bang_bl) for p, g in ifs)
            loai_hong = "quan_ly_vi_the" if vi_the else "chua_dich"
            if gap_else:
                ho.append("lenh vao nam trong nhanh else")
                loai[loai_hong] += 1
                continue
            nhom = []                         # [(chieu, [guard...], vi_tri)]
            if ifs:
                guards = [g for _, g in ifs]
                vi = min(p for p, _ in ifs)
                if chieu == 0:
                    # `if(up or down){ if(up){type=BUY} if(down){type=SELL} ... }`
                    tach = None
                    for p, g in ifs:
                        hh = _tach_hoac(_boc_ngoac(g))
                        if len(hh) > 1 and all(re.fullmatch(_TEN, x) for x in hh):
                            cc = [_chieu_nhanh(vb, p, m.start(), x) for x in hh]
                            if all(c is not None for c in cc):
                                tach = (g, hh, cc)
                                break
                    if tach is None:
                        ho.append("khong xac dinh duoc chieu lenh: " + guards[0][:50])
                        loai[loai_hong] += 1
                        continue
                    g0, hh, cc = tach
                    con_lai = [g for g in guards if g is not g0]
                    for x, c in zip(hh, cc):
                        nhom.append((c, [x] + con_lai, vi))
                else:
                    nhom.append((chieu, guards, vi))
            else:
                ten_ham = _ham_bao(vb, m.start())
                th = _ham_tin_hieu(vb, ten_ham, chieu, m.start()) if ten_ham else None
                if th is None:
                    ho.append("khong tim duoc guard cua lenh vao")
                    loai[loai_hong] += 1
                    continue
                g, vi, thoat0 = th
                nhom.append((chieu, [g], vi, thoat0))
            co = False
            bat_dau = len(ra)
            for mu in nhom:
                c, guards, vi = mu[0], mu[1], mu[2]
                goc, _ = _dau_ham(vb, vi)
                thoat = (mu[3] if len(mu) > 3 else []) + _thoat_som(vb, goc, vi)
                dk, h, qt = [], [], []
                for g in guards:
                    d2, h2 = _no_dieu_kien(g, vi, bang_cb, bang_bl)
                    if h2 and _la_quan_tri(g):
                        qt.append(g[:60])
                        continue
                    dk += d2
                    h += h2
                co_nhanh = guards[0] if re.fullmatch(_TEN, guards[0]) else None
                for t in thoat:
                    ve = _tach_va(t)
                    loc_co = False
                    if co_nhanh and len(ve) >= 2 and co_nhanh in ve:
                        phan = " and ".join(x for x in ve if x != co_nhanh)
                        loc_co = True             # `if(co && x) return;` = LOC cua co
                    elif any(re.fullmatch(_TEN, x) and x != co_nhanh and
                             any(x == y for y in _cac_co(guards, nhom)) for x in ve):
                        continue                  # loc cua NHANH KIA
                    else:
                        phan = t
                    pd_ = _phu_dinh(phan, vi, bang_cb, bang_bl)
                    if pd_ is not None:
                        dk += [dict(x, _loc=1) for x in pd_] if loc_co else pd_
                    elif _la_quan_tri(phan):
                        qt.append(t[:60])
                    else:
                        h.append("loc thoat som: " + t[:50])
                if h or not dk:
                    ho += h or ["guard rong sau khi dich"]
                    continue
                dk = _bo_trung_dieu_kien(dk)
                # chi so cac dieu kien LOC gan voi co nhanh (xem `_ap_moi_tick`)
                loc_idx = [k for k, d in enumerate(dk) if d.get("_loc")]
                dk = [{k: v for k, v in d.items() if k != "_loc"} for d in dk]
                loai_b0 = [_loai_bar0(d) for d in dk]
                dk = [_bo_bar0(d) for d in dk]
                ho_cc = _ho_cua(dk[0])
                if ho_cc == "khac":
                    ho_cc = _ho_gia_thuan(dk, c) or "khac"
                gia_dinh = []
                if _co_pivot_gio(dk):
                    gia_dinh.append("pivot gio (MultiPivots.mqh) = (H+L+C)/3 cua thanh "
                                    "H1 vua dong (bar i): dung khi chay tren du lieu H1")
                co = True
                ten = f"{tien_to}_{'mua' if c == 1 else 'ban'}_" + "_va_".join(
                    f"{_ten_toan_hang(d['trai'])}_{_TEN_PHEP.get(d['phep'], 'bang')}"
                    f"_{_ten_toan_hang(d['phai'])}" for d in dk[:3])
                ra.append({
                    "ten": ten[:60], "ho": ho_cc, "chieu": c, "giu": 1,
                    "co_che": (
                        f"Chien luoc THAT rut tu lenh vao MQL5: vao lenh khi "
                        f"{len(dk)} dieu kien cung dung (`{' and '.join(guards)[:70]}`)."
                        f" Phoi nhiem duoc tra tien khi ben doi ung buoc phai giao "
                        f"dich o dung trang thai nay - gia thuyet kiem chinh dieu do."),
                    "vao": dk, "nguon": nguon,
                    "luoi_goc": {k: v for d in dk
                                 for k, v in _luoi_tu_dieu_kien(d, khai).items()},
                    "so_dieu_kien": len(dk),
                    "bo_qua_quan_tri": sorted(set(qt)),
                })
                # SL/TP, keo SL, mot lenh mot ngay (them 10/10/2026 dem)
                sltp, ghi = _sltp_mql(vb, m, c, co_nhanh, vi, bang_cb, bang_bl, hang)
                if sltp is not None:
                    ra[-1]["sltp"] = sltp
                gia_dinh += ghi
                mln = _mot_lenh_ngay_mql(vb, m, co_nhanh, thoat)
                if mln is not None:
                    g_ = mln.pop("_guard")
                    mln["nhom"] = f"{nguon}@{m.start()}"
                    ra[-1]["mot_lenh_ngay"] = mln
                    ra[-1]["bo_qua_quan_tri"] = [x for x in ra[-1]["bo_qua_quan_tri"]
                                                 if x != g_[:60]]
                    gia_dinh.append(
                        "mot lenh/ngay: chan khi ngay-trong-thang cua bar = "
                        + "/".join(mln["chan_boi"]) + "; lenh nay dat "
                        + "/".join(mln["dat"]) + " (mo phong chung ca nhom mua+ban, "
                        "mot vi the mot luc)")
                if gia_dinh:
                    ra[-1]["gia_dinh"] = gia_dinh
                ra[-1]["_loai_b0"] = loai_b0
                ra[-1]["_loc"] = loc_idx
            _ap_moi_tick(ra[bat_dau:], _kiem_moi_tick(vb, m.start()))
            n_co += co
            if co:
                loai["dich_duoc"] += 1
            else:
                loai[loai_hong] += 1
    finally:
        _CHE_DO_MQL = cu
    # token gia song chi dung noi bo: van ban bao cao doc lai la `close`
    ho = [x.replace(_GIA0, "close") for x in ho]
    for sp in ra:
        sp["co_che"] = sp["co_che"].replace(_GIA0, "close")
        sp["bo_qua_quan_tri"] = [x.replace(_GIA0, "close") for x in sp["bo_qua_quan_tri"]]
    return {"co_che": ra, "chua_dien_dat_duoc": sorted(set(ho))[:12],
            "so_vao_lenh": n, "so_vao_lenh_co_co_che": n_co,
            # PHAN LOAI moi diem vao (them 10/10/2026) - xem `mau_thu/do_moc.py`:
            # dich_duoc | ma_chet (sau return vo dieu kien) | quan_ly_vi_the
            # (hedge/luoi/nhoi lenh theo gia vao lenh, so lenh, loi lo) | chua_dich.
            "phan_loai_vao_lenh": loai}


def _cac_co(guards: list, nhom: list) -> list[str]:
    """Moi co nhanh (ten don) cua cac nhanh trong cung lenh vao."""
    return [mu[1][0] for mu in nhom if re.fullmatch(_TEN, mu[1][0])]


def doc_chien_luoc(vb: str, nguon: str = "", tien_to: str = "ma") -> dict:
    """CHIEN LUOC THAT: lan tu `strategy.entry` nguoc ve dieu kien vao.

    Vi sao ham nay ton tai rieng voi `doc_ma`: ban dau bo doc nhat MOI phep so
    sanh trong file, ke ca nhung phep chi dung de VE hay to mau. Ty le rut thi
    cao nhung SAI - Sonic R ra 8 "kieu danh" trong khi ban goc vao lenh khi
    xu huong dung VA gia hoi ve dai VA nen xac nhan. Tam mau roi khong phai ba
    dieu kien ghep: chung kich hoat o nhung luc khac han nhau.

    O day di dung duong cua chuong trinh: tim `strategy.entry`, lay guard cua no
    (`when = ...` hoac khoi `if (...)` bao ngoai), no bien ra toi khi cham day la
    phep so sanh, roi ghep TAT CA lam mot co che.

    Va neu MOT ve khong dich duoc thi BO CA CO CHE, khong bo rieng ve do: bo mot
    ve lam dieu kien LONG hon ban goc - nhieu lenh hon, hanh vi khac - ma van
    mang ten cua tac gia. Do la noi doi. Ve khong dich duoc duoc bao ra o
    `chua_dien_dat_duoc` de biet ngu phap con thieu gi.
    """
    vb = _chuan_hoa(vb)

    if not vb or not _VAO_LENH.search(vb):
        return {"co_che": [], "chua_dien_dat_duoc": [], "so_vao_lenh": 0}
    if _la_mql(vb):
        return _doc_chien_luoc_mql(vb, nguon, tien_to)
    bang_cb = _bang_ky_hieu(vb)
    bang_bl = _bang_bool(vb)
    khai = rut_input(vb)
    L = vb.splitlines(keepends=True)
    dau_dong = []
    p = 0
    for l in L:
        dau_dong.append(p)
        p += len(l)

    ra, ho, n = [], [], 0
    for m in _VAO_LENH.finditer(vb):
        n += 1
        doi = m.group("doi_p") or m.group("doi_m") or m.group("doi_o") or ""
        if m.group("mql"):
            # MQL5: chieu nam trong TEN HAM, khong nam trong doi so
            chieu = -1 if m.group("mql") == "Sell" else 1
        elif m.group("ham"):
            chieu = -1 if re.search(r"ORDER_TYPE_SELL|\bSELL\b", doi) else 1
        else:
            chieu = -1 if ("strategy.short" in doi
                           or re.search(r",\s*false", doi)) else 1
        guard, vi = None, m.start()
        mw = re.search(r"when\s*=\s*([^,)\n]+)", doi)
        if mw:
            guard = mw.group(1).strip()
        else:
            # lui tim khoi `if (...)` gan nhat phia tren
            i = max(k for k, x in enumerate(dau_dong) if x <= m.start())
            # Cua so 12 dong la du cho Pine (guard sat lenh) nhung KHONG du cho
            # MQL5: giua `if(dieu_kien)` va `trade.Buy()` thuong con tinh lot,
            # SL, TP - do 05/09 thay khoang cach den 30+ dong.
            for j in range(i, max(-1, i - 40), -1):
                # MQL5 hay viet `if(dk) {` tren MOT dong; ban cu doi dong
                # `if` phai ket thuc KHONG co `{` nen truot het file .mq5.
                mi = re.match(r"^[ \t]*if[ \t]*\(?(.+?)\)?[ \t]*\{?[ \t]*$",
                              L[j].rstrip())
                if mi:
                    ung = mi.group(1).strip()
                    # BO QUA `if` la KIEM LOI cua chinh lenh vao. MQL5 viet
                    # `if(!trade.Buy(...))` hoac `if(!OrderSend(req,res))` -
                    # do la xu ly that bai, khong phai dieu kien vao. Lay no
                    # lam guard thi co che sinh ra la `!OrderSend(request,
                    # result)`, vo nghia. Do 05/09: day la ly do hang dau
                    # khien 113 file nhan ra lenh vao ma 0 file ra co che.
                    if _LA_KIEM_LOI.search(ung):
                        continue
                    guard, vi = ung, dau_dong[j]
                    break
        # LAN QUA RANH GIOI HAM. Guard sat lenh chi noi dang di nhanh nao;
        # dieu kien chien luoc nam o cho GOI ham bao lenh vao.
        if guard is None or _LA_PHAN_NHANH.search(guard):
            ten_ham = _ham_bao(vb, m.start())
            tim_duoc = None
            if ten_ham:
                for vt in _cho_goi(vb, ten_ham, m.start())[:6]:
                    k = max(kk for kk, xx in enumerate(dau_dong) if xx <= vt)
                    for j in range(k, max(-1, k - 25), -1):
                        mi2 = re.match(
                            r"^[ \t]*if[ \t]*\(?(.+?)\)?[ \t]*\{?[ \t]*$",
                            L[j].rstrip())
                        if not mi2:
                            continue
                        g2 = mi2.group(1).strip()
                        if _LA_KIEM_LOI.search(g2) or _LA_PHAN_NHANH.search(g2):
                            continue
                        tim_duoc, vi = g2, dau_dong[j]
                        break
                    if tim_duoc:
                        break
            if tim_duoc:
                guard = tim_duoc
        if not guard:
            ho.append("khong tim duoc guard cua lenh vao")
            continue
        dk, h = _no_dieu_kien(guard, vi, bang_cb, bang_bl)
        if h or not dk:
            ho += h or ["guard rong sau khi dich"]
            continue                    # BO CA CO CHE, khong bo rieng ve
        ten = f"{tien_to}_{'mua' if chieu == 1 else 'ban'}_" + "_va_".join(
            f"{_ten_toan_hang(d['trai'])}_{_TEN_PHEP[d['phep']]}_{_ten_toan_hang(d['phai'])}"
            for d in dk[:3])
        ra.append({
            "ten": ten[:60], "ho": _ho_cua(dk[0]), "chieu": chieu, "giu": 1,
            "co_che": (
                f"Chien luoc THAT rut tu `strategy.entry`: vao lenh khi "
                f"{len(dk)} dieu kien cung dung (`{guard[:70]}`). Phoi nhiem duoc "
                f"tra tien khi ben doi ung buoc phai giao dich o dung trang thai "
                f"nay - gia thuyet kiem chinh dieu do."),
            "vao": dk, "nguon": nguon,
            "luoi_goc": {k: v for d in dk
                         for k, v in _luoi_tu_dieu_kien(d, khai).items()},
            "so_dieu_kien": len(dk),
        })
    return {"co_che": ra, "chua_dien_dat_duoc": sorted(set(ho))[:12],
            "so_vao_lenh": n}


def doc_ma(vb: str, ngon_ngu: str = "tu_doan", nguon: str = "",
           tien_to: str = "ma", toi_da: int = 12) -> list[dict]:
    """Mot file ma -> NHIEU khai bao co che theo `nhan/ngu_phap.py`.

    Tra `[]` khi khong dich duoc dieu kien nao - do la ket qua binh thuong va
    pho bien (mot file tien ich quan ly lenh khong co dieu kien vao nao ca).
    """
    vb = _chuan_hoa(vb)

    if not vb:
        return []
    bang = _bang_ky_hieu(vb)
    khai = rut_input(vb)
    ra = []
    for dk in _dieu_kien(vb, bang)[:toi_da]:
        trich = dk.pop("_trich", "")
        ho = _ho_cua(dk)
        # KHONG sinh co che ho `khac`. Day khong phai bo loc chat lam canh: luat
        # cua du an la moi ho phai khai duoc PHAM VI ("chay o lop tai san nao,
        # hong o lop nao, vi sao") - xem `nhan/pham_vi.py` va bai kiem
        # `test_moi_khai_bao_deu_co_ly_do_co_che`. Mot dieu kien nhu
        # `close > open` khong goi ten duoc co che kinh te nao, nen khong co co
        # so de doi hoi mot phep thu phan chung cho no. Dat ten duoc ho truoc da.
        if ho == "khac":
            continue
        ten = f"{tien_to}_{_ten_toan_hang(dk['trai'])}_{_TEN_PHEP[dk['phep']]}_{_ten_toan_hang(dk['phai'])}"
        ra.append({
            "ten": ten[:60],
            "ho": ho,
            "chieu": 1,
            "giu": 1,
            "co_che": (
                f"Rut tu ma nguon that: dieu kien `{trich}`. Phoi nhiem duoc tra "
                f"tien khi ben doi ung buoc phai giao dich o dung trang thai nay - "
                f"gia thuyet nay kiem chinh dieu do, khong kiem cai bot goc."),
            "vao": [dk],
            "nguon": nguon,
            # MIEN QUET CUA CHINH TAC GIA (them 01/09). Khong chay mot dong ma
            # nao cua ho: `input(34, minval=2, maxval=200)` da noi ro bien nay
            # chay trong khoang nao. Tang kham pha lay day lam DIEM NEO thay vi
            # mot luoi ta tu bia.
            "luoi_goc": _luoi_tu_dieu_kien(dk, khai),
        })
    return ra
