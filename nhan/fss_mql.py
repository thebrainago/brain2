# -*- coding: utf-8 -*-
"""EA SINH TU DONG boi Forex Strategy Studio (FSS) - mau "cay quyet dinh" (them 11/10/2026).

Vi du `mau_thu/mo_rong/forexstrategystudio/EMA Crossover.mq5`. Lenh vao khong co guard
`if(...)` truc tiep: OnTick dung mang phieu `ACTION actions0[] = {booleanToAction(ACTION::BUY,
<dk>), booleanToAction(ACTION::SELL, <dk>)}`, gop bang `actionAverage(actions0, true)` roi
`switch` goi `openPosition(ORDER_TYPE_BUY/SELL, LOTS)` (OrderSend trong ham). Lenh dong la
OrderSend THU HAI (trong `closePosition`, `request.position` = ve dang mo) do
`decideIfClosePosition()` quyet o tick dau moi bar: SL/TP theo PIP so voi GIA KHOP luc vao,
gia hien tai = `iClose(_Symbol,_Period,0)` (BID tick dau), pip = 0.01 neu ten ma co "JPY",
0.1 neu co "BITCOIN", con lai 0.0001 (heuristic THEO TEN MA cua chinh EA - khong phai `_Point`).

Chi nhan khi CHUNG MINH duoc tung manh tren ma (so khop than ham da bo khoang trang/chu
thich voi mau FSS); lech mot manh -> tu choi co ly do. Nhung gi doc duoc:
  - `calcMovingAvg(n, s, Symbol(), Period(), MODE_x, PRICE_CLOSE)`: tao iMA roi
    `CopyBuffer(h, 0, s+1, 1, ..)` -> gia tri cua bar DA DONG s+1 (khong phai bar 0 song).
    Quy uoc DSL: bar 1 = bar i (khong tre), bar s+1 -> `tre s`.
  - Hai phieu BUY/SELL LOAI TRU NHAU (co cap so sanh nghich cung hai ve) -> trung binh =
    phieu duy nhat; khong chung minh duoc loai tru -> tu choi (khi ca hai dung EA ra NEUTRAL).
  - `if(BUY_OPEN || SELL_OPEN){ ...dong...; return; }` -> MOT vi the mot luc cho ca he, tick
    dong lenh khong vao lai; cau hinh `static` (closeType/tpType/slType/tpValue/slValue)
    khong bi gan lai o dau.
Gia dinh ghi ro: Strategy Tester tinh iMA dong bo ngay sau khi tao handle (ngoai doi
CopyBuffer co the tra -1 -> EMPTY_VALUE); lenh/dong luon khop (TRADE_RETCODE_DONE).
"""
from __future__ import annotations

import re

_TEN = r"[A-Za-z_][A-Za-z0-9_]*"
_MA = {"MODE_EMA": "ema", "MODE_SMA": "sma", "MODE_SMMA": "smma", "MODE_LWMA": "wma"}
_DAO = {">": "<", "<": ">", ">=": "<=", "<=": ">="}


def bo_chu_thich(vb: str) -> str:
    """Bo // va /* */ ngoai chuoi ky tu (giu nguyen chuoi "..." va xuong dong)."""
    ra, i, n = [], 0, len(vb)
    while i < n:
        c = vb[i]
        if c == '"':
            j = i + 1
            while j < n and vb[j] != '"' and vb[j] != "\n":
                j += 2 if vb[j] == "\\" else 1
            ra.append(vb[i:j + 1])
            i = j + 1
        elif vb.startswith("//", i):
            j = vb.find("\n", i)
            i = n if j < 0 else j
        elif vb.startswith("/*", i):
            j = vb.find("*/", i + 2)
            k = n if j < 0 else j + 2
            ra.append("\n" * vb.count("\n", i, k))
            i = k
        else:
            ra.append(c)
            i += 1
    return "".join(ra)


def _gon(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _dong(vb: str, mo: int, a: str = "{", b: str = "}") -> int:
    m = 0
    for k in range(mo, len(vb)):
        if vb[k] == a:
            m += 1
        elif vb[k] == b:
            m -= 1
            if m == 0:
                return k
    return -1


def _than_ham(vb: str, kieu: str, ten: str) -> tuple[str, str] | None:
    """(danh sach tham so, than) - da gon khoang trang."""
    m = re.search(rf"^[ \t]*{kieu}[ \t]+{re.escape(ten)}[ \t]*\(", vb, re.M)
    if not m:
        return None
    k = _dong(vb, m.end() - 1, "(", ")")
    a = vb.find("{", k)
    if k < 0 or a < 0 or vb[k + 1:a].strip():
        return None
    e = _dong(vb, a)
    return (_gon(vb[m.end():k]), _gon(vb[a + 1:e])) if e > 0 else None


def _tach_cap(s: str, sep: str) -> list[str]:
    """Tach `s` theo `sep` o muc ngoac 0."""
    ra, sau, cu, i = [], 0, 0, 0
    while i < len(s):
        c = s[i]
        if c in "({[":
            sau += 1
        elif c in ")}]":
            sau -= 1
        elif sau == 0 and s.startswith(sep, i):
            ra.append(s[cu:i])
            i += len(sep)
            cu = i
            continue
        i += 1
    ra.append(s[cu:])
    return ra


def _bo_ngoac(s: str) -> str:
    while s.startswith("(") and _dong(s, 0, "(", ")") == len(s) - 1:
        s = s[1:-1]
    return s


def _ma(s: str) -> dict | str:
    m = re.fullmatch(r"calcMovingAvg\((\d+),(\d+),(?:Symbol\(\)|_Symbol),(?:Period\(\)|_Period|"
                     r"PERIOD_CURRENT),(MODE_\w+),(PRICE_\w+)\)", s)
    if not m:
        return f"fss: ve khong phai calcMovingAvg chuan: `{s[:40]}`"
    if m.group(3) not in _MA:
        return f"fss: phuong phap MA {m.group(3)} chua ho tro"
    if m.group(4) != "PRICE_CLOSE":
        return f"fss: gia ap dung {m.group(4)} chua ho tro"
    t = {"chi_bao": _MA[m.group(3)], "n": int(m.group(1))}
    s_ = int(m.group(2))
    return {"chi_bao": "tre", "cua": t, "n": s_} if s_ > 0 else t


def _dieu_kien(bt: str) -> list | str:
    ra = []
    for ve in _tach_cap(_bo_ngoac(bt), "&&"):
        ve = _bo_ngoac(ve)
        hit = None
        for op in (">=", "<=", ">", "<"):
            p = _tach_cap(ve, op)
            if len(p) == 2:
                hit = (op, p)
                break
        if hit is None or "||" in ve:
            return f"fss: ve khong phai so sanh don: `{ve[:40]}`"
        a, b = _ma(_bo_ngoac(hit[1][0])), _ma(_bo_ngoac(hit[1][1]))
        for x in (a, b):
            if isinstance(x, str):
                return x
        ra.append({"trai": a, "phep": hit[0], "phai": b})
    return ra


def _loai_tru(a: list, b: list) -> bool:
    """Co cap (X op Y) trong a va (X op' Y) / (Y op X) trong b khong cung dung duoc."""
    for d in a:
        for e in b:
            if d["trai"] == e["trai"] and d["phai"] == e["phai"] and \
                    {d["phep"], e["phep"]} in ({">", "<"}, {">", "<="}, {">=", "<"}):
                return True
            if d["trai"] == e["phai"] and d["phai"] == e["trai"] and \
                    e["phep"] == d["phep"] and d["phep"] in (">", "<"):
                return True
    return False


# Than ham mau FSS (da gon khoang trang + bo chu thich) - so khop DUNG.
_THAN = {
    "booleanToAction": "if(inputBool){returnactionIfTrue;}else{returnACTION::NEUTRAL;}",
    "IsSubstringIgnoreCase": "StringToLower(mainString);StringToLower(subString);return("
                             "StringFind(mainString,subString)!=-1);",
    "actionAverage": "intcount=ArraySize(actions);if(count==0)returnACTION::NEUTRAL;int"
                     "validCount=0;doublesum=0.0;for(inti=0;i<count;i++){if(ignoreNeutralSignals"
                     "&&actions[i]==ACTION::NEUTRAL)continue;sum+=(int)actions[i];validCount++;}"
                     "if(validCount==0)returnACTION::NEUTRAL;doubleaverageDouble=sum/validCount;"
                     "intaverageInt=(int)MathRound(averageDouble);returnActionFromValue("
                     "averageInt);",
}
_MANH_CALC = ("intma_handle=iMA((barPart==-1?NULL:currencyPair),(barPart==-1?PERIOD_CURRENT:"
              "timeframe),period,0,maMethod,barPart==-1?handleVolumes:barPart);",
              "if(CopyBuffer(ma_handle,0,shift+1,1,ma_values)!=1){",
              "doubleresult=ma_values[0];IndicatorRelease(ma_handle);")
_MANH_DONG = ("doublecurrentPrice=iClose(_Symbol,_Period,0);boolisBuy=BUY_OPEN;doublediff=("
              "currentPrice-openPrice)*(isBuy?1:-1);stringcurrencyPair=Symbol();double"
              "pipValue=IsSubstringIgnoreCase(currencyPair,\"JPY\")?0.01:IsSubstringIgnoreCase("
              "currencyPair,\"BITCOIN\")?0.1:0.0001;if(diff>0){switch(tpType){",
              "casePIPS:if(diff/pipValue>=tpValue){returnACTION::CLOSE;}break;caseNONE:"
              "default:break;}returnACTION::NOP;}else{switch(slType){",
              "casePIPS:if((-diff/pipValue)>=slValue){returnACTION::CLOSE;}break;caseNONE:"
              "default:break;}returnACTION::NOP;}break;}")
_RX_ONTICK = re.compile(
    r"datetimecurrent_bar_time=iTime\(_Symbol,_Period,0\);if\(current_bar_time==last_bar_time\)"
    r"return;last_bar_time=current_bar_time;if\(BUY_OPEN\|\|SELL_OPEN\)\{ACTIONaction="
    r"decideIfClosePosition\(\);if\(action==ACTION::CLOSE\)\{if\(closePosition\(\)\)\{"
    r"SELL_OPEN=false;BUY_OPEN=false;\}\}return;\}ACTIONactions0\[\]=\{(?P<phieu>.*)\};"
    r"ACTIONaction=actionAverage\(actions0,true\);switch\(action\)\{caseACTION::STRONG_BUY:"
    r"caseACTION::BUY:if\(openPosition\(ORDER_TYPE_BUY,(?P<lot1>\w+)\)\)\{BUY_OPEN=true;\}break;"
    r"caseACTION::STRONG_SELL:caseACTION::SELL:if\(openPosition\(ORDER_TYPE_SELL,(?P<lot2>\w+)"
    r"\)\)\{SELL_OPEN=true;\}break;default:break;\}")


def la_fss(vb_tho: str) -> bool:
    return bool(re.search(r"\bactionAverage[ \t]*\(", vb_tho)) and \
        bool(re.search(r"\bdecideIfClosePosition[ \t]*\(", vb_tho)) and \
        bool(re.search(r"\bopenPosition[ \t]*\(", vb_tho))


def doc_fss(vb_tho: str) -> dict:
    """{"co_che": [mua, ban], "gia_dinh": [...]} hoac {"loi": ly_do}."""
    vb = bo_chu_thich(vb_tho)
    for ten, mau in _THAN.items():
        kieu = "bool" if ten == "IsSubstringIgnoreCase" else "ACTION"
        th = _than_ham(vb, kieu, ten)
        if th is None or th[1] != mau:
            return {"loi": f"fss: than ham {ten} khac mau (khong chung minh)"}
    th = _than_ham(vb, "ACTION", "ActionFromValue")
    if th is None or not all(x in th[1] for x in ("case2:returnSTRONG_BUY;", "case1:returnBUY;",
                                                   "case0:returnNEUTRAL;", "case-1:returnSELL;",
                                                   "case-2:returnSTRONG_SELL;")):
        return {"loi": "fss: ActionFromValue khac mau"}
    en = re.search(r"enum[ \t]+ACTION[ \t]*\{([^}]*)\}", vb)
    if not en or not all(x in _gon(en.group(1)) for x in ("STRONG_BUY=2", "BUY=1", "NEUTRAL=0",
                                                          "SELL=-1", "STRONG_SELL=-2")):
        return {"loi": "fss: enum ACTION khac mau"}
    th = _than_ham(vb, "double", "calcMovingAvg")
    if th is None or th[0] != ("intperiod,intshift,stringcurrencyPair,ENUM_TIMEFRAMEStimeframe,"
                               "ENUM_MA_METHODmaMethod,intbarPart") or \
            not all(x in th[1] for x in _MANH_CALC) or not th[1].endswith("returnresult;"):
        return {"loi": "fss: calcMovingAvg khac mau (khong chung minh bar doc)"}
    ot = _than_ham(vb, "void", "OnTick")
    m = _RX_ONTICK.fullmatch(ot[1]) if ot else None
    if not m:
        return {"loi": "fss: OnTick khac mau cay quyet dinh"}
    # phieu
    phieu = _tach_cap(m.group("phieu"), ",")
    dk = {}
    for p in phieu:
        mp = re.fullmatch(r"booleanToAction\(ACTION::(BUY|SELL),(.*)\)", p)
        if not mp or mp.group(1) in dk:
            return {"loi": "fss: mang phieu khong phai mot BUY + mot SELL"}
        d = _dieu_kien(mp.group(2))
        if isinstance(d, str):
            return {"loi": d}
        dk[mp.group(1)] = d
    if set(dk) != {"BUY", "SELL"}:
        return {"loi": "fss: mang phieu khong phai mot BUY + mot SELL"}
    if not _loai_tru(dk["BUY"], dk["SELL"]):
        return {"loi": "fss: khong chung minh duoc phieu BUY/SELL loai tru (ca hai -> NEUTRAL)"}
    # cau hinh dong lenh (static, khong gan lai)
    cfg = {}
    for ten, kieu in (("closeType", "CLOSE_TYPE"), ("tpType", "SLTPType"), ("slType", "SLTPType"),
                      ("tpValue", "double"), ("slValue", "double")):
        mm = re.findall(rf"^[ \t]*static[ \t]+{kieu}[ \t]+{ten}[ \t]*=[ \t]*([\w.]+)[ \t]*;", vb, re.M)
        gan = re.findall(rf"\b{ten}[ \t]*(?:=(?!=)|\+=|-=|\+\+|--)", vb)
        if len(mm) != 1 or len(gan) != 1:
            return {"loi": f"fss: cau hinh `{ten}` khong phai static gan mot lan"}
        cfg[ten] = mm[0]
    if cfg["closeType"] != "SLTP":
        return {"loi": f"fss: closeType={cfg['closeType']} chua ho tro"}
    if cfg["tpType"] not in ("PIPS", "NONE") or cfg["slType"] not in ("PIPS", "NONE"):
        return {"loi": f"fss: tpType/slType {cfg['tpType']}/{cfg['slType']} chua ho tro"}
    th = _than_ham(vb, "ACTION", "decideIfClosePosition")
    if th is None or not th[1].startswith("switch(closeType){caseSLTP:{") or \
            not all(x in th[1] for x in _MANH_DONG):
        return {"loi": "fss: decideIfClosePosition khac mau"}
    op = _than_ham(vb, "bool", "openPosition")
    if op is None or not all(x in op[1] for x in (
            "if(order_type==ORDER_TYPE_BUY)request.price=ask;elseif(order_type==ORDER_TYPE_SELL)"
            "request.price=bid;", "openPrice=result.price;returntrue;")) or \
            re.search(r"request\.(?:sl|tp)=", op[1]):
        return {"loi": "fss: openPosition khac mau (gia khop / SL-TP)"}
    for x in ("BUY_OPEN", "SELL_OPEN", "openPrice"):
        if len(re.findall(rf"\b{x}[ \t]*=(?!=)", vb)) != {"BUY_OPEN": 3, "SELL_OPEN": 3,
                                                           "openPrice": 2}[x]:
            return {"loi": f"fss: `{x}` bi gan ngoai mau"}
    cl = _than_ham(vb, "bool", "closePosition")
    if cl is None or "if(!PositionSelect(_Symbol))" not in cl[1] or \
            "request.position=position_ticket;" not in cl[1] or \
            "request.volume=volume;" not in cl[1]:
        return {"loi": "fss: closePosition khac mau"}
    tp = float(cfg["tpValue"]) if cfg["tpType"] == "PIPS" else None
    sl = float(cfg["slValue"]) if cfg["slType"] == "PIPS" else None
    dmp = {"tp_pip": tp, "sl_pip": sl, "pip_theo_ten": [["JPY", 0.01], ["BITCOIN", 0.1]],
           "pip_mac_dinh": 0.0001}
    gia_dinh = [
        "calcMovingAvg: CopyBuffer(h,0,shift+1,1) = bar DA DONG shift+1 (bar 1 = bar i)",
        "phieu BUY/SELL loai tru nhau (chung minh tu cap so sanh nghich) -> trung binh = phieu duy nhat",
        "dong o TICK DAU bar moi khi BID - gia_khop (mua) / gia_khop - BID (ban) >= TP pip hoac "
        "<= -SL pip; pip theo TEN MA (JPY 0.01, BITCOIN 0.1, khac 0.0001) - heuristic cua EA",
        "mot vi the mot luc cho ca he (BUY_OPEN||SELL_OPEN); tick dong lenh khong vao lai",
        "GIA DINH Strategy Tester tinh iMA dong bo ngay sau khi tao handle (EA tao/huy handle "
        "moi lan goi; ngoai doi CopyBuffer co the tra -1 -> EMPTY_VALUE, khong mo phong)",
        "lenh vao/dong luon khop (TRADE_RETCODE_DONE); PositionSelect(_Symbol) chi thay lenh cua EA",
    ]
    return {"co_che": [{"chieu": 1, "vao": dk["BUY"]}, {"chieu": -1, "vao": dk["SELL"]}],
            "dong_mo_pip": dmp, "gia_dinh": gia_dinh}
