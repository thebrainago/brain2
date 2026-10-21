# -*- coding: utf-8 -*-
"""tai_lich_su_mt5.py - MAY NHA (Windows): keo LICH SU GIA cua chinh server XM qua goi MetaTrader5 (21/10/2026, Grok Bot).

Khong dung mat khau: gan vao terminal XM DANG dang nhap (giong do_phi_san.py). Khong goi LLM. Resume: moi (ma, thang) mot tep
data/du_lieu_dai/mt5/<SERVER>/<MA>/M1_<YYYY-MM>.csv.gz (git bo qua); tep da co = bo qua (tru thang hien tai).

  1. Nen M1 (copy_rates_range) tung thang tu --tu (mac dinh 2004-01) -> het; XM chi tra phan server co. Thang rong lien tiep
     o dau lich su -> ghi 'rong' (khong hoi lai). Neu M1 het truoc ma H1 con -> keo them H1 (lich su H1 thuong dai hon).
  2. Mau TICK (copy_ticks_range, 2 ngay giua tuan moi thang) -> spread ask-bid theo gio server x nam: tick_spread.csv.
  3. symbol_info -> symbol_info.json (spread, swap_long/short, swap_mode, ngay x3, hop dong, point...).
Gio: MT5 tra thoi gian SERVER (XM = GMT+2/+3, doi theo DST My) -> khong can doi mui gio.

Chay (may nha, KHI RANH):  mt5tools\\TAI_LICH_SU_MT5.bat   (hoac)
  python mt5tools/tai_lich_su_mt5.py "C:\\Program Files\\XM Global MT5\\terminal64.exe" [--tu 2004-01] [--ma EURUSD,GBPNZD]
  python mt5tools/tai_lich_su_mt5.py "C:\\MT5_slot\\metaquotes\\terminal64.exe" --vai phu   (slot rieng, MetaQuotes-Demo)
Moi server luu rieng data/du_lieu_dai/mt5/<SERVER>/ ; nhan.du_lieu_dai gop: XM uu tien, server khac duoc hieu chinh gio + gia.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
from nhan.tai_du_lieu import MA  # noqa: E402  (19 ma cua 78 he DAT)

RA = GOC / "data" / "du_lieu_dai" / "mt5"
TEN_SAN = {"XAUUSD": ["GOLDmicro", "GOLD", "XAUUSDmicro", "XAUUSD"]}


XM_GIAO_DICH = r"C:\Program Files\XM Global MT5\terminal64.exe"


def kiem_terminal(duong_dan: str, server: str | None, vai: str) -> str | None:
    """vai 'xm' = terminal XM (chi DOC lich su); vai 'phu' = slot RIENG dang nhap MetaQuotes-Demo (hoac server khac XM).
    Tra ly do tu choi, hoac None neu duoc chay. Slot phu KHONG BAO GIO duoc la terminal XM giao dich."""
    p = duong_dan.replace("/", "\\").lower().rstrip("\\")
    if vai == "phu":
        if p == XM_GIAO_DICH.lower() or "xm global" in p:
            return "slot phụ không được là terminal XM giao dịch (%s)" % duong_dan
        if server is not None and "XM" in server.upper():
            return "slot phụ đang đăng nhập server XM (%s) — cần đăng nhập MetaQuotes-Demo" % server
    elif vai == "xm" and server is not None and "XM" not in server.upper():
        return "vai xm nhưng terminal đăng nhập %s" % server
    return None


def ten_tren_san(goc: str, co: set[str]) -> str | None:
    for t in TEN_SAN.get(goc, []) + [goc + "micro", goc + "#", goc]:
        if t in co:
            return t
    return None


def thang(tu: str, den: dt.date) -> list[tuple[int, int]]:
    y, m = map(int, tu.split("-"))
    ra = []
    while (y, m) <= (den.year, den.month):
        ra.append((y, m)); m += 1
        if m > 12:
            y, m = y + 1, 1
    return ra


def _ke(y: int, m: int) -> tuple[dt.datetime, dt.datetime]:
    a = dt.datetime(y, m, 1)
    b = dt.datetime(y + (m == 12), m % 12 + 1, 1)
    return a, b


def ngay_mau(y: int, m: int) -> list[dt.date]:
    d = dt.date(y, m, 8)
    while d.weekday() != 1:
        d += dt.timedelta(days=1)
    return [d, d + dt.timedelta(days=1)]


def keo(mt5, sym: str, goc: str, d: Path, tu: str, log=print) -> dict:
    import pandas as pd
    d.mkdir(parents=True, exist_ok=True)
    hom = dt.date.today()
    tt_f = d / "trang_thai.json"
    tt = json.loads(tt_f.read_text()) if tt_f.exists() else {}
    rong_lien = 0
    for y, m in thang(tu, hom):
        k = "%04d-%02d" % (y, m)
        f = d / ("M1_%s.csv.gz" % k)
        cur = (y, m) == (hom.year, hom.month)
        if (f.exists() and not cur) or tt.get(k) == "rong":
            continue
        a, b = _ke(y, m)
        r = mt5.copy_rates_range(sym, mt5.TIMEFRAME_M1, a, b)
        if r is None or len(r) == 0:
            rong_lien += 1
            if not tt.get("co_du_lieu"):
                tt[k] = "rong"                         # truoc diem bat dau lich su
            log("  %s %s M1: rỗng (%s)" % (goc, k, mt5.last_error()))
        else:
            x = pd.DataFrame(r)
            x["time"] = pd.to_datetime(x["time"], unit="s")
            x[["time", "open", "high", "low", "close", "tick_volume", "spread"]].to_csv(f, index=False, compression="gzip")
            tt["co_du_lieu"] = True; tt[k] = len(x); rong_lien = 0
            log("  %s %s M1: %d nến" % (goc, k, len(x)))
        tt_f.write_text(json.dumps(tt, indent=0))
        time.sleep(0.2)
    # H1 cung server: thuong dai hon M1 -> mot tep
    r = mt5.copy_rates_range(sym, mt5.TIMEFRAME_H1, dt.datetime(int(tu[:4]), 1, 1), dt.datetime.now())
    if r is not None and len(r):
        x = pd.DataFrame(r); x["time"] = pd.to_datetime(x["time"], unit="s")
        x[["time", "open", "high", "low", "close", "tick_volume", "spread"]].to_csv(d / "H1_tat_ca.csv.gz", index=False, compression="gzip")
        tt["h1_tu"], tt["h1_n"] = str(x["time"].iloc[0]), len(x)
    # mau tick -> spread theo gio x nam
    sp_f = d / "tick_spread.csv"
    cu = pd.read_csv(sp_f) if sp_f.exists() else pd.DataFrame(columns=["ngay", "gio", "n", "p50", "p90"])
    xong = set(cu["ngay"].astype(str))
    moi = []
    for y, m in thang(tu, hom):
        for nd in ngay_mau(y, m):
            if str(nd) in xong or nd >= hom:
                continue
            a = dt.datetime(nd.year, nd.month, nd.day)
            t = mt5.copy_ticks_range(sym, a, a + dt.timedelta(days=1), mt5.COPY_TICKS_INFO)
            if t is None or len(t) == 0:
                moi.append({"ngay": str(nd), "gio": -1, "n": 0, "p50": None, "p90": None}); continue
            z = pd.DataFrame(t); z["gio"] = pd.to_datetime(z["time"], unit="s").dt.hour
            z["sp"] = z["ask"] - z["bid"]
            for g, q in z.groupby("gio"):
                moi.append({"ngay": str(nd), "gio": int(g), "n": len(q), "p50": float(q["sp"].median()), "p90": float(q["sp"].quantile(0.9))})
    if moi:
        pd.concat([cu, pd.DataFrame(moi)]).to_csv(sp_f, index=False)
    si = mt5.symbol_info(sym)
    if si is not None:
        info = {k: getattr(si, k) for k in ("name", "digits", "point", "spread", "spread_float", "trade_contract_size", "swap_mode",
                                             "swap_long", "swap_short", "swap_rollover3days", "volume_min", "volume_step",
                                             "currency_profit", "currency_margin") if hasattr(si, k)}
        info["do_luc"] = dt.datetime.now().isoformat(timespec="seconds")
        (d / "symbol_info.json").write_text(json.dumps(info, indent=1, default=str), encoding="utf-8")
    tt_f.write_text(json.dumps(tt, indent=0))
    return tt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("terminal")
    ap.add_argument("--tu", default="2004-01")
    ap.add_argument("--ma", default=",".join(MA))
    ap.add_argument("--vai", choices=["xm", "phu"], default="xm",
                    help="xm = terminal XM; phu = slot rieng dang nhap MetaQuotes-Demo (khong bao gio la terminal XM giao dich)")
    a = ap.parse_args(argv)
    ly = kiem_terminal(a.terminal, None, a.vai)
    if ly:
        print("TỪ CHỐI:", ly); return 2
    import MetaTrader5 as mt5  # chi co tren Windows
    assert mt5.initialize(path=a.terminal, portable=True if a.vai == "phu" else False), mt5.last_error()
    ai = mt5.account_info()
    ly = kiem_terminal(a.terminal, ai.server if ai else None, a.vai)
    if ly:
        mt5.shutdown(); print("TỪ CHỐI:", ly); return 2
    goc_ra = RA / re.sub(r"[^A-Za-z0-9._-]", "_", ai.server)
    co = {s.name for s in mt5.symbols_get()}
    for g in [x.strip().upper() for x in a.ma.split(",") if x.strip()]:
        sym = ten_tren_san(g, co)
        if not sym:
            print("BỎ QUA %s: không có trên server %s" % (g, ai.server)); continue
        mt5.symbol_select(sym, True)
        print("== %s (%s)" % (g, sym), flush=True)
        tt = keo(mt5, sym, g, goc_ra / g, a.tu)
        print("   H1 từ %s (%s nến)" % (tt.get("h1_tu"), tt.get("h1_n")), flush=True)
    mt5.shutdown()
    print("XONG. Chạy tiếp trên máy nhà: python -m nhan.du_lieu_dai --dung  (gộp + kiểm tra), rồi commit thư mục reports/du_lieu_dai/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
