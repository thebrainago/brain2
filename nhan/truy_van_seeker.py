# -*- coding: utf-8 -*-
"""TRUY VAN SEEKER (11/10/2026): biet TIM GI -> tim -> cao.

Chu du an (t30u + chi dao 11/10 12:49): uu tien bot MT4/MT5 co san chien luoc + file `.set`;
Telegram la nguon chinh cua cac nhom do, nhung he thong phai biet TU GI de tim. Lop nay sinh
truy van tu hai nguon, CO GHI NGUON GOC moi truy van (de biet tu nao ra hang, tu nao chet):

  (1) HAT GIONG CO DINH (`HAT_GIONG`): MT4/MT5 + EA + .set, da ngon ngu (EN/VI/RU/ES/PT/ID/
      ZH/TR) - chot TRUOC, khong chinh theo ket qua.
  (2) TU DAO TU CAI DA THAY: ten file `.set` (bo ma tai san/khung), ten EA trong goi tai ve,
      khoa input trong `.set` (vd `GridStep`, `LotMultiplier` -> co che), ho co che (`ho`) cua
      EA da DICH DUOC, va ghi chu vong thu (`ly_do` chua dich). Trong so theo do sau trong
      pheu: EA hang A (dich duoc, du tep) > co `.set` > chi co ten.

DUNG O DAU:
  - `diem_tieu_de(tieu_de)`: xep bai trong danh sach MQL5 Code Base TRUOC khi tai (het ngan
    sach thi bai tot da tai truoc); panel/auditor/guard/indicator bi ha.
  - `khop(van_ban)`: loc bai Telegram xem truoc cong khai (diem theo truy van + dinh kem).
  - `cho_telegram()`: danh sach truy van ngan cho o tim kiem Telegram (CAN phien MTProto -
    tren box CHUA DO DUOC; khong tu tham gia nhom nao).
Chi tinh toan tren van ban; khong mang, khong ghi gi ngoai `luu()`.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path

#: Hat giong: (truy van, ngon ngu). Tap trung vao "EA + chien luoc + .set".
HAT_GIONG: list[tuple[str, str]] = [
    ("mt5 ea set file", "en"), ("mt4 ea set file", "en"), ("expert advisor mq5 source", "en"),
    ("mq4 source code ea", "en"), ("ea settings .set", "en"), ("free ea mt5 set", "en"),
    ("grid ea set file", "en"), ("martingale ea set", "en"), ("breakout ea mq5", "en"),
    ("scalping ea mt4 set", "en"), ("gold ea set xauusd", "en"), ("backtest ea report set", "en"),
    ("ea mt5 miễn phí file set", "vi"), ("chia sẻ ea mt4 set", "vi"), ("bot mt5 mã nguồn", "vi"),
    ("советник mt5 set файл", "ru"), ("советник mq4 исходник", "ru"),
    ("ea mt5 archivo set", "es"), ("robô mt5 arquivo set", "pt"), ("ea mt4 file set gratis", "id"),
    ("mt5 EA 源码 set", "zh"), ("mt5 ea set dosyası", "tr"),
]

#: Tu cua tai san / khung / rac - bo khi dao ten.
_BO = set("""eurusd gbpusd usdjpy audusd usdcad usdchf nzdusd eurjpy gbpjpy audcad eurgbp xauusd
xagusd gold us30 nas100 us500 ger40 btcusd ethusd m1 m5 m15 m30 h1 h4 d1 w1 mn1 mt4 mt5 ea expert
advisor set mq5 mq4 mqh v1 v2 v3 v4 v5 final new free pro the and for with by of a an to in on
default test tester backtest copy demo live real optimized opt input inputs settings setting""".split())
#: Tu khong mang nghia co che (ten EA hay co) - khong dao lam truy van.
_BO_DAO = set("""trade trader trading risk guard prop demo sketch sample example lite bot robot system
smart auto auto ultimate super best simple basic easy fast quick classic version custom based""".split())
#: Tu ha diem tieu de (cong cu, khong phai chien luoc).
#: 18/10/2026: bo "manager", "indicator", "library", "class" - Grid/Trade Manager la XU LI LENH, chi bao la thu can gom.
TU_CONG_CU = ("panel", "auditor", "guard", "dashboard", "utility",
              "simulator", "planner", "profiler", "inspector", "copier", "clock", "calculator",
              "script", "screenshot", "alert", "notifier")
TU_CHIEN_LUOC = ("strategy", "breakout", "grid", "martingale", "scalp", "trend", "reversal", "recovery", "basket",
                 "trailing", "manager", "averaging", "indicator",
                 "cross", "rsi", "macd", "bollinger", "ema", "sma", "atr", "hedge", "dca",
                 "mean", "momentum", "orb", "session", "stoch", "ichimoku", "zone", "range")
#: Khoa input .set -> tu co che (doc nhieu .set thuc te; chi la nhan tim kiem).
_KHOA_CO_CHE = {"grid": "grid", "step": "grid", "multiplier": "martingale", "martin": "martingale",
                "lotexponent": "martingale", "trail": "trailing", "breakeven": "breakeven",
                "rsi": "rsi", "macd": "macd", "ma_period": "moving average", "maperiod": "moving average",
                "bands": "bollinger", "atr": "atr", "stoch": "stochastic", "hedge": "hedge",
                "session": "session", "breakout": "breakout", "dca": "dca", "basket": "basket"}


_TIEN = {"usd", "eur", "gbp", "jpy", "aud", "nzd", "cad", "chf", "xau", "xag", "btc", "eth",
         "sgd", "hkd", "cnh", "try", "zar", "mxn", "sek", "nok", "pln"}


def _la_cap_tien(t: str) -> bool:
    return len(t) == 6 and t[:3] in _TIEN and t[3:] in _TIEN


def tach_tu(ten: str) -> list[str]:
    """`RSI_Exhaustion_Reversal_EURUSD.set` -> ['rsi','exhaustion','reversal']."""
    s = Path(str(ten)).stem
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    ra = []
    for t in re.split(r"[^A-Za-z]+", s):
        t = t.lower()
        if not t or t in _BO or _la_cap_tien(t):
            continue
        if len(t) >= 3 or t in ("ma",):
            ra.append(t)
    return ra


def doc_set(vb: str) -> dict:
    """File .set MT4/MT5 -> {ten_input: gia_tri} (bo dong `;` va phan `||` toi uu)."""
    ra = {}
    for d in (vb or "").splitlines():
        d = d.strip().lstrip("\ufeff")
        if not d or d.startswith(";") or "=" not in d:
            continue
        k, v = d.split("=", 1)
        k = k.strip()
        if not k or len(k) > 64 or "," in k:
            continue
        ra[k] = v.split("||", 1)[0].strip()[:80]
    return ra


def tu_khoa_set(khoa: list[str]) -> list[str]:
    ra = []
    for k in khoa:
        t = k.lower().replace("_", "")
        for mau, tu in _KHOA_CO_CHE.items():
            if mau.replace("_", "") in t and tu not in ra:
                ra.append(tu)
    return ra


def dao_tu(hang: list[dict], ghi_chu: dict | None = None) -> Counter:
    """Dao tu tu bang xep hang ung vien (`xep_hang_ung_vien.xep`) + ghi chu vong thu.

    Trong so: hang A x3, co .set x2, con lai x1. `ghi_chu` = `{ly_do: so_lan}` tu do_kho
    (chi lay tu co che, vd 'iADX', 'iSAR' -> 'adx', 'sar')."""
    dem: Counter = Counter()
    for x in hang:
        # chi dao tu ung vien CO diem vao (A/B, Telegram co file): cong cu/quan ly lenh (hang C)
        # sinh tu rac ('guard', 'risk', 'prop') - do luot that 11/10.
        if x.get("hang") not in ("A", "B", "T"):
            continue
        w = 3 if x.get("hang") == "A" else 2 if x.get("co_set") else 1
        for t in tach_tu(x.get("ten", "")):
            if t in _BO_DAO or any(t.startswith(k) for k in TU_CONG_CU):
                continue
            dem[t] += w
        for s in x.get("tep_set", []) or []:
            for t in tach_tu(s):
                dem[t] += 2
        for t in tu_khoa_set(x.get("khoa_set", []) or []):
            dem[t] += 2
        for h in x.get("ho", []) or []:
            for t in tach_tu(h):
                dem[t] += w
    for ly, n in (ghi_chu or {}).items():
        for m in re.findall(r"\bi([A-Z][A-Za-z]{1,12})\s*\(?", str(ly)):
            t = m.lower()
            if t not in _BO:
                dem[t] += int(n)
    return dem


def sinh(hang: list[dict] | None = None, ghi_chu: dict | None = None,
         toi_da_dao: int = 25) -> list[dict]:
    """-> [{q, nguon, ngon_ngu, trong_so}] : hat giong truoc, roi tu dao (x 'mt5 ea set')."""
    ra = [{"q": q, "nguon": "hat_giong", "ngon_ngu": nn, "trong_so": 10} for q, nn in HAT_GIONG]
    da = {x["q"] for x in ra}
    for t, w in dao_tu(hang or [], ghi_chu).most_common(toi_da_dao):
        for q in ("%s ea set" % t, "%s mt5 ea" % t):
            if q not in da:
                da.add(q)
                ra.append({"q": q, "nguon": "dao", "tu": t, "ngon_ngu": "en", "trong_so": int(w)})
    return ra


def _tu_cua(ds: list[dict]) -> set:
    tu = set()
    for x in ds:
        if x.get("nguon") == "dao":
            tu.add(x["tu"])
    return tu


def diem_tieu_de(tieu_de: str, truy_van: list[dict] | None = None) -> int:
    """Diem uu tien mot bai Code Base theo TIEU DE (truoc khi tai). Cao = tai truoc."""
    t = (tieu_de or "").lower()
    d = 0
    if ".set" in t or " set " in t or "setfile" in t or "set file" in t:
        d += 20
    if any(k in t for k in TU_CHIEN_LUOC):
        d += 10
    if any(k in t for k in TU_CONG_CU):
        d -= 25
    for tu in _tu_cua(truy_van or []):
        if re.search(r"\b%s\b" % re.escape(tu), t):
            d += 3
    return d


def khop(van_ban: str, dinh_kem: list[dict] | None = None,
         truy_van: list[dict] | None = None) -> dict:
    """Bai Telegram -> {diem, khop[], co_set, co_ma}. Dinh kem .set/.mq5/.mq4 la tin hieu manh
    nhat (file chi tai duoc qua MTProto - CHUA DO DUOC tren box neu thieu phien)."""
    t = (van_ban or "").lower()
    k = []
    for x in truy_van or [{"q": q} for q, _ in HAT_GIONG]:
        tu = [w for w in re.split(r"\s+", x["q"].lower()) if len(w) >= 3 and w not in ("ea",)]
        if tu and all(w in t for w in tu):
            k.append(x["q"])
    ten_dk = [str(d.get("ten", "")).lower() for d in dinh_kem or []]
    co_set = any(n.endswith(".set") for n in ten_dk) or bool(re.search(r"\.set\b", t))
    co_ma = any(n.endswith((".mq5", ".mq4", ".mqh")) for n in ten_dk)
    co_ex = any(n.endswith((".ex5", ".ex4")) for n in ten_dk)
    d = 5 * len(k) + (30 if co_set else 0) + (25 if co_ma else 0) + (5 if co_ex else 0)
    if any(w in t for w in TU_CHIEN_LUOC):
        d += 3
    return {"diem": d, "khop": k[:5], "co_set": co_set, "co_ma": co_ma, "co_ex": co_ex}


def cho_telegram(ds: list[dict], toi_da: int = 15) -> list[str]:
    """Truy van ngan cho o tim kiem Telegram: hat giong + tu dao co trong so cao nhat."""
    hg = [x["q"] for x in ds if x["nguon"] == "hat_giong"]
    dao = sorted((x for x in ds if x["nguon"] == "dao"), key=lambda x: -x["trong_so"])
    return (hg[: toi_da // 2] + [x["q"] for x in dao])[:toi_da]


def luu(ds: list[dict], p) -> None:
    Path(p).write_text(json.dumps({"luc": time.strftime("%Y-%m-%d %H:%M:%S"), "truy_van": ds},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
