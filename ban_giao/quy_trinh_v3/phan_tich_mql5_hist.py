#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phân tích 82 export lịch sử MQL5 + Cổng 0 phí XM. Chỉ số ĐO; thiếu thì CHƯA ĐO ĐƯỢC."""
from __future__ import annotations

import csv
import json
import math
import re
import statistics as st
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

HIST = Path("/workspace/mql5_hist")
BRAIN = Path("/workspace/brain2")
OUT_DIR = Path("/workspace/quy_trinh_v3")
PHI_MICRO = BRAIN / "config" / "phi_xm_micro.json"
CHI_PHI_DO = BRAIN / "config" / "chi_phi_do.json"
LOC_CHAT = BRAIN / "reports" / "MQL5_LOC_CHAT.md"

EDGE_COST_MIN = 1.5
CAGR_MIN = 10.0
DD_MAX = 80.0


def parse_num(s: str) -> Optional[float]:
    if s is None:
        return None
    t = str(s).strip().replace("\xa0", "").replace(" ", "").replace(",", "")
    if t == "" or t.lower() in ("cancelled", "canceled", "n/a"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def parse_time(s: str) -> Optional[datetime]:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y.%m.%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


# --- symbol map -----------------------------------------------------------
_SUFFIX_RE = re.compile(
    r"(\.fx|\.p|\.i|\.c|micro|#|-E|\.|f|b|c)$", re.I
)

SYMBOL_MAP = {
    "GOLD": "XAUUSD",
    "GOLDM": "XAUUSD",
    "GOLDMICRO": "XAUUSD",
    "GOLDM#": "XAUUSD",
    "GOLD#": "XAUUSD",
    "GOLDMI": "XAUUSD",
    "XAUUSDC": "XAUUSD",
    "XAUUSDB": "XAUUSD",
    "XAUUSD.I": "XAUUSD",
    "XAUUSD.P": "XAUUSD",
    "NAS100": "US100",
    "NQCASH": "US100",
    "NQ": "US100",
    "US500CASH": "US500",
    "USTEC": "US100",
}


def map_symbol(raw: str) -> Optional[str]:
    if not raw or not str(raw).strip():
        return None
    s = str(raw).strip()
    su = s.upper()
    if su in SYMBOL_MAP:
        return SYMBOL_MAP[su]
    base = su
    # Bóc hậu tố broker theo thứ tự dài → ngắn; KHÔNG cắt chữ cái của mã 6 ký tự (EURCHF).
    for _ in range(5):
        n2 = base
        for suf in ("MICRO", ".FX", ".P", ".I", "-E", "#"):
            if n2.endswith(suf):
                n2 = n2[: -len(suf)]
                break
        else:
            # dấu chấm / gạch cuối (AUDCAD. / AUDCAD-)
            if n2.endswith(".") or n2.endswith("-"):
                n2 = n2[:-1]
            # hậu tố 1 chữ chỉ khi dài > 6 (EURUSDf, XAUUSDc, GOLDm)
            elif len(n2) > 6 and n2[-1] in ("F", "C", "B", "M") and n2[:-1].isalnum():
                n2 = n2[:-1]
        if n2 == base:
            break
        base = n2
    if base in SYMBOL_MAP:
        return SYMBOL_MAP[base]
    if len(base) == 6 and base.isalpha():
        return base
    if base in ("XAUUSD", "BTCUSD", "ETHUSD", "US500", "US100", "US30"):
        return base
    if any(x in base for x in ("OIL", "BRENT", "CL_", "COFFEE", "KC_")):
        return "OTHER:" + base
    return base if base else None


# --- fee ------------------------------------------------------------------
@dataclass
class Phi:
    symbol: str
    spread_p90: float
    swap_mua: float
    swap_ban: float
    point: float
    contract: float
    nguon: str
    thieu_spread: bool = False
    swap_mode: int = 1  # 1=POINTS
    gia_ref: float = 0.0


_PHI_CACHE: dict[str, Optional[Phi]] = {}
_DO = None
_MICRO = None
_SB = None


def _load_fee_files():
    global _DO, _MICRO, _SB
    if _DO is None:
        _DO = json.loads(CHI_PHI_DO.read_text(encoding="utf-8"))
        _MICRO = json.loads(PHI_MICRO.read_text(encoding="utf-8"))
        _SB = _DO.get("_spread_bar_mt5") or {}


def load_phi(symbol: str) -> Optional[Phi]:
    """XM fee. None nếu không đo được spread+swap."""
    if symbol.startswith("OTHER:"):
        return None
    if symbol in _PHI_CACHE:
        return _PHI_CACHE[symbol]
    _load_fee_files()
    sym = symbol.upper()

    # 1) phi_xm_micro
    if sym in _MICRO and isinstance(_MICRO[sym], dict):
        r = _MICRO[sym]
        point = 0.001 if sym.endswith("JPY") else (0.01 if sym in ("XAUUSD", "US500", "US100") else 1e-5)
        if sym == "XAUUSD":
            point = 0.01
            contract = 1.0  # GOLDmicro
        elif sym.endswith("JPY"):
            contract = 1000.0
        else:
            contract = 1000.0
        phi = Phi(
            symbol=sym,
            spread_p90=float(r["spread_p90_gia"]),
            swap_mua=float(r["swap_mua_diem"]),
            swap_ban=float(r["swap_ban_diem"]),
            point=point,
            contract=contract,
            nguon="phi_xm_micro.json",
        )
        _PHI_CACHE[symbol] = phi
        return phi

    # US100 alias — try NAS100 in do / no micro spread
    aliases = {
        "US100": ["NAS100", "USTEC", "US100Cash"],
        "US500": ["US500", "US500Cash"],
    }
    # 2) chi_phi_do MICRO XM + spread bar
    micro_key = sym + "MICRO"
    r = _DO.get(micro_key) or _DO.get(sym)
    # special gold
    if sym == "XAUUSD":
        r = _DO.get("GOLDMICRO") or _DO.get("XAUUSD") or r
    if sym == "US100":
        r = _DO.get("NAS100") or r

    spread = None
    # prefer absolute from phi-like; else spread bar
    sb = _SB.get(sym) or (_SB.get("XAUUSD") if sym == "XAUUSD" else None)
    if sym == "US100":
        sb = _SB.get("NAS100") or _SB.get("US100")
    if isinstance(sb, dict) and sb.get("chung") is not None:
        chung = float(sb["chung"])
        gia = float((r or {}).get("gia_luc_do") or 0) or None
        # Index/vàng: chung trong bar thường là tỷ lệ (spread/price). FX: tuyệt đối ~1e-4.
        if sym in ("US100", "US500", "US30", "XAUUSD") and chung < 0.01 and gia:
            spread = chung * gia
        else:
            spread = chung

    if r is None and spread is None:
        _PHI_CACHE[symbol] = None
        return None

    if r is None:
        # only spread — still insufficient without swap
        _PHI_CACHE[symbol] = None
        return None

    # Prefer XM MICRO swap when available
    swap_mua = float(r.get("swap_long") or 0)
    swap_ban = float(r.get("swap_short") or 0)
    point = float(r.get("point") or (0.01 if sym in ("XAUUSD", "US500", "US100") else 1e-5))
    contract = float(r.get("contract_size") or 1000.0)
    san = str(r.get("san") or "")
    thieu_spread = spread is None
    if spread is None:
        # cannot apply Cổng 0 fully
        _PHI_CACHE[symbol] = None
        return None
    # For XAU if we used relative conversion, label
    nguon = f"chi_phi_do:{micro_key if _DO.get(micro_key) else sym}+spread_bar"
    if sym == "XAUUSD" and _MICRO.get("XAUUSD"):
        # should have hit branch 1
        pass
    smode = int(r.get("swap_mode") or 1)
    gia_ref = float(r.get("gia_luc_do") or 0)
    if smode != 1:
        # Non-POINTS: dùng phi_nam (tỷ lệ/năm) thay vì swap points
        swap_mua = float(r.get("phi_nam_mua") or 0)
        swap_ban = float(r.get("phi_nam_ban") or 0)
    phi = Phi(
        symbol=sym,
        spread_p90=float(spread),
        swap_mua=swap_mua,
        swap_ban=swap_ban,
        point=point,
        contract=contract,
        nguon=nguon + (f"|san={san}" if san else ""),
        thieu_spread=thieu_spread,
        swap_mode=smode,
        gia_ref=gia_ref,
    )
    _PHI_CACHE[symbol] = phi
    return phi


def nights_hold(hold_days: float) -> float:
    """Wed x3 ≈ 7 night-units / 5 trading nights."""
    return max(hold_days, 0.0) * (7.0 / 5.0)


def xm_cost_price(phi: Phi, hold_days: float, chieu: int, gia_tham: float | None = None) -> tuple[float, float, float]:
    """Trả (spread_price, swap_price, total_cost_price). swap_price mang dấu (âm = trả)."""
    sp = abs(phi.spread_p90)
    dem = nights_hold(hold_days)
    if phi.swap_mode == 1:  # POINTS
        diem = phi.swap_mua if chieu > 0 else phi.swap_ban
        sw = diem * phi.point * dem
    else:
        rate = phi.swap_mua if chieu > 0 else phi.swap_ban  # phi_nam
        gia = gia_tham or phi.gia_ref or 0.0
        if gia > 0 and abs(rate) < 2.0:
            # phi_nam dương ≈ chi phí/năm trên giá → sw âm
            sw = -abs(rate) * gia * (max(hold_days, 0.0) / 365.0)
        else:
            sw = 0.0
    cost = sp + max(-sw, 0.0)
    return sp, sw, cost


# --- parse trades ---------------------------------------------------------
@dataclass
class Trade:
    t_open: datetime
    t_close: datetime
    symbol_raw: str
    symbol: str
    chieu: int  # +1 buy, -1 sell
    volume: float
    price_open: float
    price_close: float
    sl: Optional[float]
    tp: Optional[float]
    commission: float
    swap: float
    profit: float
    comment: str
    has_sl: bool
    has_tp: bool


def _is_cancelled(type_: str, comment: str, profit_s: str) -> bool:
    blob = f"{type_} {comment} {profit_s}".lower()
    return "cancel" in blob


def parse_roundtrip(path: Path) -> list[Trade]:
    """Time;Type;Volume;Symbol;Price;S/L;T/P;Time;Price;Commission;Swap;Profit;Comment"""
    raw = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    if not raw:
        return []
    trades = []
    for line in raw[1:]:
        if not line.strip():
            continue
        p = line.split(";")
        if len(p) < 12:
            continue
        typ = p[1].strip()
        comment = p[12].strip() if len(p) > 12 else ""
        if _is_cancelled(typ, comment, p[11] if len(p) > 11 else ""):
            continue
        if typ.lower() in ("buy limit", "sell limit", "buy stop", "sell stop", "buy stop limit", "sell stop limit"):
            # pending still open or weird — skip if no profit parsed as closed market
            # if close time exists and type is pending with cancelled already skipped
            if "cancel" in comment.lower():
                continue
            # pending that filled? uncommon in this export format as open type
            # skip pure pending rows without buy/sell
            if typ.lower() not in ("buy", "sell"):
                continue
        if typ not in ("Buy", "Sell", "buy", "sell"):
            # skip Balance etc
            if typ.lower() in ("balance", "credit", "deposit", "withdrawal"):
                continue
            if typ.lower() not in ("buy", "sell"):
                continue
        vol = parse_num(p[2])
        sym_raw = p[3].strip()
        px_o = parse_num(p[4])
        sl = parse_num(p[5])
        tp = parse_num(p[6])
        t_o = parse_time(p[0])
        t_c = parse_time(p[7])
        px_c = parse_num(p[8])
        com = parse_num(p[9]) or 0.0
        sw = parse_num(p[10]) or 0.0
        pr = parse_num(p[11])
        if None in (vol, px_o, px_c, t_o, t_c, pr):
            continue
        if vol <= 0:
            continue
        chieu = 1 if typ.lower() == "buy" else -1
        sym = map_symbol(sym_raw)
        if not sym:
            continue
        trades.append(
            Trade(
                t_open=t_o,
                t_close=t_c,
                symbol_raw=sym_raw,
                symbol=sym,
                chieu=chieu,
                volume=vol,
                price_open=px_o,
                price_close=px_c,
                sl=sl,
                tp=tp,
                commission=com,
                swap=sw,
                profit=pr,
                comment=comment,
                has_sl=sl is not None and sl != 0,
                has_tp=tp is not None and tp != 0,
            )
        )
    return trades


def parse_deals(path: Path) -> list[Trade]:
    """Time;Symbol;Type;Direction;Volume;Price;Commission;Swap;Profit;Comment
    Ghép In/Out theo FIFO từng symbol+type.
    """
    raw = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    if not raw:
        return []
    # collect deals
    opens = defaultdict(list)  # key (sym, type) -> stack of in deals
    trades: list[Trade] = []
    # First pass: sort chronologically (file often newest-first)
    rows = []
    for line in raw[1:]:
        if not line.strip():
            continue
        p = line.split(";")
        if len(p) < 9:
            continue
        t = parse_time(p[0])
        if not t:
            continue
        rows.append((t, p))
    rows.sort(key=lambda x: x[0])

    for t, p in rows:
        sym_raw = p[1].strip()
        typ = p[2].strip()  # Buy/Sell
        direction = p[3].strip()  # In/Out
        vol = parse_num(p[4])
        px = parse_num(p[5])
        com = parse_num(p[6]) or 0.0
        sw = parse_num(p[7]) or 0.0
        pr = parse_num(p[8]) or 0.0
        comment = p[9].strip() if len(p) > 9 else ""
        if vol is None or px is None or vol <= 0:
            continue
        if typ not in ("Buy", "Sell", "buy", "sell"):
            continue
        # Direction In: Type = hướng vị thế. Direction Out: Type = chiều deal đóng (= ngược vị thế).
        if direction.lower() == "in":
            key = (sym_raw, typ.lower())  # buy/sell = chiều vị thế
            opens[key].append(
                dict(t=t, vol=vol, px=px, com=com, sw=sw, comment=comment, chieu=(1 if typ.lower()=="buy" else -1))
            )
        elif direction.lower() == "out":
            # Sell Out đóng Buy; Buy Out đóng Sell
            pos_side = "buy" if typ.lower() == "sell" else "sell"
            key = (sym_raw, pos_side)
            remain = vol
            while remain > 1e-12 and opens[key]:
                op = opens[key][0]
                take = min(op["vol"], remain)
                frac = take / op["vol"] if op["vol"] else 1.0
                chieu = op["chieu"]
                sym = map_symbol(sym_raw)
                if sym:
                    trades.append(
                        Trade(
                            t_open=op["t"],
                            t_close=t,
                            symbol_raw=sym_raw,
                            symbol=sym,
                            chieu=chieu,
                            volume=take,
                            price_open=op["px"],
                            price_close=px,
                            sl=None,
                            tp=None,
                            commission=com * (take / vol if vol else 1) + op["com"] * frac,
                            swap=sw * (take / vol if vol else 1) + op["sw"] * frac,
                            profit=pr * (take / vol if vol else 1),
                            comment=comment or op["comment"],
                            has_sl=False,
                            has_tp="[tp]" in (comment or "").lower() or "[tp]" in (op["comment"] or "").lower(),
                        )
                    )
                op["vol"] -= take
                remain -= take
                if op["vol"] <= 1e-12:
                    opens[key].pop(0)
        # else ignore
    return trades


def load_trades(path: Path) -> list[Trade]:
    head = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[:1]
    if not head:
        return []
    if "Direction" in head[0]:
        return parse_deals(path)
    return parse_roundtrip(path)


# --- analytics ------------------------------------------------------------
def max_concurrent(trades: list[Trade]) -> int:
    events = []
    for tr in trades:
        events.append((tr.t_open, 1))
        events.append((tr.t_close, -1))
    events.sort(key=lambda x: (x[0], -x[1]))
    cur = mx = 0
    for _, d in events:
        cur += d
        mx = max(mx, cur)
    return mx


def _merge_partials(trades: list[Trade]) -> list[Trade]:
    """Gộp partial close / scale-in cùng (symbol, chiều, t_open) thành 1 rổ để tránh ảo lưới."""
    bags: dict[tuple, list[Trade]] = defaultdict(list)
    for t in trades:
        bags[(t.symbol, t.chieu, t.t_open)].append(t)
    out: list[Trade] = []
    for (sym, ch, t0), grp in bags.items():
        if len(grp) == 1:
            out.append(grp[0])
            continue
        t1 = max(x.t_close for x in grp)
        vol = sum(x.volume for x in grp)
        # VWAP open/close
        po = sum(x.price_open * x.volume for x in grp) / vol
        pc = sum(x.price_close * x.volume for x in grp) / vol
        pr = sum(x.profit for x in grp)
        sw = sum(x.swap for x in grp)
        com = sum(x.commission for x in grp)
        g0 = grp[0]
        out.append(
            Trade(
                t_open=t0,
                t_close=t1,
                symbol_raw=g0.symbol_raw,
                symbol=sym,
                chieu=ch,
                volume=vol,
                price_open=po,
                price_close=pc,
                sl=g0.sl,
                tp=g0.tp,
                commission=com,
                swap=sw,
                profit=pr,
                comment=g0.comment,
                has_sl=any(x.has_sl for x in grp),
                has_tp=any(x.has_tp for x in grp),
            )
        )
    return out


def detect_grid_martingale(trades: list[Trade]) -> dict:
    """Lưới = nhiều lệnh CÙNG MÃ CÙNG CHIỀU mở chồng.

    Ngưỡng CHẶT (tránh false positive từ pending/partial/2–3 lệnh có SL):
      grid ⇔ max_cung_chieu_mo >= 4
              OR (max_cung_chieu_mo >= 3 AND sl_pct < 20 AND overlap_rate >= 0.35)
    Chỉ đo trong từng symbol; multi-symbol concurrent không tính lưới.
    """
    if not trades:
        return dict(grid=False, martingale=False, ly_do="", pyramid_nhe=False)
    merged = _merge_partials(trades)
    by_sym: dict[str, list] = defaultdict(list)
    for tr in merged:
        by_sym[tr.symbol].append(tr)

    overlap_hits = 0
    max_same = 0
    for sym, ts in by_sym.items():
        ts = sorted(ts, key=lambda x: x.t_open)
        for i, a in enumerate(ts):
            for b in ts[i + 1 : i + 60]:
                if b.t_open >= a.t_close:
                    break
                if b.chieu == a.chieu:
                    overlap_hits += 1
                    break
        events = []
        for tr in ts:
            events.append((tr.t_open, tr.chieu, 1))
            events.append((tr.t_close, tr.chieu, -1))
        events.sort(key=lambda x: (x[0], -x[2]))
        cur_b = cur_s = 0
        for _, ch, d in events:
            if ch > 0:
                cur_b += d
            else:
                cur_s += d
            max_same = max(max_same, cur_b, cur_s)

    mart_hits = mart_checks = 0
    for sym, ts in by_sym.items():
        ts = sorted(ts, key=lambda x: x.t_close)
        for i in range(len(ts) - 1):
            a, b = ts[i], ts[i + 1]
            if a.profit < 0 and b.t_open >= a.t_close:
                mart_checks += 1
                if b.volume > a.volume * 1.2 and b.chieu == a.chieu:
                    mart_hits += 1

    sl_pct = 100.0 * sum(1 for t in trades if t.has_sl) / len(trades)
    overlap_rate = overlap_hits / max(len(merged), 1)
    grid = max_same >= 4 or (max_same >= 3 and sl_pct < 20 and overlap_rate >= 0.35)
    pyramid_nhe = (not grid) and max_same == 3 and sl_pct >= 20
    mart = mart_checks >= 10 and (mart_hits / mart_checks) >= 0.25
    ly = []
    if grid:
        ly.append(f"max_cung_chieu_mo={max_same}, overlap_hits={overlap_hits}/{len(merged)}")
    if pyramid_nhe:
        ly.append(f"pyramid_nhe max={max_same}")
    if mart:
        ly.append(f"martingale_rate={mart_hits}/{mart_checks}")
    if sl_pct < 10:
        ly.append(f"SL_pct={sl_pct:.1f}")
    return dict(
        grid=grid,
        martingale=mart,
        pyramid_nhe=pyramid_nhe,
        max_cung_chieu_mo=max_same,
        overlap_hits=overlap_hits,
        overlap_rate=round(overlap_rate, 3),
        n_merged=len(merged),
        mart_rate=(mart_hits / mart_checks if mart_checks else None),
        sl_pct=round(sl_pct, 2),
        ly_do="; ".join(ly),
    )


def cong_s_heuristic(trades: list[Trade]) -> dict:
    """Ước lượng khả năng suy ra luật vào."""
    if len(trades) < 30:
        return dict(diem=0, nhan="yeu", ly_do="ít hơn 30 lệnh")
    # entry minute distribution
    minutes = Counter(t.t_open.minute for t in trades)
    hours = Counter(t.t_open.hour for t in trades)
    top_min, top_min_n = minutes.most_common(1)[0]
    min_conc = top_min_n / len(trades)
    # SL/TP fixed offset?
    sl_off = []
    tp_off = []
    for t in trades:
        if t.has_sl and t.sl:
            sl_off.append(abs(t.sl - t.price_open))
        if t.has_tp and t.tp:
            tp_off.append(abs(t.tp - t.price_open))
    sl_stable = tp_stable = False
    sl_med = tp_med = None
    if len(sl_off) >= 20:
        sl_med = st.median(sl_off)
        if sl_med > 0:
            sl_stable = (st.median([abs(x - sl_med) for x in sl_off]) / sl_med) < 0.15
    if len(tp_off) >= 20:
        tp_med = st.median(tp_off)
        if tp_med > 0:
            tp_stable = (st.median([abs(x - tp_med) for x in tp_off]) / tp_med) < 0.15

    # pending comments
    pending_n = sum(1 for t in trades if any(k in t.comment.lower() for k in ("stop", "limit")))
    diem = 0
    ly = []
    if min_conc >= 0.4:
        diem += 3
        ly.append(f"phút_vào={top_min} ({min_conc*100:.0f}%)")
    elif min_conc >= 0.25:
        diem += 2
        ly.append(f"phút_vào={top_min} ({min_conc*100:.0f}%)")
    if sl_stable:
        diem += 3
        ly.append(f"SL_offset_med={sl_med:.5g} ổn định")
    if tp_stable:
        diem += 2
        ly.append(f"TP_offset_med={tp_med:.5g} ổn định")
    buy_pct = 100.0 * sum(1 for t in trades if t.chieu > 0) / len(trades)
    if 40 <= buy_pct <= 60:
        diem += 1
        ly.append(f"2 chiều cân ({buy_pct:.0f}% buy)")
    elif buy_pct >= 90 or buy_pct <= 10:
        diem -= 1
        ly.append(f"lệch chiều buy={buy_pct:.0f}%")
    # single symbol easier
    nsym = len({t.symbol for t in trades})
    if nsym == 1:
        diem += 1
        ly.append("1 mã")
    nhan = "manh" if diem >= 6 else ("trung" if diem >= 3 else "yeu")
    return dict(
        diem=diem,
        nhan=nhan,
        ly_do="; ".join(ly) if ly else "không thấy cấu trúc rõ",
        min_conc=round(min_conc, 3),
        top_minute=top_min,
        sl_stable=sl_stable,
        tp_stable=tp_stable,
        buy_pct=round(buy_pct, 1),
        n_symbol=nsym,
    )


def analyze_signal(sid: str, meta: dict) -> dict:
    path = HIST / f"{sid}.csv"
    if not path.exists():
        return dict(id=sid, ket_luan="CHUA_DO", ly_do="không có file export", **meta)

    trades = load_trades(path)
    if not trades:
        return dict(id=sid, ket_luan="CHUA_DO", ly_do="0 lệnh đóng sau khi parse", n_lenh=0, **meta)

    t0 = min(t.t_open for t in trades)
    t1 = max(t.t_close for t in trades)
    years = max((t1 - t0).total_seconds() / (365.25 * 86400), 1e-9)
    holds = [(t.t_close - t.t_open).total_seconds() / 86400 for t in trades]
    buy_n = sum(1 for t in trades if t.chieu > 0)
    syms = Counter(t.symbol for t in trades)
    raw_syms = Counter(t.symbol_raw for t in trades)

    grid = detect_grid_martingale(trades)
    cong_s = cong_s_heuristic(trades)

    # --- fee rebuild in price units ---
    per_trade_net_price = []
    per_trade_gross_price = []
    per_trade_cost = []
    per_trade_ratio_num = []
    missing_phi = Counter()
    orig_profit = sum(t.profit for t in trades)
    orig_swap = sum(t.swap for t in trades)
    orig_com = sum(t.commission for t in trades)

    # equity in original profit (broker) for DD/CAGR reference
    eq = 0.0
    peak = 0.0
    max_dd = 0.0
    eq_curve = []
    for t in sorted(trades, key=lambda x: x.t_close):
        eq += t.profit + t.swap + t.commission
        peak = max(peak, eq)
        dd = (peak - eq) / peak * 100 if peak > 0 else 0.0
        max_dd = max(max_dd, dd)
        eq_curve.append((t.t_close, eq))

    # XM costs
    usable = 0
    for t in trades:
        phi = load_phi(t.symbol)
        if phi is None:
            missing_phi[t.symbol] += 1
            continue
        hold = (t.t_close - t.t_open).total_seconds() / 86400
        gross = t.chieu * (t.price_close - t.price_open)
        sp, sw, cost = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
        # net after XM: gross - spread + swap_signed (sw already signed)
        # paying swap (sw<0) reduces net; earning swap increases
        net = gross - sp + sw
        per_trade_gross_price.append(gross)
        per_trade_net_price.append(net)
        per_trade_cost.append(cost)
        per_trade_ratio_num.append(gross)
        usable += 1

    fee_cover = usable / len(trades) if trades else 0.0

    if usable < max(20, 0.5 * len(trades)):
        ket = "CHUA_DO"
        ly_phi = f"phí XM chỉ cover {usable}/{len(trades)} lệnh ({fee_cover*100:.0f}%); thiếu: {dict(missing_phi.most_common(5))}"
        net_e = None
        ratio = None
        annual_net_price = None
    else:
        net_e = st.mean(per_trade_net_price)
        gross_e = st.mean(per_trade_gross_price)
        cost_e = st.mean(per_trade_cost)
        # Spread XM gần 0 hoặc thiếu → không tin cậy (thường US100 không có spread bar)
        if cost_e < 1e-8:
            ket = "CHUA_DO"
            ly_phi = f"cost_E≈0 ({cost_e:.3g}) — thiếu spread XM đáng tin"
            ratio = None
            annual_net_price = None
            net_e = None
        else:
            ratio = (gross_e / cost_e) if cost_e > 1e-15 else float("inf")
            annual_net_price = net_e * (len(per_trade_net_price) / years)
            ly_phi = ""
            ket = "PASS"
            if net_e <= 0:
                ket = "REJECT"
                ly_phi = f"net_E_price={net_e:.6g}≤0"
            if ratio is not None and ratio < EDGE_COST_MIN:
                ket = "REJECT"
                ly_phi = (ly_phi + "; " if ly_phi else "") + f"edge/cost={ratio:.3f}<{EDGE_COST_MIN}"

    # CAGR/DD ƯỚC from original broker equity (already includes their fees)
    # + XM haircut: scale by net_e_xm / mean(orig profit per trade in price?)
    # Simpler stated assumption: CAGR_MQL5 from meta; XM-adjusted = only if we have price net
    cagr_meta = None
    dd_meta = None
    try:
        cagr_meta = float(meta.get("cagr", "").replace(",", "."))
        dd_meta = float(meta.get("dd", "").replace(",", "."))
    except Exception:
        pass

    # Rebuild equity with XM net in USD using contract*volume heuristic
    # Assumption: lot trên export là lot chuẩn broker; quy về notional bằng phi.contract
    # Dùng volume như lot của đúng contract trong bảng phí (micro nếu MICRO).
    eq_xm = 0.0
    peak_xm = 0.0
    max_dd_xm = 0.0
    usd_nets = []
    for t in sorted(trades, key=lambda x: x.t_close):
        phi = load_phi(t.symbol)
        if phi is None:
            continue
        hold = (t.t_close - t.t_open).total_seconds() / 86400
        gross = t.chieu * (t.price_close - t.price_open)
        sp, sw, _ = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
        net_price = gross - sp + sw
        # USD ≈ net_price * contract * volume  (đúng nếu volume là lot của contract đó)
        # Với micro contract=1000 và volume 0.01 standard IC → lệch. Ghi giả định.
        usd = net_price * phi.contract * t.volume
        # Gold micro contract=1: usd = net_price * 1 * vol
        usd_nets.append(usd)
        eq_xm += usd
        peak_xm = max(peak_xm, eq_xm)
        if peak_xm > 0:
            max_dd_xm = max(max_dd_xm, (peak_xm - eq_xm) / peak_xm * 100)

    # Fixed fractional risk CAGR ƯỚC:
    # Vốn giả định V0=10000; mỗi lệnh rủi ro 1% vốn nếu có SL, else dùng |gross| median làm proxy risk unit.
    cagr_ff = None
    dd_ff = None
    ff_note = "CHƯA ĐO ĐƯỢC"
    if usd_nets and years > 0:
        V0 = 10000.0
        # scale lots so that median |usd| loss ≈ 1% V0 — actually use fixed fraction of measured usd path
        # Simpler: compound by r_i = usd_i / V0 with V0 fixed (no resize) → "fixed lot" not fractional
        # True fractional: V grows, risk 1% each trade based on SL distance in USD
        V = V0
        peak = V0
        maxdd = 0.0
        sl_risks = []
        for t in trades:
            phi = load_phi(t.symbol)
            if phi and t.has_sl and t.sl is not None:
                risk_price = abs(t.price_open - t.sl)
                sl_risks.append(risk_price * phi.contract * t.volume)
        target_risk = 0.01 * V0
        for t in sorted(trades, key=lambda x: x.t_close):
            phi = load_phi(t.symbol)
            if phi is None:
                continue
            hold = (t.t_close - t.t_open).total_seconds() / 86400
            gross = t.chieu * (t.price_close - t.price_open)
            sp, sw, _ = xm_cost_price(phi, hold, t.chieu, gia_tham=t.price_open)
            net_price = gross - sp + sw
            usd_1lot = net_price * phi.contract  # per 1.0 volume unit
            if t.has_sl and t.sl is not None and abs(t.price_open - t.sl) > 0:
                risk_1 = abs(t.price_open - t.sl) * phi.contract
            else:
                # proxy: median |gross| among trades
                risk_1 = abs(net_price) * phi.contract if net_price != 0 else phi.spread_p90 * phi.contract
                if risk_1 <= 0:
                    risk_1 = phi.spread_p90 * phi.contract + 1e-9
            # size so risk = 1% current V
            risk_budget = 0.01 * V
            vol_sz = risk_budget / risk_1 if risk_1 > 0 else 0
            pnl = usd_1lot * vol_sz
            V += pnl
            if V <= 0:
                V = 0
                maxdd = 100.0
                break
            peak = max(peak, V)
            maxdd = max(maxdd, (peak - V) / peak * 100)
        if V > 0 and years > 0:
            # Chặn bùng nổ số khi risk_1 quá nhỏ (proxy xấu)
            if V / V0 > 1e6:
                cagr_ff = None
                dd_ff = maxdd
                ff_note = "CAGR_ff CHƯA ĐO ĐƯỢC (equity giả định bùng >1e6× — proxy rủi ro không tin)"
            else:
                cagr_ff = ((V / V0) ** (1 / years) - 1) * 100
                dd_ff = maxdd
                ff_note = "V0=10000; rủi ro 1% vốn/lệnh theo SL (hoặc |net_price| nếu không SL); lot quy về contract bảng phí"

    # all-one-direction flag
    buy_pct = 100.0 * buy_n / len(trades)
    all_dir = buy_pct >= 95 or buy_pct <= 5

    # B&H flag: compare first/last mid of dominant symbol
    dom_sym, dom_n = syms.most_common(1)[0]
    bh = None
    ts_dom = [t for t in trades if t.symbol == dom_sym]
    if len(ts_dom) >= 10:
        # use opens chronology
        ts_dom_o = sorted(ts_dom, key=lambda x: x.t_open)
        g0 = ts_dom_o[0].price_open
        g1 = ts_dom_o[-1].price_close
        if g0 > 0:
            ret = g1 / g0 - 1
            bh_cagr = ((1 + ret) ** (1 / years) - 1) * 100 if ret > -1 else None
            bh = dict(symbol=dom_sym, px0=g0, px1=g1, ret_pct=round(ret * 100, 2), cagr_pct=round(bh_cagr, 2) if bh_cagr is not None else None)

    # Cổng 0 final with DD/CAGR gates when ff available
    ly_do_parts = []
    if ket == "REJECT" and ly_phi:
        ly_do_parts.append(ly_phi)
    if ket == "CHUA_DO" and ly_phi:
        ly_do_parts.append(ly_phi)
    if ket == "PASS" and cagr_ff is not None and dd_ff is not None:
        if not (cagr_ff > CAGR_MIN and dd_ff < DD_MAX):
            ket = "REJECT"
            ly_do_parts.append(f"CAGR_ff={cagr_ff:.2f}/DD_ff={dd_ff:.2f} không đạt 10%/80%")
    if grid["grid"] or grid["martingale"]:
        # flag but not auto-reject at Cổng 0 (fee gate); note for V1
        ly_do_parts.append("CỜ:" + grid["ly_do"])

    return dict(
        id=sid,
        ten=meta.get("ten"),
        rank_chat=meta.get("rank"),
        server=meta.get("server"),
        ma_meta=meta.get("ma"),
        cagr_mql5=cagr_meta,
        dd_mql5=dd_meta,
        n_lenh=len(trades),
        years=round(years, 3),
        trades_per_yr=round(len(trades) / years, 1),
        t0=t0.isoformat(sep=" "),
        t1=t1.isoformat(sep=" "),
        symbols=dict(syms.most_common(6)),
        symbols_raw=dict(raw_syms.most_common(6)),
        buy_pct=round(buy_pct, 1),
        all_one_direction=all_dir,
        hold_med_days=round(st.median(holds), 3),
        hold_p90_days=round(sorted(holds)[max(int(0.9 * len(holds)) - 1, 0)], 3),
        hold_max_days=round(max(holds), 2),
        max_concurrent=max_concurrent(trades),
        sl_pct=grid["sl_pct"],
        grid=grid["grid"],
        martingale=grid["martingale"],
        grid_note=grid["ly_do"],
        orig_profit_sum=round(orig_profit, 2),
        orig_swap_sum=round(orig_swap, 2),
        orig_commission_sum=round(orig_com, 2),
        orig_dd_pct_equity=round(max_dd, 2),
        fee_cover_pct=round(fee_cover * 100, 1),
        missing_phi=dict(missing_phi.most_common(8)),
        net_E_price=round(net_e, 6) if net_e is not None else None,
        edge_cost_ratio=round(ratio, 3) if ratio is not None else None,
        annual_net_price=round(annual_net_price, 4) if annual_net_price is not None else None,
        cagr_ff_pct=round(cagr_ff, 2) if cagr_ff is not None else None,
        dd_ff_pct=round(dd_ff, 2) if dd_ff is not None else None,
        ff_note=ff_note,
        bh=bh,
        cong_s=cong_s,
        ket_luan=ket,
        ly_do="; ".join(ly_do_parts) if ly_do_parts else ("ok" if ket == "PASS" else ket),
        phi_nguon_chinh=None,
    )


def parse_meta() -> dict[str, dict]:
    md = LOC_CHAT.read_text(encoding="utf-8")
    out = {}
    for line in md.splitlines():
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*\[(\d+)\]\([^)]+\)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            line,
        )
        if not m:
            continue
        out[m.group(2)] = dict(
            rank=int(m.group(1)),
            ten=m.group(3).strip(),
            ma=m.group(4).strip(),
            tuoi=m.group(5).strip(),
            cagr=m.group(6).strip(),
            dd=m.group(7).strip(),
            sut=m.group(8).strip(),
            luoi=m.group(9).strip(),
            server=m.group(11).strip(),
        )
    return out


def main():
    meta = parse_meta()
    results = []
    for sid in sorted(meta.keys(), key=lambda x: meta[x]["rank"]):
        print("...", sid, meta[sid]["ten"][:40], flush=True)
        try:
            r = analyze_signal(sid, meta[sid])
        except Exception as e:
            r = dict(id=sid, ket_luan="LOI", ly_do=f"{type(e).__name__}: {e}", **meta[sid])
        results.append(r)

    # summary counts
    c = Counter(r.get("ket_luan") for r in results)
    print("COUNTS", dict(c))

    out_json = OUT_DIR / "mql5_83_loc_phi_ket_qua.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # CSV summary
    fields = [
        "rank_chat", "id", "ten", "ket_luan", "ly_do", "n_lenh", "years", "trades_per_yr",
        "buy_pct", "all_one_direction", "hold_med_days", "hold_max_days", "max_concurrent",
        "sl_pct", "grid", "martingale", "fee_cover_pct", "net_E_price", "edge_cost_ratio",
        "cagr_ff_pct", "dd_ff_pct", "cagr_mql5", "dd_mql5",
        "cong_s_nhan", "cong_s_diem", "cong_s_ly_do", "symbols",
    ]
    out_csv = OUT_DIR / "mql5_83_loc_phi_tom_tat.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            row = {k: r.get(k) for k in fields if k in r}
            row["cong_s_nhan"] = (r.get("cong_s") or {}).get("nhan")
            row["cong_s_diem"] = (r.get("cong_s") or {}).get("diem")
            row["cong_s_ly_do"] = (r.get("cong_s") or {}).get("ly_do")
            row["symbols"] = json.dumps(r.get("symbols") or {}, ensure_ascii=False)
            w.writerow(row)
    print("wrote", out_json, out_csv)


if __name__ == "__main__":
    main()
