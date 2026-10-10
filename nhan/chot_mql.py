# -*- coding: utf-8 -*-
"""CHOT CAP MQL5 - hai co `static int` nho qua nhieu bar, TIEU THU khi vao lenh.

Them 11/10/2026 (vong "trang thai lop / co static"). Dang EA (016_CCI_2MAVG):

    static int MACross = 0, CCICross = 0;
    if(newBar) {                               // NewBar(): static datetime + iTime(..,0)
       if(CCI1>0 && CCI2<=0) CCICross =  1;    // su kien B
       if(CCI1<0 && CCI2>=0) CCICross = -1;
       if(f1>s1 && f2<=s2) { MACross =  1; CloseTrades(POSITION_TYPE_SELL); }
       if(f1<s1 && f2>=s2) { MACross = -1; CloseTrades(POSITION_TYPE_BUY);  }
       if(MACross!=0 && MACross==CCICross)
          if(OpenTrade(MACross)>0) { MACross = 0; CCICross = 0; }
    }
    bool OpenTrade(int x){ if(x<0) return PositionOpen(..SELL..); if(x>0) return PositionOpen(..BUY..); }

May trang thai CHUNG MINH DUOC tu ma (khong doan): moi bar chay cac phep gan theo
thu tu ma, roi vao lenh khi a != 0 va a == b, xong reset ca hai. Tin hieu chi phu
thuoc lich su chi bao (lenh luon duoc gui khi dieu kien dung, khong phu thuoc vi
the) -> toan tu DSL `chot_cap` (`nhan/ngu_phap.py`). Lenh dong `CloseTrades(TYPE)`
trong khoi su kien -> dieu kien `ra` cua chan cung loai.

Chi nhan khi MOI dieu duoi day kiem duoc tren ma; thieu mot dieu -> tu choi CO LY DO
(khong roi ve duong doc cu, vi duong cu se dich SAI: bo qua co):
  - ham lenh vao F(int p) chi re nhanh `if(p<0)` / `if(p>0)` (p khong dung cho khac);
  - F duoc goi DUNG MOT cho, dang `if(F(A)>0){A=0;B=0;}` (hoac `if(F(A))`), khong else;
  - khoi goi nam trong `if(A!=0 && A==B)` va cong bar moi DA KIEM (ham static datetime);
  - A, B la `static int X = 0;` trong cung ham; moi phep gan khac la `X = +-1;` trong
    MOT `if(su kien)` (cung cong bar moi, truoc khoi kiem); khong dung A/B o cho khac;
  - doan ma tu cong toi het khoi kiem khong co for/while/switch/else/return;
  - dieu kien su kien dich duoc DAY DU va chi doc bar da dong (khong bar 0 song).
Ve luon dung do loi EA (`fastMA2 = MAVG2_Buffer[2]` -> `s2 <= s2`) bi BO, co ghi lai.
"""
from __future__ import annotations

import copy
import json
import re

_TEN = r"[A-Za-z_][A-Za-z0-9_]*"
_CAM = re.compile(r"\b(?:for|while|switch|do|else|case|goto|return|break|continue)\b")


def _D():
    from nhan import doc_ma as D                  # tre: tranh vong import
    return D


def _gon(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _than(vb: str, mo: int) -> tuple[int, int] | None:
    e = _D()._cuoi_khoi(vb, mo)
    return (mo, e) if e > 0 else None


def _la_ham_bar_moi(vb: str, ten: str) -> bool:
    """`bool NB(){ static datetime c=0; datetime n=iTime(Sym,Per,0); if(n==c) return(false);
    c=n; return(true); }` (thu tu so sanh, ngoac return tuy y)."""
    mh = re.search(rf"\bbool[ \t]+{re.escape(ten)}[ \t]*\([ \t]*\)\s*\{{", vb)
    if not mh:
        return False
    k = _than(vb, mh.end() - 1)
    if k is None:
        return False
    g = _gon(vb[k[0] + 1:k[1]])
    m = re.fullmatch(
        rf"staticdatetime({_TEN})=0;datetime({_TEN})=iTime\([^()]*(?:\([^()]*\))?[^()]*"
        rf"(?:\([^()]*\))?[^()]*,0\);if\((\w+)==(\w+)\)return\(?false\)?;(\w+)=(\w+);"
        rf"return\(?true\)?;", g)
    if not m:
        return False
    c, n = m.group(1), m.group(2)
    return {m.group(3), m.group(4)} == {c, n} and m.group(5) == c and m.group(6) == n


def _ham_dong_loai(vb: str, ten: str) -> bool:
    """`bool Close(ENUM_POSITION_TYPE t)`: duyet PositionsTotal, chi PositionClose khi
    loai vi the == t; t khong dung o cho khac."""
    mh = re.search(rf"\b(?:bool|void|int)[ \t]+{re.escape(ten)}[ \t]*\([ \t]*"
                   rf"ENUM_POSITION_TYPE[ \t]+({_TEN})[ \t]*\)\s*\{{", vb)
    if not mh:
        return False
    k = _than(vb, mh.end() - 1)
    if k is None:
        return False
    t = mh.group(1)
    than = vb[k[0] + 1:k[1]]
    if "PositionsTotal()" not in than or len(re.findall(r"PositionClose\(", than)) != 1:
        return False
    rx = (rf"if[ \t]*\([ \t]*(?:\w+\.PositionType\(\)|\(?ENUM_POSITION_TYPE\)?[ \t]*"
          rf"PositionGetInteger\(POSITION_TYPE\)|PositionGetInteger\(POSITION_TYPE\))"
          rf"[ \t]*==[ \t]*{t}[ \t]*\)\s*\{{?\s*\w+[ \t]*&?=[ \t]*\w+\.PositionClose\(|"
          rf"if[ \t]*\([ \t]*(?:\w+\.PositionType\(\)|PositionGetInteger\(POSITION_TYPE\))"
          rf"[ \t]*==[ \t]*{t}[ \t]*\)\s*\{{?\s*(?:\w+\.)?PositionClose\(")
    if len(re.findall(rf"\b{t}\b", than)) != 1 or not re.search(rx, than):
        return False
    return True


def _hang_co_dinh(x):
    """Hang so CUNG trong ma (`CCI1>0`) khong phai input -> khong toi uu."""
    if isinstance(x, dict):
        if set(x) == {"hang"}:
            return {"hang_co_dinh": x["hang"]}
        return {k: _hang_co_dinh(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_hang_co_dinh(v) for v in x]
    return x


def _dich_su_kien(g: str, vi: int, bang_cb: list, bang_bl: list) -> tuple[list | None, list, str]:
    """Guard su kien -> (dieu kien DSL | None, ghi chu, ly do tu choi)."""
    D = _D()
    dk, h = D._no_dieu_kien(g, vi, bang_cb, bang_bl)
    if h:
        return None, [], "chot: su kien khong dich duoc: " + "; ".join(h)[:60]
    ghi, ra = [], []
    for d in dk:
        if D._co_bar0(d.get("trai")) or D._co_bar0(d.get("phai")):
            return None, [], "chot: su kien doc bar 0 song (`" + g[:40] + "`)"
        a = json.dumps(d.get("trai"), sort_keys=True)
        b = json.dumps(d.get("phai"), sort_keys=True)
        if a == b:
            if d.get("phep") in ("<=", ">=", "=="):
                ghi.append(f"ve LUON DUNG `{g[:60]}` (hai ve giong het - loi trong ma EA) "
                           "-> bo, su kien chi con cac ve con lai")
                continue
            return None, [], "chot: su kien co ve LUON SAI (`" + g[:40] + "`)"
        ra.append(d)
    if not ra:
        return None, [], "chot: su kien rong sau khi bo ve luon dung"
    return _hang_co_dinh(ra), ghi, ""


def doc_chot(vb: str, vi: int, chieu: int, bang_cb: list, bang_bl: list) -> dict | None:
    """Lenh vao tai `vi` (chieu +1/-1) co nam trong may CHOT CAP khong.

    None = khong phai dang nay (de duong doc cu xu ly). {"loi": ly_do} = dung dang
    (ham F(int) re nhanh theo dau, goi trong `if(A!=0 && A==B)`) nhung khong chung
    minh du -> tu choi. Nguoc lai: {"vao", "ra", "gia_dinh", "bo_qua_quan_tri", "guard"}.
    """
    D = _D()
    goc_f, F = D._dau_ham(vb, vi)
    if not F:
        return None
    ms = re.search(rf"\b(?:bool|int|ulong|long)[ \t]+{re.escape(F)}[ \t]*\([ \t]*int[ \t]+"
                   rf"({_TEN})[ \t]*\)\s*\{{", vb)
    if not ms:
        return None
    p = ms.group(1)
    ifs_f, ge_f = D._cac_if_bao(vb, vi)
    if len(ifs_f) != 1 or ge_f:
        return None
    mg = re.fullmatch(rf"\s*{p}\s*([<>])\s*0\s*", ifs_f[0][1])
    if not mg:
        return None
    goi = D._cho_goi(vb, F, ms.start())
    goi = [c for c in goi if D._dau_ham(vb, c)[1] != F]
    if len(goi) != 1:
        return None
    c = goi[0]
    mc = re.match(rf"{re.escape(F)}[ \t]*\([ \t]*({_TEN})[ \t]*\)[ \t]*(?:>[ \t]*0[ \t]*)?\)\s*\{{",
                  vb[c:])
    if not mc or not re.search(r"\bif[ \t]*\([ \t]*$", vb[max(0, c - 40):c]):
        return None
    A = mc.group(1)
    ifs_c, ge_c = D._cac_if_bao(vb, c)
    if not ifs_c:
        return None
    ve = {_gon(x) for x in D._tach_va(D._boc_ngoac(ifs_c[0][1]))}
    B = None
    for x in ve:
        mm = re.fullmatch(rf"(?:{A}=={_TEN}|{_TEN}=={A})", x)
        if mm:
            B = [y for y in x.split("==") if y != A]
            B = B[0] if len(B) == 1 else None
    if B is None or ve != {f"{A}!=0", f"{A}=={B}"} and ve != {f"{A}!=0", f"{B}=={A}"}:
        return None
    # --- tu day: DUNG DANG -> moi thieu sot la tu choi co ly do ---
    s_ham = 1 if mg.group(1) == ">" else -1
    if s_ham != chieu:
        return {"loi": f"chot: chieu lenh trai voi nhanh `{p}{mg.group(1)}0` cua {F}"}
    k_f = _than(vb, ms.end() - 1)
    if k_f is None or len(re.findall(rf"\b{p}\b", vb[k_f[0]:k_f[1]])) != \
            len(re.findall(rf"\bif[ \t]*\([ \t]*{p}[ \t]*[<>][ \t]*0[ \t]*\)", vb[k_f[0]:k_f[1]])):
        return {"loi": f"chot: tham so `{p}` cua {F} dung ngoai nhanh dau"}
    if ge_c:
        return {"loi": "chot: khoi goi lenh nam trong nhanh else"}
    b0 = c + mc.end() - 1
    k_r = _than(vb, b0)
    if k_r is None:
        return {"loi": "chot: khong dong duoc khoi reset"}
    lenh = sorted(_gon(x) for x in vb[k_r[0] + 1:k_r[1]].split(";") if x.strip())
    if lenh != sorted([f"{A}=0", f"{B}=0"]):
        return {"loi": "chot: khoi sau lenh vao khong chi la reset hai co"}
    if re.match(r"\s*else\b", vb[k_r[1] + 1:]):
        return {"loi": "chot: khoi reset co else"}
    goc_g, G = D._dau_ham(vb, c)
    k_g = _than(vb, goc_g)
    if G is None or k_g is None:
        return {"loi": "chot: khong xac dinh duoc ham goi"}
    than_g = vb[k_g[0]:k_g[1]]
    for X in (A, B):
        if len(re.findall(rf"\bstatic[ \t]+int[ \t]+{X}[ \t]*=[ \t]*0[ \t]*;", than_g)) != 1:
            return {"loi": f"chot: `{X}` khong phai `static int {X} = 0;` trong {G}"}
    # cong bar moi
    cong = [g for _, g in ifs_c[1:]]
    if not cong:
        return {"loi": "chot: khong co cong bar moi quanh khoi kiem (EA chay moi tick)"}
    for g in cong:
        g_ = _gon(g)
        mn = re.fullmatch(rf"({_TEN})\(\)", g_)
        if mn and _la_ham_bar_moi(vb, mn.group(1)):
            continue
        if re.fullmatch(_TEN, g_):
            gan = re.findall(rf"\b{g_}[ \t]*=(?!=)[ \t]*([^;]*);", than_g)
            if len(gan) == 1 and re.fullmatch(rf"\s*({_TEN})\(\)\s*", gan[0]) and \
                    _la_ham_bar_moi(vb, gan[0].strip()[:-2]):
                continue
        return {"loi": f"chot: guard ngoai `{g[:30]}` khong phai cong bar moi da kiem"}
    # thoat som truoc khoi goi: chi quan tri
    qt = []
    for t in D._thoat_som(vb, goc_g, c):
        if D._la_quan_tri(t) or re.search(r"TerminalInfoInteger|MQLInfoInteger|IsStopped", t):
            qt.append(t[:60])
        else:
            return {"loi": "chot: thoat som khong phai quan tri: " + t[:40]}
    # doan tu cong toi het khoi kiem: khong vong lap / nhanh khac
    p_cong = min(pp for pp, _ in ifs_c[1:])
    k_kiem = _than(vb, vb.find("{", ifs_c[0][0]))
    if k_kiem is None or _CAM.search(vb[p_cong:k_kiem[1]]):
        return {"loi": "chot: co vong lap / else / return trong khoi bar moi (khong chung minh)"}
    # moi lan dung A/B trong G
    dung = [mm.start() + k_g[0] for mm in re.finditer(rf"\b(?:{A}|{B})\b", than_g)]
    dat, dong = [], {"BUY": [], "SELL": []}
    ghi: list = []
    p_kiem = ifs_c[0][0]
    for q in dung:
        if p_cong <= q < k_kiem[1] and (q in range(ifs_c[0][0], ifs_c[0][0] + len(ifs_c[0][1]) + 2)
                                         or q in range(c, c + mc.end())
                                         or k_r[0] <= q <= k_r[1]):
            continue                              # guard kiem / loi goi / khoi reset
        if re.search(rf"static[ \t]+int[ \t]+$", vb[max(0, q - 14):q]):
            continue                              # khai bao static
        mm = re.match(rf"({A}|{B})[ \t]*=(?!=)[ \t]*([-+]?\s*1)[ \t]*;", vb[q:])
        if not mm:
            return {"loi": f"chot: `{vb[q:q + 20].strip()}` - dung co ngoai mau (khong chung minh)"}
        if not (p_cong <= q < p_kiem):
            return {"loi": "chot: phep gan co nam ngoai doan cong..kiem"}
        ifs_q, ge_q = D._cac_if_bao(vb, q)
        if ge_q or len(ifs_q) != 1 + len(cong) or [g for _, g in ifs_q[1:]] != cong:
            return {"loi": "chot: phep gan co khong nam trong DUNG MOT if su kien (+cong)"}
        dk, g2, ly = _dich_su_kien(ifs_q[0][1], ifs_q[0][0], bang_cb, bang_bl)
        if dk is None:
            return {"loi": ly}
        ghi += g2
        dat.append({"bien": "a" if mm.group(1) == A else "b",
                    "gt": 1 if _gon(mm.group(2)) in ("1", "+1") else -1, "khi": dk})
    for X, ten in ((A, "a"), (B, "b")):
        if not any(d["bien"] == ten for d in dat):
            return {"loi": f"chot: co `{X}` khong bao gio duoc dat +-1"}
    # lenh dong theo loai trong khoi su kien
    for mm in re.finditer(rf"\b({_TEN})[ \t]*\([ \t]*POSITION_TYPE_(BUY|SELL)[ \t]*\)[ \t]*;", than_g):
        q = k_g[0] + mm.start()
        if not _ham_dong_loai(vb, mm.group(1)):
            ghi.append(f"`{mm.group(1)}(POSITION_TYPE_{mm.group(2)})` khong chung minh duoc "
                       "la dong theo loai - lenh dong CHUA dich")
            dong[mm.group(2)].append(None)
            continue
        ifs_q, ge_q = D._cac_if_bao(vb, q)
        if ge_q or len(ifs_q) != 1 + len(cong) or [g for _, g in ifs_q[1:]] != cong \
                or not (p_cong <= q < p_kiem):
            dong[mm.group(2)].append(None)
            continue
        dk, g2, ly = _dich_su_kien(ifs_q[0][1], ifs_q[0][0], bang_cb, bang_bl)
        dong[mm.group(2)].append(dk)
        ghi += g2
    if re.search(r"PositionClose\(", vb) and not dong["BUY"] and not dong["SELL"]:
        ghi.append("co PositionClose ngoai mau chot - lenh dong CHUA dich")
    loai = "BUY" if chieu > 0 else "SELL"
    ra = None
    if len(dong[loai]) == 1 and dong[loai][0] is not None:
        ra = dong[loai][0]
        ghi.append(f"dong lenh {loai} o tick dau bar moi khi su kien dong dung "
                   "(truoc lenh vao cung tick, nhu EA)")
    elif dong[loai]:
        ghi.append(f"lenh dong {loai} khong dich duoc (nhieu cho / khong chung minh)")
    # SL/TP o lenh vao
    mo = re.search(r"\bPositionOpen[ \t]*\(", vb[vi:vi + 200])
    if mo:
        doi = D._tach_doi_so(vb, vi + mo.end() - 1)
        if not doi or len(doi) < 6 or _gon(doi[4]) not in ("0", "0.0") or \
                _gon(doi[5]) not in ("0", "0.0"):
            ra = None
            ghi.append("lenh vao co SL/TP chua dich -> lenh dong chua day du")
    ghi += ["lenh vao luon khop (EA reset hai co khi PositionOpen tra true; lenh bi tu "
            "choi thi co giu nguyen - khong mo phong)",
            "EA mo lenh moi khi chot khop, KHONG gioi han so vi the: mo phong MOT vi the "
            "moi chan - tin hieu khi dang co lenh bi bo (xap xi)",
            "hai MA bang nhau tuyet doi (co giu gia tri cu) bo qua - xac suat ~0 voi so thuc"]
    toan = {"chi_bao": "chot_cap", "dat": dat, "kiem": ["a", "b"]}
    return {"vao": [{"trai": toan, "phep": "==", "phai": {"hang_co_dinh": float(chieu)}}],
            "ra": copy.deepcopy(ra), "gia_dinh": list(dict.fromkeys(ghi)),
            "bo_qua_quan_tri": sorted(set(qt)), "guard": ifs_c[0][1], "ham": F}
